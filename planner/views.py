import re

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import JobPosting
from .services.job_detail import fetch_job_detail


def index(request):
    return render(request, "planner/index.html")


def build_company_mark(name):
    normalized = re.sub(r"[\(\)\[\]\s]|주식회사|㈜|\(주\)", "", name or "")
    if not normalized:
        return "TL"
    if re.search(r"[A-Za-z]", normalized):
        letters = "".join(ch for ch in normalized if ch.isalpha())
        return (letters[:2] or normalized[:2]).upper()
    return normalized[:2]


def build_job_tags(job):
    raw = job.required_skills or job.job_role or job.summary_text or ""
    tags = []
    for item in re.split(r"[,/]", raw):
        cleaned = re.sub(r"\s+", " ", item).strip()
        if cleaned and cleaned not in tags:
            tags.append(cleaned)
        if len(tags) == 3:
            break

    if not tags and job.location:
        tags.append(job.location)
    if not tags and job.company_name:
        tags.append(job.company_name)

    return [f"#{tag}" for tag in tags[:3]]


def build_deadline_label(job):
    if not job.deadline_at:
        return ""
    today = timezone.localdate()
    deadline = timezone.localtime(job.deadline_at).date()
    delta = (deadline - today).days
    if delta < 0:
        return "마감"
    if delta == 0:
        return "D-Day"
    return f"D-{delta}"


def split_detail_lines(value):
    lines = []
    for raw in (value or "").splitlines():
        cleaned = re.sub(r"\s+", " ", raw).strip(" -•·\t")
        if not cleaned:
            continue
        lines.append(cleaned)
    return lines


def build_main_task_preview(job):
    tasks = split_detail_lines(job.detail_main_tasks)
    if tasks:
        return tasks[:3]
    if job.summary_text:
        return [re.sub(r"\s+", " ", job.summary_text).strip()]
    return []


def jobs_index(request):
    jobs = list(
        JobPosting.objects.filter(is_active=True).order_by(
        "-posted_at", "-updated_at", "-id"
        )[:100]
    )
    jobs.sort(
        key=lambda job: (
            0 if job.source == "wanted" else 1,
            -(job.posted_at.timestamp() if job.posted_at else 0),
            -job.id,
        )
    )
    for job in jobs:
        job.ui_company_mark = build_company_mark(job.company_name)
        job.ui_deadline_label = build_deadline_label(job)
        job.ui_tags = build_job_tags(job)
        job.ui_main_tasks = build_main_task_preview(job)
    return render(request, "jobs/index.html", {"jobs": jobs})


def job_detail_api(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id, is_active=True)
    return JsonResponse(fetch_job_detail(job))
