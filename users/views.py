import re

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, ProfileUpdateForm, SignupForm
from .services import build_profile_analysis


def format_github_summary_text(summary):
    cleaned = (summary or "").strip()
    if not cleaned:
        return ""

    parts = [part.strip() for part in cleaned.split(" / ") if part.strip()]
    if not parts:
        return cleaned

    formatted = []
    for part in parts:
        if part.startswith("공개 저장소 "):
            formatted.append(part.replace("공개 저장소 ", "공개 저장소는 ") + "입니다.")
        elif part.startswith("주요 언어 "):
            formatted.append(part.replace("주요 언어 ", "주요 사용 언어는 ") + "입니다.")
        elif part.startswith("최근 프로젝트 키워드 "):
            formatted.append(part.replace("최근 프로젝트 키워드 ", "최근 저장소 설명에서 확인된 핵심 주제는 ") + "입니다.")
        else:
            if not part.endswith(("다.", "니다.", ".")):
                part = part + "."
            formatted.append(part)
    return " ".join(formatted)


def format_ai_profile_summary_text(summary, user_name):
    cleaned = (summary or "").strip()
    if not cleaned:
        return ""

    cleaned = re.sub(rf"^{re.escape(user_name)}\s*님은\s*", "이 프로필은 ", cleaned)
    cleaned = re.sub(r"^\S+\s*님은\s*", "이 프로필은 ", cleaned)
    return cleaned


def reset_profile_analysis(user):
    user.github_username = ""
    user.github_profile_summary = ""
    user.github_top_languages = ""
    user.github_connected_at = None
    user.resume_extracted_text = ""
    user.resume_analysis_summary = ""
    user.analysis_recommendation = ""
    user.ai_profile_summary = ""
    user.ai_profile_payload = {}
    user.ai_profile_error = ""
    user.profile_analyzed_at = None


@login_required
def index(request):
    user = request.user
    has_profile_sources = bool(user.github_url or user.resume_file)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            action = request.POST.get("action", "save")
            user = form.save(commit=False)
            source_fields = {"github_url", "resume_file"}
            if source_fields.intersection(set(form.changed_data)):
                reset_profile_analysis(user)
            user.save()

            if action == "analyze":
                if not user.can_run_profile_analysis():
                    messages.error(request, "오늘은 분석을 3번 모두 사용했습니다. 내일 다시 시도해 주세요.")
                    return redirect("users-index")
                try:
                    analysis = build_profile_analysis(user.github_url, user.resume_file)
                    user.github_username = analysis["github_username"]
                    user.github_profile_summary = analysis["github_profile_summary"]
                    user.github_top_languages = analysis["github_top_languages"]
                    user.resume_extracted_text = analysis["resume_extracted_text"]
                    user.resume_analysis_summary = analysis["resume_analysis_summary"]
                    user.analysis_recommendation = analysis["analysis_recommendation"]
                    user.ai_profile_summary = analysis.get("ai_profile_summary", "")
                    user.ai_profile_payload = analysis.get("ai_profile_payload", {})
                    user.ai_profile_error = analysis.get("ai_profile_error", "")
                    if user.github_url:
                        user.mark_github_connected()
                    user.mark_profile_analyzed()
                    user.consume_profile_analysis()
                    user.save()
                    messages.success(request, "분석 결과를 적용했습니다.")
                    return redirect("users-index")
                except Exception as exc:
                    messages.error(request, f"분석 중 오류가 발생했습니다: {exc}")
            else:
                messages.success(request, "프로필 정보를 저장했습니다.")
                return redirect("users-index")
        else:
            messages.error(request, "입력값을 다시 확인해 주세요.")
    else:
        form = ProfileUpdateForm(instance=user)

    edit_mode = request.method == "POST" or request.GET.get("edit") == "1" or not has_profile_sources
    context = {
        "form": form,
        "edit_mode": edit_mode,
        "has_profile_sources": has_profile_sources,
        "formatted_github_summary": format_github_summary_text(user.github_profile_summary),
        "formatted_ai_profile_summary": format_ai_profile_summary_text(user.ai_profile_summary, user.name),
        "resume_points": [line for line in user.resume_analysis_summary.split(" / ") if line],
        "ai_target_roles": user.ai_profile_payload.get("target_roles", []) if user.ai_profile_payload else [],
        "ai_core_skills": user.ai_profile_payload.get("core_skills", []) if user.ai_profile_payload else [],
        "ai_project_evidence": user.ai_profile_payload.get("project_evidence", []) if user.ai_profile_payload else [],
        "ai_strengths": user.ai_profile_payload.get("strengths", []) if user.ai_profile_payload else [],
        "ai_gaps": user.ai_profile_payload.get("gaps", []) if user.ai_profile_payload else [],
        "ai_study_priorities": user.ai_profile_payload.get("study_priorities", []) if user.ai_profile_payload else [],
        "daily_analysis_limit": 3,
        "daily_analysis_count": user.get_today_analysis_count(),
        "remaining_analysis_count": user.get_remaining_analysis_count(),
    }
    return render(request, "users/index.html", context)

def signup(request):
    if request.user.is_authenticated:
        return redirect("users-index")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect("users-index")
    else:
        form = SignupForm()

    return render(request, "users/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("users-index")

    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "로그인되었습니다.")
            return redirect("users-index")
    else:
        form = LoginForm(request)

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "로그아웃되었습니다.")
    return redirect("home")
