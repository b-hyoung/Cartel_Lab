from django.contrib import admin

from .models import JobPosting, JobSyncLog, JuniorRequirementStat


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

# Register your models here.
