from django.contrib import admin

from .models import JobMarketSnapshot, JobPosting, JobSyncLog, JuniorRequirementStat


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "title",
        "company_name",
        "location",
        "experience_label",
        "is_junior_friendly",
        "is_active",
    )
    list_filter = ("source", "is_junior_friendly", "is_active")
    search_fields = ("title", "company_name", "location", "required_skills")


@admin.register(JobSyncLog)
class JobSyncLogAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "run_at",
        "fetched_count",
        "created_count",
        "updated_count",
        "status",
    )
    list_filter = ("source", "status")


@admin.register(JuniorRequirementStat)
class JuniorRequirementStatAdmin(admin.ModelAdmin):
    list_display = ("stat_date", "role", "skill", "demand_count", "demand_ratio")
    list_filter = ("stat_date", "role")


@admin.register(JobMarketSnapshot)
class JobMarketSnapshotAdmin(admin.ModelAdmin):
    list_display = ("analysis_key", "sampled_job_count", "total_jobs", "model_name", "analyzed_at")
    readonly_fields = ("created_at", "analyzed_at")
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
