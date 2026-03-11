from __future__ import annotations

import json
from typing import Any

import requests
from django.conf import settings


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def is_openai_configured() -> bool:
    return bool(getattr(settings, "OPENAI_API_KEY", ""))


def _extract_response_text(payload: dict[str, Any]) -> str:
    if payload.get("output_text"):
        return payload["output_text"]

    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"]
    return ""


def call_openai_json_schema(
    *,
    model: str,
    schema_name: str,
    schema: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    response = requests.post(
        OPENAI_RESPONSES_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_prompt}],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema,
                    "strict": True,
                }
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    raw_text = _extract_response_text(payload)
    if not raw_text:
        raise RuntimeError("OpenAI 응답에서 구조화된 결과를 읽지 못했습니다.")
    return json.loads(raw_text)


def build_profile_prompt(*, github_summary: str, github_languages: str, resume_summary: str, resume_text: str) -> str:
    trimmed_resume = (resume_text or "")[:5000]
    return (
        "학생 프로필을 구조화된 JSON으로 정리하십시오.\n"
        "반드시 입력 텍스트에 근거한 내용만 사용하고, 과장하거나 존재하지 않는 경험을 만들지 마십시오.\n"
        "요약(summary)은 구어체를 사용하지 않는 문어체 한국어로 2~4문장 이내로 작성하십시오.\n"
        "존칭 표현이나 '님은' 같은 표현은 사용하지 말고, 이력서나 GitHub에 직접 드러난 사실만 정리하십시오.\n\n"
        f"[GitHub 요약]\n{github_summary or '없음'}\n\n"
        f"[GitHub 주요 언어]\n{github_languages or '없음'}\n\n"
        f"[이력서 요약]\n{resume_summary or '없음'}\n\n"
        f"[이력서 원문 일부]\n{trimmed_resume or '없음'}"
    )


def generate_ai_profile(*, github_summary: str, github_languages: str, resume_summary: str, resume_text: str) -> dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "target_roles": {"type": "array", "items": {"type": "string"}},
            "core_skills": {"type": "array", "items": {"type": "string"}},
            "project_evidence": {"type": "array", "items": {"type": "string"}},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "gaps": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "부족한 점과 함께, 어떤 프로젝트나 결과물로 보완하면 좋은지 예시를 포함한 문장",
                },
            },
            "study_priorities": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "무엇을 어떤 방식으로 공부하고, 어떤 산출물로 남기면 되는지 예시를 포함한 실행 문장",
                },
            },
        },
        "required": [
            "summary",
            "target_roles",
            "core_skills",
            "project_evidence",
            "strengths",
            "gaps",
            "study_priorities",
        ],
        "additionalProperties": False,
    }
    return call_openai_json_schema(
        model=getattr(settings, "OPENAI_PROFILE_MODEL", "gpt-4.1-mini"),
        schema_name="student_profile_analysis",
        schema=schema,
        system_prompt=(
            "너는 채용 공고 추천 시스템의 프로필 정규화 분석기다. "
            "학생의 이력서와 GitHub 정보를 읽고, 추천에 재사용할 수 있는 구조화 프로필을 만든다. "
            "모든 서술은 문어체 한국어로 작성하고, 구어체, 대화체, 과도한 수식, 인칭 호칭을 사용하지 않는다. "
            "gaps와 study_priorities는 반드시 실행 예시를 포함해야 하며, "
            "'무엇이 부족하다'에서 끝내지 말고 '어떤 기술로 어떤 프로젝트를 만들어 어떤 식으로 정리할지'까지 제시한다."
        ),
        user_prompt=build_profile_prompt(
            github_summary=github_summary,
            github_languages=github_languages,
            resume_summary=resume_summary,
            resume_text=resume_text,
        ),
    )


def build_job_prompt(*, ai_profile: dict[str, Any], job_payload: dict[str, Any]) -> str:
    return (
        "학생 프로필과 공고를 비교해 추천 여부를 JSON으로 판단해 주세요.\n"
        "반드시 입력에 있는 근거만 사용하고, 점수는 0~100 정수로 주세요.\n\n"
        f"[학생 프로필]\n{json.dumps(ai_profile, ensure_ascii=False)}\n\n"
        f"[공고 정보]\n{json.dumps(job_payload, ensure_ascii=False)}"
    )


def generate_job_recommendation(*, ai_profile: dict[str, Any], job_payload: dict[str, Any]) -> dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "fit_score": {"type": "integer"},
            "summary": {"type": "string"},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "gaps": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "보완이 필요한 점과 함께, 어떤 프로젝트나 문서로 보완하면 되는지 예시를 포함한 문장",
                },
            },
            "study_plan": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "어떤 기술을 어떤 방식으로 학습하고, 어떤 결과물로 증명할지 예시를 포함한 실행 문장",
                },
            },
        },
        "required": ["fit_score", "summary", "strengths", "gaps", "study_plan"],
        "additionalProperties": False,
    }
    return call_openai_json_schema(
        model=getattr(settings, "OPENAI_JOB_MODEL", "gpt-4.1-mini"),
        schema_name="job_fit_analysis",
        schema=schema,
        system_prompt=(
            "너는 학생 맞춤 채용 추천 분석기다. "
            "학생 프로필과 채용 공고를 비교해서 강점, 부족한 부분, 추천 학습 포인트를 짧고 구체적으로 정리한다. "
            "gaps와 study_plan은 반드시 예시를 포함해야 하며, "
            "예를 들어 어떤 기술을 사용해 어떤 프로젝트를 만들고 README나 포트폴리오에 어떤 식으로 정리할지까지 제시한다."
        ),
        user_prompt=build_job_prompt(ai_profile=ai_profile, job_payload=job_payload),
    )
