import asyncio
import discord
from discord.ext import commands, tasks
from django.conf import settings
from django.utils import timezone
from datetime import time as dtime, timedelta
from zoneinfo import ZoneInfo
from asgiref.sync import sync_to_async

KST = ZoneInfo("Asia/Seoul")

from attendance.models import AttendanceRecord, AttendanceTimeSetting
from users.models import User
from timetable.models import Timetable


# 명령어 매핑
CHECK_IN_CMDS = {'ㅊㅅ', '출석', 'ㅊㄱ'}
CHECK_OUT_CMDS = {'ㅌㅅ', '퇴실', 'ㅌㄱ'}
ABSENT_CMDS = {'ㄲㅈ', '꺼져', 'ㄱㅈ'}


def _get_time_setting():
    return AttendanceTimeSetting.objects.first()


def _get_user_by_discord_id(discord_id: str):
    """discord_id로 매핑된 User 반환. 없으면 None."""
    try:
        return User.objects.get(discord_id=str(discord_id))
    except User.DoesNotExist:
        return None


def _do_check_in(user):
    """출석 처리. (성공 타입, 에러 메시지) 중 하나 반환."""
    today = timezone.localdate()
    now_time = timezone.localtime().time()
    time_setting = _get_time_setting()

    status = "present"
    if time_setting and now_time > time_setting.check_in_deadline:
        status = "late"

    record, created = AttendanceRecord.objects.get_or_create(
        user=user,
        attendance_date=today,
        defaults={"status": status},
    )

    if not created:
        return None, "이미 출결됐어요 그만해"

    return "check_in", None


def _do_check_out(user):
    """퇴실 처리."""
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    try:
        record = AttendanceRecord.objects.get(user=user, attendance_date=today)
    except AttendanceRecord.DoesNotExist:
        return None, "출석 기록이 없어요. 먼저 ㅊㅅ 해주세요."

    if record.check_out_at:
        return None, "이미 퇴실했어요 그만해"

    time_setting = _get_time_setting()
    if time_setting and now_time < time_setting.check_out_minimum:
        if record.status == "present":
            record.status = "leave"

    if record.status == "leave":
        record.save(update_fields=["status"])
    from attendance.services import finalize_checkout
    finalize_checkout(record, timezone.now())
    return "check_out", None


def _do_absent(user):
    """결석 처리."""
    today = timezone.localdate()

    record, created = AttendanceRecord.objects.get_or_create(
        user=user,
        attendance_date=today,
        defaults={"status": "absent"},
    )

    if not created:
        return None, "이미 처리됐어요 그만해"

    return "absent", None


class AttendanceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        if not settings.DISCORD_CHANNEL_ID:
            raise ValueError("DISCORD_CHANNEL_ID 환경변수가 설정되지 않았습니다.")
        self.attendance_channel_id = int(settings.DISCORD_CHANNEL_ID)

    async def setup_hook(self):
        self.check_in_reminder.start()
        self.check_in_nag.start()
        self.check_out_reminder.start()
        self.b_class_thursday_reminder.start()
        self.b_class_thursday_nag.start()

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != self.attendance_channel_id:
            return

        content = message.content.strip()

        if content in CHECK_IN_CMDS:
            await self._handle_command(message, _do_check_in)
        elif content in CHECK_OUT_CMDS:
            await self._handle_command(message, _do_check_out)
        elif content in ABSENT_CMDS:
            await self._handle_command(message, _do_absent)

    async def _handle_command(self, message, handler):
        user = await sync_to_async(_get_user_by_discord_id)(str(message.author.id))
        if not user:
            return

        success, error_msg = await sync_to_async(handler)(user)
        if error_msg:
            await message.channel.send(f"{message.author.mention} {error_msg}")
        else:
            await message.add_reaction("✅")

    # ── 스케줄러: A반 기본 ──

    @tasks.loop(time=dtime(hour=10, minute=0, second=0, tzinfo=KST))
    async def check_in_reminder(self):
        """10:00 전체 출결 알림"""
        channel = self.get_channel(self.attendance_channel_id)
        if channel:
            await channel.send("@everyone 출결해주세요!", allowed_mentions=discord.AllowedMentions(everyone=True))

    @tasks.loop(time=dtime(hour=10, minute=30, second=0, tzinfo=KST))
    async def check_in_nag(self):
        """10:30 미출결자 리마인드"""
        await self._send_nag_reminder()

    @tasks.loop(time=dtime(hour=20, minute=0, second=0, tzinfo=KST))
    async def check_out_reminder(self):
        """20:00 전체 퇴실 알림"""
        channel = self.get_channel(self.attendance_channel_id)
        if channel:
            await channel.send("@everyone 퇴실해주세요!", allowed_mentions=discord.AllowedMentions(everyone=True))

    # ── 스케줄러: B반 목요일 ──

    @tasks.loop(time=dtime(hour=0, minute=1, second=0, tzinfo=KST))
    async def b_class_thursday_reminder(self):
        """목요일 B반 첫 수업 시간 기준 출결 알림"""
        today = timezone.localdate()
        if today.weekday() != 3:
            return

        first_class = await sync_to_async(
            Timetable.objects.filter(
                class_group="B", weekday=3
            ).order_by("start_time").first
        )()

        if not first_class:
            return

        now = timezone.localtime()
        target = timezone.make_aware(
            timezone.datetime.combine(today, first_class.start_time),
            timezone.get_current_timezone(),
        )
        wait_seconds = (target - now).total_seconds()
        if wait_seconds <= 0:
            return
        await asyncio.sleep(wait_seconds)

        channel = self.get_channel(self.attendance_channel_id)
        if channel:
            b_users = await sync_to_async(
                lambda: list(User.objects.filter(class_group="B", discord_id__gt=""))
            )()
            mentions = " ".join(f"<@{u.discord_id}>" for u in b_users)
            if mentions:
                await channel.send(f"{mentions} B반 출결해주세요!")

    @tasks.loop(time=dtime(hour=0, minute=2, second=0, tzinfo=KST))
    async def b_class_thursday_nag(self):
        """목요일 B반 첫 수업 30분 후 미출결자 리마인드"""
        today = timezone.localdate()
        if today.weekday() != 3:
            return

        first_class = await sync_to_async(
            Timetable.objects.filter(
                class_group="B", weekday=3
            ).order_by("start_time").first
        )()

        if not first_class:
            return

        now = timezone.localtime()
        nag_time = timezone.make_aware(
            timezone.datetime.combine(today, first_class.start_time),
            timezone.get_current_timezone(),
        ) + timedelta(minutes=30)

        wait_seconds = (nag_time - now).total_seconds()
        if wait_seconds <= 0:
            return
        await asyncio.sleep(wait_seconds)

        await self._send_nag_reminder(class_group="B")

    # ── 공통 리마인드 ──

    async def _send_nag_reminder(self, class_group=None):
        """미출결자(웹/앱/디스코드 모두 포함)에게 리마인드 멘션."""
        today = timezone.localdate()
        channel = self.get_channel(self.attendance_channel_id)
        if not channel:
            return

        def _get_missing_users():
            qs = User.objects.filter(discord_id__gt="")
            if class_group:
                qs = qs.filter(class_group=class_group)

            checked_user_ids = set(
                AttendanceRecord.objects.filter(
                    attendance_date=today
                ).values_list("user_id", flat=True)
            )

            return list(qs.exclude(id__in=checked_user_ids))

        missing = await sync_to_async(_get_missing_users)()

        if not missing:
            return

        mentions = " ".join(f"<@{u.discord_id}>" for u in missing)
        await channel.send(f"{mentions} 아직 출결 안 했어요!")

    # ── loop before_loop: 봇 준비 대기 ──

    @check_in_reminder.before_loop
    async def before_check_in_reminder(self):
        await self.wait_until_ready()

    @check_in_nag.before_loop
    async def before_check_in_nag(self):
        await self.wait_until_ready()

    @check_out_reminder.before_loop
    async def before_check_out_reminder(self):
        await self.wait_until_ready()

    @b_class_thursday_reminder.before_loop
    async def before_b_class_thursday_reminder(self):
        await self.wait_until_ready()

    @b_class_thursday_nag.before_loop
    async def before_b_class_thursday_nag(self):
        await self.wait_until_ready()
