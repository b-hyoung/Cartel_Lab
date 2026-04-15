import pytest
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
from django.utils import timezone
from attendance.models import AttendanceRecord
from attendance.services import finalize_checkout
from farm.tests.factories import make_user, make_farm


@pytest.fixture
def setup(db):
    user = make_user()
    farm = make_farm(user)
    return user, farm


@pytest.mark.django_db
def test_finalize_checkout_grants_reward(setup):
    user, farm = setup
    rec = AttendanceRecord.objects.create(user=user)
    when = timezone.now() + timedelta(hours=4)
    finalize_checkout(rec, when)
    rec.refresh_from_db()
    farm.refresh_from_db()
    assert rec.check_out_at == when
    assert rec.reward_granted is True
    assert farm.total_exp > 0


@pytest.mark.django_db
def test_finalize_checkout_skip_reward(setup):
    user, farm = setup
    rec = AttendanceRecord.objects.create(user=user)
    when = timezone.now() + timedelta(hours=4)
    finalize_checkout(rec, when, skip_reward=True)
    rec.refresh_from_db()
    farm.refresh_from_db()
    assert rec.check_out_at == when
    assert rec.reward_granted is False
    assert farm.total_exp == 0


@pytest.mark.django_db
def test_finalize_checkout_idempotent(setup):
    user, farm = setup
    rec = AttendanceRecord.objects.create(user=user)
    when = timezone.now() + timedelta(hours=4)
    finalize_checkout(rec, when)
    finalize_checkout(rec, when)
    farm.refresh_from_db()
    assert AttendanceRecord.objects.get(pk=rec.pk).reward_granted is True
    # 중복 적립 없음 — 4시간 체류 1회분 EXP만
    assert farm.total_exp == 18
