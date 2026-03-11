from django.conf import settings
from django.db import models


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("present", "출석"),
        ("late", "지각"),
        ("absent", "결석"),
        ("leave", "조퇴"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    attendance_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    check_in_at = models.DateTimeField(auto_now_add=True)
    check_out_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "attendance_date")
        indexes = [
            models.Index(fields=["user", "attendance_date"]),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.attendance_date} ({self.status})"


class LocationSetting(models.Model):
    name = models.CharField("위치 이름", max_length=100, default="연구실")
    latitude = models.FloatField("위도")
    longitude = models.FloatField("경도")
    radius = models.FloatField("허용 반경 (미터)", default=50.0)
    is_active = models.BooleanField("활성 여부", default=True)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"
