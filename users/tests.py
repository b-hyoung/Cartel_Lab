from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        self.assertEqual(user.daily_analysis_count, 1)
        self.assertEqual(user.daily_analysis_date, timezone.localdate())

    @patch("users.views.build_profile_analysis")
    def test_profile_update_blocks_after_three_daily_analyses(self, mock_build_profile_analysis):
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

        for _ in range(3):
            response = self.client.post(
                reverse("users-index"),
                {
                    "github_url": "https://github.com/bhs-dev",
                    "action": "analyze",
                },
            )
            self.assertRedirects(response, reverse("users-index"))

        response = self.client.post(
            reverse("users-index"),
            {
                "github_url": "https://github.com/bhs-dev",
                "action": "analyze",
            },
            follow=True,
        )

        user.refresh_from_db()
        self.assertContains(response, "오늘은 분석을 3번 모두 사용했습니다.")
        self.assertEqual(user.daily_analysis_count, 3)
        self.assertEqual(mock_build_profile_analysis.call_count, 3)
