from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .services import build_portfolio_review_input, format_portfolio_feedback
from .models import User


class AuthFlowTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("users-signup"),
            {
                "student_id": "20240001",
                "name": "홍길동",
                "password1": "teamlab-pass-123",
                "password2": "teamlab-pass-123",
            },
        )

        self.assertRedirects(response, reverse("users-index"))
        self.assertTrue(User.objects.filter(student_id="20240001", name="홍길동").exists())
        self.assertEqual(self.client.session.get("_auth_user_id"), str(User.objects.get(student_id="20240001").pk))

    def test_login_uses_student_id_and_password(self):
        user = User.objects.create_user(
            student_id="20240002",
            name="김학생",
            password="teamlab-pass-123",
        )

        response = self.client.post(
            reverse("users-login"),
            {
                "student_id": "20240002",
                "password": "teamlab-pass-123",
            },
        )

        self.assertRedirects(response, reverse("users-index"))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    @patch("users.views.build_profile_analysis")
    def test_profile_update_save_only_stores_inputs_without_analysis(self, mock_build_profile_analysis):
        user = User.objects.create_user(
            student_id="20240003",
            name="박형석",
            password="teamlab-pass-123",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users-index"),
            {
                "github_url": "https://github.com/bhs-dev",
                "resume_file": SimpleUploadedFile(
                    "resume.txt",
                    b"Python Django AWS experience",
                    content_type="text/plain",
                ),
                "action": "save",
            },
        )

        self.assertRedirects(response, reverse("users-index"))
        user.refresh_from_db()
        self.assertEqual(user.github_url, "https://github.com/bhs-dev")
        self.assertTrue(bool(user.resume_file))
        self.assertEqual(user.github_username, "")
        self.assertIsNone(user.profile_analyzed_at)
        mock_build_profile_analysis.assert_not_called()

    @patch("users.views.build_profile_analysis")
    def test_profile_update_analyze_applies_analysis_result(self, mock_build_profile_analysis):
        user = User.objects.create_user(
            student_id="20240004",
            name="박형석",
            password="teamlab-pass-123",
        )
        self.client.force_login(user)
        mock_build_profile_analysis.return_value = {
            "github_username": "bhs-dev",
            "github_profile_summary": "공개 저장소 5개 / 주요 언어 Python, TypeScript",
            "github_top_languages": "Python, TypeScript",
            "resume_extracted_text": "Python Django AWS 경험",
            "resume_analysis_summary": "백엔드 프로젝트 경험 / 배포 경험 / 협업 경험",
            "analysis_recommendation": "AWS 배포 경험을 더 구체적으로 정리하세요.",
        }

        response = self.client.post(
            reverse("users-index"),
            {
                "github_url": "https://github.com/bhs-dev",
                "resume_file": SimpleUploadedFile(
                    "resume.txt",
                    b"Python Django AWS experience",
                    content_type="text/plain",
                ),
                "action": "analyze",
            },
        )

        self.assertRedirects(response, reverse("users-index"))
        user.refresh_from_db()
        self.assertEqual(user.github_username, "bhs-dev")
        self.assertIn("Python", user.github_top_languages)
        self.assertIn("백엔드 프로젝트 경험", user.resume_analysis_summary)
        self.assertTrue(bool(user.profile_analyzed_at))

    @patch("users.views.get_or_refresh_market_snapshot")
    @patch("users.views.build_profile_analysis")
    def test_profile_update_analyze_passes_selected_direction_to_analysis(
        self,
        mock_build_profile_analysis,
        mock_get_or_refresh_market_snapshot,
    ):
        user = User.objects.create_user(
            student_id="20240006",
            name="방향학생",
            password="teamlab-pass-123",
        )
        self.client.force_login(user)
        mock_get_or_refresh_market_snapshot.return_value = SimpleNamespace(
            analysis_summary="테스트",
            role_breakdown=[{"role": "Frontend", "ratio": 40, "major_skills": ["React", "TypeScript"]}],
        )
        mock_build_profile_analysis.return_value = {
            "github_username": "bhs-dev",
            "github_profile_summary": "공개 저장소는 5개입니다.",
            "github_top_languages": "Python, TypeScript",
            "resume_extracted_text": "Python Django AWS 경험",
            "resume_analysis_summary": "백엔드 프로젝트 경험 / 배포 경험 / 협업 경험",
            "analysis_recommendation": "AWS 배포 경험을 더 구체적으로 정리하세요.",
        }

        response = self.client.post(
            reverse("users-index"),
            {
                "job_direction_choice": "Frontend",
                "desired_job_direction_other": "",
                "github_url": "https://github.com/bhs-dev",
                "resume_file": SimpleUploadedFile(
                    "resume.txt",
                    b"Python Django AWS experience",
                    content_type="text/plain",
                ),
                "action": "analyze",
            },
        )

        self.assertRedirects(response, reverse("users-index"))
        user.refresh_from_db()
        self.assertEqual(user.desired_job_direction, "Frontend")
        self.assertEqual(mock_build_profile_analysis.call_count, 1)
        args, kwargs = mock_build_profile_analysis.call_args
        self.assertEqual(args[0], "https://github.com/bhs-dev")
        self.assertIn("resume", getattr(args[1], "name", ""))
        self.assertEqual(kwargs["desired_direction"], "Frontend")
        self.assertEqual(
            kwargs["market_role_context"],
            {"role": "Frontend", "ratio": 40, "major_skills": ["React", "TypeScript"]},
        )

    @patch("users.views.build_profile_analysis")
    def test_profile_update_allows_repeated_analysis_without_daily_limit(self, mock_build_profile_analysis):
        user = User.objects.create_user(
            student_id="20240005",
            name="제한학생",
            password="teamlab-pass-123",
            github_url="https://github.com/bhs-dev",
        )
        user.resume_file = "resumes/resume.txt"
        user.save()
        self.client.force_login(user)
        mock_build_profile_analysis.return_value = {
            "github_username": "bhs-dev",
            "github_profile_summary": "공개 저장소 5개",
            "github_top_languages": "Python",
            "resume_extracted_text": "Python 경험",
            "resume_analysis_summary": "프로젝트 경험",
            "analysis_recommendation": "보완 필요",
        }

        for _ in range(4):
            response = self.client.post(
                reverse("users-index"),
                {
                    "github_url": "https://github.com/bhs-dev",
                    "action": "analyze",
                },
            )
            self.assertRedirects(response, reverse("users-index"))

        user.refresh_from_db()
        self.assertTrue(bool(user.profile_analyzed_at))
        self.assertEqual(mock_build_profile_analysis.call_count, 4)

    def test_profile_update_save_allows_other_direction_input(self):
        user = User.objects.create_user(
            student_id="20240007",
            name="기타학생",
            password="teamlab-pass-123",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users-index"),
            {
                "job_direction_choice": "__other__",
                "desired_job_direction_other": "게임 클라이언트",
                "github_url": "",
                "action": "save",
            },
        )

        self.assertRedirects(response, reverse("users-index"))
        user.refresh_from_db()
        self.assertEqual(user.desired_job_direction, "게임 클라이언트")
        self.assertEqual(user.desired_job_direction_other, "게임 클라이언트")


class ProfileAnalysisFormattingTests(TestCase):
    def test_build_portfolio_review_input_excludes_skill_stack_and_keeps_project_descriptions(self):
        source = """
        박형석
        youqlrqod@gmail.com
        01064152785
        기술 스택
        Next.js, TypeScript, React, Firebase, AWS, Docker
        프로젝트 경험
        Next.js와 React를 활용해 SSR 기반 웹서비스를 개발하고 이미지 로딩 최적화로 LCP를 3초에서 1초로 개선했습니다.
        GPT API 기반 문제 해설 기능을 구현하고 캐시 구조를 도입해 API 비용을 40% 절감했습니다.
        """

        review_input = build_portfolio_review_input(source)

        self.assertNotIn("Next.js, TypeScript, React, Firebase, AWS, Docker", review_input)
        self.assertIn("SSR 기반 웹서비스", review_input)
        self.assertIn("API 비용을 40% 절감", review_input)

    def test_format_portfolio_feedback_includes_all_items(self):
        feedback = format_portfolio_feedback(
            [
                {
                    "problem_sentence": "기능을 구현했습니다.",
                    "problem_points": ["성과가 보이지 않습니다."],
                    "improvement_points": ["사용 기술과 결과를 함께 적습니다."],
                    "before_example": "기능을 구현했습니다.",
                    "after_example": "React와 TypeScript로 기능을 구현하고 응답 시간을 20% 개선했습니다.",
                },
                {
                    "problem_sentence": "API를 사용했습니다.",
                    "problem_points": ["어떤 구조인지 보이지 않습니다."],
                    "improvement_points": ["캐시 구조와 비용 개선을 설명합니다."],
                    "before_example": "API를 사용했습니다.",
                    "after_example": "GPT API 호출에 캐시를 도입해 비용을 40% 절감했습니다.",
                },
            ]
        )

        self.assertIn("기능을 구현했습니다.", feedback)
        self.assertIn("API를 사용했습니다.", feedback)
        self.assertIn("40% 절감", feedback)
