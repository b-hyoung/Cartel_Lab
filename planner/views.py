import calendar
import secrets
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .google_calendar import (
    GoogleCalendarError,
    build_authorization_url,
    create_todo_event,
    delete_event,
    exchange_code_for_token,
    fetch_google_email,
    is_configured,
    list_events,
    token_expiry_from_seconds,
)
from .models import DailyTodo, GoogleCalendarCredential, LabWideGoal, WeeklyGoal


def _week_start_from_input(raw_date):
    """Return week start (Sunday) from an iso date string."""
    if raw_date:
        try:
            target_date = date.fromisoformat(raw_date)
        except ValueError:
            target_date = timezone.localdate()
    else:
        target_date = timezone.localdate()

    # Python weekday: Monday=0 ... Sunday=6
    days_from_sunday = (target_date.weekday() + 1) % 7
    return target_date - timedelta(days=days_from_sunday)


def _goal_date(goal):
    return goal.week_start + timedelta(days=goal.weekday)


def _time_from_input(raw_time):
    if not raw_time:
        return None
    try:
        return timezone.datetime.strptime(raw_time, "%H:%M").time()
    except ValueError:
        return None


def _planner_plan_redirect_for_date(target_date):
    month = target_date.strftime("%Y-%m")
    return redirect(
        f"{reverse('planner-index')}?view=plan&month={month}&date={target_date.isoformat()}"
    )


def _sync_daily_todo_create(todo):
    credential = getattr(todo.user, "google_calendar_credential", None)
    if not credential:
        return None

    event_id = create_todo_event(credential, todo)
    if not event_id:
        raise GoogleCalendarError("구글 캘린더에서 이벤트 ID를 받지 못했습니다.")

    todo.google_event_id = event_id
    todo.save(update_fields=["google_event_id", "updated_at"])
    return event_id


def _parse_google_datetime(raw_value):
    if not raw_value:
        return None

    normalized = raw_value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return timezone.localtime(parsed)


def _todo_fields_from_google_event(event):
    summary = (event.get("summary") or "").strip()
    start = event.get("start") or {}

    if start.get("dateTime"):
        start_dt = _parse_google_datetime(start["dateTime"])
        if not start_dt:
            return None, None, summary
        return start_dt.date(), start_dt.time().replace(second=0, microsecond=0), summary

    if start.get("date"):
        try:
            return date.fromisoformat(start["date"]), None, summary
        except ValueError:
            return None, None, summary

    return None, None, summary


def _sync_google_events_for_range(user, start_date, end_date):
    credential = getattr(user, "google_calendar_credential", None)
    if not credential:
        return {"created": 0, "updated": 0, "deleted": 0}

    tz = timezone.get_current_timezone()
    range_start = timezone.make_aware(datetime.combine(start_date, time.min), tz)
    range_end = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), time.min), tz)
    events = list_events(credential, range_start, range_end)

    created = 0
    updated = 0
    deleted = 0

    for event in events:
        google_event_id = event.get("id", "")
        if not google_event_id:
            continue

        todo_qs = DailyTodo.objects.filter(user=user, google_event_id=google_event_id)
        status = event.get("status", "")
        if status == "cancelled":
            deleted += todo_qs.count()
            todo_qs.delete()
            continue

        target_date, planned_time, content = _todo_fields_from_google_event(event)
        if not target_date or not content:
            continue

        todo = todo_qs.first()
        if todo:
            changed = False
            if todo.target_date != target_date:
                todo.target_date = target_date
                changed = True
            if todo.planned_time != planned_time:
                todo.planned_time = planned_time
                changed = True
            if todo.content != content:
                todo.content = content
                changed = True
            if changed:
                todo.save(update_fields=["target_date", "planned_time", "content", "updated_at"])
                updated += 1
            continue

        DailyTodo.objects.create(
            user=user,
            target_date=target_date,
            planned_time=planned_time,
            content=content,
            google_event_id=google_event_id,
        )
        created += 1

    return {"created": created, "updated": updated, "deleted": deleted}


def index(request):
    planner_view = request.GET.get("view", "goal")
    if planner_view not in {"goal", "plan"}:
        planner_view = "goal"

    today = timezone.localdate()
    month_raw = request.GET.get("month")
    try:
        current_month = date.fromisoformat(f"{month_raw}-01") if month_raw else today.replace(day=1)
    except ValueError:
        current_month = today.replace(day=1)

    selected_date_raw = request.GET.get("date")
    try:
        selected_date = date.fromisoformat(selected_date_raw) if selected_date_raw else today
    except ValueError:
        selected_date = today

    if selected_date.month != current_month.month or selected_date.year != current_month.year:
        selected_date = current_month

    first_weekday, _ = calendar.monthrange(current_month.year, current_month.month)
    # monthrange: Monday=0 ... Sunday=6
    leading_days = (first_weekday + 1) % 7
    calendar_start = current_month - timedelta(days=leading_days)
    calendar_end = calendar_start + timedelta(days=41)

    if (
        request.user.is_authenticated
        and planner_view == "plan"
        and hasattr(request.user, "google_calendar_credential")
    ):
        try:
            _sync_google_events_for_range(request.user, calendar_start, calendar_end)
        except GoogleCalendarError as exc:
            messages.warning(request, f"구글 캘린더 자동 동기화에 실패했습니다: {exc}")

    if request.user.is_authenticated:
        goals = WeeklyGoal.objects.filter(
            user=request.user,
            week_start__gte=calendar_start - timedelta(days=6),
            week_start__lte=calendar_end,
        ).order_by("week_start", "weekday", "created_at")
    else:
        goals = WeeklyGoal.objects.none()

    goals_by_date = {}
    for goal in goals:
        goal_date = _goal_date(goal)
        if calendar_start <= goal_date <= calendar_end:
            goals_by_date.setdefault(goal_date, []).append(goal)

    weeks = []
    cursor = calendar_start
    for _ in range(6):
        week_days = []
        for _ in range(7):
            day_goals = goals_by_date.get(cursor, [])
            week_days.append(
                {
                    "date": cursor,
                    "is_current_month": cursor.month == current_month.month,
                    "is_selected": cursor == selected_date,
                    "is_today": cursor == today,
                    "preview_goals": day_goals[:2],
                    "more_count": max(len(day_goals) - 2, 0),
                }
            )
            cursor += timedelta(days=1)
        weeks.append(week_days)

    selected_goals = goals_by_date.get(selected_date, [])
    prev_month = (current_month.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)

    context = {
        "planner_view": planner_view,
        "current_month": current_month,
        "selected_date": selected_date,
        "prev_month": prev_month,
        "next_month": next_month,
        "weeks": weeks,
        "selected_goals": selected_goals,
        "lab_wide_goals": LabWideGoal.objects.select_related("created_by")[:8],
        "daily_todos": (
            DailyTodo.objects.filter(user=request.user, target_date=selected_date)
            if request.user.is_authenticated
            else DailyTodo.objects.none()
        ),
        "google_calendar_enabled": is_configured(),
        "google_calendar_connected": (
            request.user.is_authenticated
            and hasattr(request.user, "google_calendar_credential")
        ),
        "google_calendar_email": (
            request.user.google_calendar_credential.google_email
            if request.user.is_authenticated
            and hasattr(request.user, "google_calendar_credential")
            else ""
        ),
    }
    return render(request, "planner/index.html", context)


@login_required
def add_goal(request):
    if request.method != "POST":
        return redirect("planner-index")

    week_start = _week_start_from_input(request.POST.get("week_start"))
    weekday_raw = request.POST.get("weekday", "")
    content = request.POST.get("content", "").strip()
    target_date_raw = request.POST.get("target_date")
    planned_time = _time_from_input(request.POST.get("planned_time"))

    if target_date_raw:
        try:
            target_date = date.fromisoformat(target_date_raw)
            week_start = _week_start_from_input(target_date.isoformat())
            weekday_raw = str((target_date - week_start).days)
        except ValueError:
            pass

    if weekday_raw.isdigit() and content:
        weekday = int(weekday_raw)
        if 0 <= weekday <= 6:
            WeeklyGoal.objects.create(
                user=request.user,
                week_start=week_start,
                weekday=weekday,
                planned_time=planned_time,
                content=content,
            )

    target_date = request.POST.get("target_date")
    if target_date:
        try:
            selected_date = date.fromisoformat(target_date)
            month_key = selected_date.strftime("%Y-%m")
            return redirect(
                f"{reverse('planner-index')}?view=plan&month={month_key}&date={selected_date.isoformat()}"
            )
        except ValueError:
            pass
    return redirect(f"{reverse('planner-index')}?view=plan")


@login_required
def toggle_goal(request, goal_id):
    if request.method != "POST":
        return redirect("planner-index")

    goal = get_object_or_404(WeeklyGoal, id=goal_id, user=request.user)
    goal.is_completed = not goal.is_completed
    goal.save(update_fields=["is_completed", "updated_at"])

    goal_date = _goal_date(goal)
    month_key = goal_date.strftime("%Y-%m")
    return redirect(
        f"{reverse('planner-index')}?view=plan&month={month_key}&date={goal_date.isoformat()}"
    )


@login_required
def update_goal(request, goal_id):
    if request.method != "POST":
        return redirect("planner-index")

    goal = get_object_or_404(WeeklyGoal, id=goal_id, user=request.user)
    content = request.POST.get("content", "").strip()
    planned_time = _time_from_input(request.POST.get("planned_time"))
    if content:
        goal.content = content
        goal.planned_time = planned_time
        goal.save(update_fields=["content", "planned_time", "updated_at"])

    goal_date = _goal_date(goal)
    month_key = goal_date.strftime("%Y-%m")
    return redirect(
        f"{reverse('planner-index')}?view=plan&month={month_key}&date={goal_date.isoformat()}"
    )


@login_required
def add_lab_goal(request):
    if request.method != "POST":
        return redirect("planner-index")

    content = request.POST.get("content", "").strip()
    if content:
        LabWideGoal.objects.create(created_by=request.user, content=content)
    return redirect(f"{reverse('planner-index')}?view=goal")


@login_required
def add_daily_todo(request):
    if request.method != "POST":
        return redirect("planner-index")

    content = request.POST.get("content", "").strip()
    planned_time = _time_from_input(request.POST.get("planned_time"))
    target_date_raw = request.POST.get("target_date")
    month_raw = request.POST.get("month")
    target_date = timezone.localdate()
    try:
        if target_date_raw:
            target_date = date.fromisoformat(target_date_raw)
    except ValueError:
        pass

    if content:
        todo = DailyTodo.objects.create(
            user=request.user,
            target_date=target_date,
            planned_time=planned_time,
            content=content,
        )
        if hasattr(request.user, "google_calendar_credential"):
            try:
                _sync_daily_todo_create(todo)
            except GoogleCalendarError as exc:
                messages.warning(request, f"투두는 저장됐지만 구글 캘린더 동기화에 실패했습니다: {exc}")

    month = month_raw or target_date.strftime("%Y-%m")
    return redirect(
        f"{reverse('planner-index')}?view=plan&month={month}&date={target_date.isoformat()}"
    )


@login_required
def toggle_daily_todo(request, todo_id):
    if request.method != "POST":
        return redirect("planner-index")

    todo = get_object_or_404(DailyTodo, id=todo_id, user=request.user)
    todo.is_completed = not todo.is_completed
    todo.save(update_fields=["is_completed", "updated_at"])

    month = todo.target_date.strftime("%Y-%m")
    return redirect(
        f"{reverse('planner-index')}?view=plan&month={month}&date={todo.target_date.isoformat()}"
    )


@login_required
def delete_daily_todo(request, todo_id):
    if request.method != "POST":
        return redirect("planner-index")

    todo = get_object_or_404(DailyTodo, id=todo_id, user=request.user)
    target_date = todo.target_date

    credential = getattr(request.user, "google_calendar_credential", None)
    if credential and todo.google_event_id:
        try:
            delete_event(credential, todo.google_event_id)
        except GoogleCalendarError as exc:
            messages.warning(request, f"구글 캘린더 일정 삭제에 실패했습니다: {exc}")

    todo.delete()
    return _planner_plan_redirect_for_date(target_date)


@login_required
def google_calendar_import(request):
    if request.method != "POST":
        return redirect("planner-index")

    if not hasattr(request.user, "google_calendar_credential"):
        messages.error(request, "Google Calendar 연결 후 가져오기를 사용할 수 있습니다.")
        return _planner_plan_redirect_for_date(timezone.localdate())

    target_raw = request.POST.get("target_date", "")
    month_raw = request.POST.get("month", "")
    try:
        target_date = date.fromisoformat(target_raw) if target_raw else timezone.localdate()
    except ValueError:
        target_date = timezone.localdate()

    if request.POST.get("scope") == "month":
        try:
            month_date = date.fromisoformat(f"{month_raw}-01") if month_raw else target_date.replace(day=1)
        except ValueError:
            month_date = target_date.replace(day=1)
        _, month_days = calendar.monthrange(month_date.year, month_date.month)
        range_start = month_date
        range_end = month_date.replace(day=month_days)
    else:
        range_start = target_date
        range_end = target_date

    try:
        result = _sync_google_events_for_range(request.user, range_start, range_end)
        messages.success(
            request,
            f"구글 일정 가져오기 완료: 생성 {result['created']}건, 업데이트 {result['updated']}건, 삭제 {result['deleted']}건",
        )
    except GoogleCalendarError as exc:
        messages.error(request, f"구글 일정 가져오기에 실패했습니다: {exc}")

    return _planner_plan_redirect_for_date(target_date)


@login_required
def google_calendar_connect(request):
    if not is_configured():
        messages.error(request, "Google Calendar 설정이 비어 있습니다. .env 값을 먼저 입력하세요.")
        return redirect("planner-index")

    state = secrets.token_urlsafe(24)
    request.session["google_oauth_state"] = state
    return redirect(build_authorization_url(request, state))


@login_required
def google_calendar_callback(request):
    if not is_configured():
        messages.error(request, "Google Calendar 설정이 비어 있습니다.")
        return redirect("planner-index")

    expected_state = request.session.pop("google_oauth_state", "")
    received_state = request.GET.get("state", "")
    if not expected_state or expected_state != received_state:
        messages.error(request, "구글 로그인 검증(state)에 실패했습니다. 다시 시도하세요.")
        return redirect("planner-index")

    oauth_error = request.GET.get("error")
    if oauth_error:
        messages.error(request, f"구글 연결이 취소되었거나 실패했습니다: {oauth_error}")
        return redirect("planner-index")

    code = request.GET.get("code", "")
    if not code:
        messages.error(request, "구글 인증 코드가 없어 연결할 수 없습니다.")
        return redirect("planner-index")

    try:
        token_data = exchange_code_for_token(request, code)
        google_email = fetch_google_email(token_data["access_token"])
    except GoogleCalendarError as exc:
        messages.error(request, f"구글 계정 연결에 실패했습니다: {exc}")
        return redirect("planner-index")

    credential, created = GoogleCalendarCredential.objects.get_or_create(
        user=request.user,
        defaults={
            "google_email": google_email,
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "token_expires_at": token_expiry_from_seconds(token_data.get("expires_in")),
            "scope": token_data.get("scope", ""),
        },
    )

    if not created:
        credential.google_email = google_email
        credential.access_token = token_data["access_token"]
        if token_data.get("refresh_token"):
            credential.refresh_token = token_data["refresh_token"]
        credential.token_expires_at = token_expiry_from_seconds(token_data.get("expires_in"))
        credential.scope = token_data.get("scope", credential.scope)
        credential.save(
            update_fields=[
                "google_email",
                "access_token",
                "refresh_token",
                "token_expires_at",
                "scope",
                "updated_at",
            ]
        )

    today = timezone.localdate()
    month_start = today.replace(day=1)
    _, month_days = calendar.monthrange(today.year, today.month)
    month_end = today.replace(day=month_days)
    try:
        _sync_google_events_for_range(request.user, month_start, month_end)
    except GoogleCalendarError:
        pass

    messages.success(request, "Google Calendar 연결이 완료되었습니다.")
    return _planner_plan_redirect_for_date(today)


@login_required
def google_calendar_disconnect(request):
    if request.method != "POST":
        return redirect("planner-index")

    GoogleCalendarCredential.objects.filter(user=request.user).delete()
    messages.success(request, "Google Calendar 연결을 해제했습니다.")
    return _planner_plan_redirect_for_date(timezone.localdate())
