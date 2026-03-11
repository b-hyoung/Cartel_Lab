from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from django.conf import settings

from .ai_services import generate_ai_profile, is_openai_configured


GITHUB_API_BASE = "https://api.github.com"
PROFILE_SKILL_KEYWORDS = (
    "python",
    "django",
    "fastapi",
    "flask",
    "java",
    "spring",
    "kotlin",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "vue",
    "node",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "html",
    "css",
)


def extract_github_username(value: str) -> str:
    cleaned = (value or "").strip().rstrip("/")
    if not cleaned:
        return ""
    if "github.com" not in cleaned:
        return cleaned.lstrip("@")
    parsed = urlparse(cleaned)
    parts = [part for part in parsed.path.split("/") if part]
    return parts[0] if parts else ""


def fetch_github_analysis(github_url: str) -> dict[str, Any]:
    username = extract_github_username(github_url)
    if not username:
        return {
            "username": "",
            "summary": "",
            "top_languages": [],
        }

    headers = {"Accept": "application/vnd.github+json"}
    token = getattr(settings, "GITHUB_API_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    user_response = requests.get(
        f"{GITHUB_API_BASE}/users/{username}",
        headers=headers,
        timeout=15,
    )
    user_response.raise_for_status()
    user_payload = user_response.json()

    repo_response = requests.get(
        f"{GITHUB_API_BASE}/users/{username}/repos",
        headers=headers,
        params={"sort": "updated", "per_page": 100},
        timeout=15,
    )
    repo_response.raise_for_status()
    repos = repo_response.json()

    language_counter = Counter()
    repo_descriptions = []
    for repo in repos:
        language = (repo.get("language") or "").strip()
        if language:
            language_counter.update([language])
        description = (repo.get("description") or "").strip()
        if description:
            repo_descriptions.append(description)

    top_languages = [name for name, _ in language_counter.most_common(5)]
    summary_parts = []
    if user_payload.get("public_repos") is not None:
        summary_parts.append(f"공개 저장소는 {user_payload['public_repos']}개입니다.")
    if top_languages:
        summary_parts.append(f"주요 사용 언어는 {', '.join(top_languages[:3])}입니다.")
    if repo_descriptions:
        summary_parts.append(f"최근 저장소 설명에서 확인된 핵심 주제는 {repo_descriptions[0][:80]}입니다.")

    return {
        "username": username,
        "summary": " ".join(summary_parts),
        "top_languages": top_languages,
    }


def extract_resume_text(file_field) -> str:
    if not file_field:
        return ""

    suffix = Path(file_field.name).suffix.lower()
    file_field.open("rb")
    try:
        if suffix == ".txt":
            return file_field.read().decode("utf-8", errors="ignore").strip()

        if suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(file_field)
            return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

        return ""
    finally:
        file_field.close()


def analyze_resume_text(text: str) -> dict[str, Any]:
    normalized = (text or "").strip()
    if not normalized:
        return {
            "summary": "",
            "skills": [],
            "recommendation": "",
        }

    lowered = normalized.lower()
    found_skills = [keyword for keyword in PROFILE_SKILL_KEYWORDS if keyword in lowered]
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    summary = " / ".join(lines[:3])[:320]

    recommendations = []
    if "aws" not in found_skills and "docker" not in found_skills:
        recommendations.append("배포 경험이 부족합니다. Django 또는 Spring 기반 프로젝트를 AWS EC2나 Docker로 배포하고, README에 배포 구조와 실행 방법을 정리한 예시를 추가하십시오.")
    if "sql" not in found_skills and "mysql" not in found_skills:
        recommendations.append("데이터베이스 활용 근거가 약합니다. MySQL 또는 PostgreSQL로 게시판, 예약, 일정 관리와 같은 CRUD 프로젝트를 만들고 테이블 설계 이유와 주요 SQL 예시를 함께 정리하십시오.")
    if "git" not in found_skills:
        recommendations.append("협업 경험이 약하게 보입니다. Git 브랜치 전략, Pull Request, 코드 리뷰 기록이 남는 팀 프로젝트를 진행하고 협업 과정과 역할 분담을 포트폴리오에 명시하십시오.")
    if not recommendations:
        recommendations.append("프로젝트 설명을 더 구체화할 필요가 있습니다. 기능 구현 목록만 적지 말고, 예를 들어 응답 속도 개선, 비용 절감, 사용자 수 변화처럼 수치가 드러나는 성과를 함께 작성하십시오.")

    return {
        "summary": summary,
        "skills": found_skills[:10],
        "recommendation": " ".join(recommendations),
    }


def build_profile_analysis(github_url: str, resume_file) -> dict[str, Any]:
    github_analysis = fetch_github_analysis(github_url) if github_url else {
        "username": "",
        "summary": "",
        "top_languages": [],
    }
    resume_text = extract_resume_text(resume_file) if resume_file else ""
    resume_analysis = analyze_resume_text(resume_text)

    stored_payload = {
        "github_username": github_analysis["username"],
        "github_profile_summary": github_analysis["summary"],
        "github_top_languages": ", ".join(github_analysis["top_languages"]),
        "resume_extracted_text": resume_text,
        "resume_analysis_summary": resume_analysis["summary"],
        "analysis_recommendation": resume_analysis["recommendation"],
        "ai_profile_summary": "",
        "ai_profile_payload": {},
        "ai_profile_error": "",
    }

    if is_openai_configured() and (resume_text or github_analysis["summary"]):
        try:
            ai_profile = generate_ai_profile(
                github_summary=github_analysis["summary"],
                github_languages=", ".join(github_analysis["top_languages"]),
                resume_summary=resume_analysis["summary"],
                resume_text=resume_text,
            )
            stored_payload["ai_profile_summary"] = ai_profile.get("summary", "")
            stored_payload["ai_profile_payload"] = ai_profile
        except Exception as exc:
            stored_payload["ai_profile_error"] = str(exc)

    return stored_payload
