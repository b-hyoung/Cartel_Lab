from django.contrib import admin

from .models import DailyTodo, LabWideGoal, WeeklyGoal


@admin.register(WeeklyGoal)
class WeeklyGoalAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "week_start", "weekday", "content", "is_completed")
    list_filter = ("week_start", "weekday", "is_completed")
    search_fields = ("user__student_id", "user__name", "content")


@admin.register(LabWideGoal)
class LabWideGoalAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "content", "created_at")
    search_fields = ("created_by__student_id", "created_by__name", "content")


@admin.register(DailyTodo)
class DailyTodoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "target_date", "planned_time", "content", "is_completed")
    list_filter = ("target_date", "is_completed")
    search_fields = ("user__student_id", "user__name", "content")
