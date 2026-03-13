from django.test import TestCase

from planner.models import JobPosting
from planner.services.job_detail import (
    parse_saramin_detail_payload,
    parse_wanted_detail_html,
    split_bullets,
)
from planner.services.market_analysis import build_heuristic_market_breakdown
from planner.services.recommendation import score_job_for_user
from planner.services.job_sync import SaraminScraper, WantedScraper
from planner.views import build_main_task_preview
from users.models import User


class JobSyncParsingTests(TestCase):
    def test_parse_saramin_listing_html(self):
        html = """
        <div id="rec-53213432" class="list_item effect">
            <div class="box_item">
                <div class="col company_nm">
                    <a class="str_tit" target="_blank">(주)아이샵케어</a>
                </div>
                <div class="col notification_info">
                    <div class="job_tit">
                        <a class="str_tit" title="백엔드 개발자 모집" href="/zf_user/jobs/relay/view?rec_idx=53213432"><span>백엔드 개발자 모집</span></a>
                    </div>
                    <div class="job_meta">
                        <span class="job_sector">
                            <span>백엔드/서버개발</span><span>웹개발</span>
                        </span>
                    </div>
                </div>
                <div class="col recruit_info">
                    <ul>
                        <li><p class="work_place">서울 강남구</p></li>
                        <li><p class="career">신입 · 정규직</p></li>
                        <li><p class="education">학력무관</p></li>
                    </ul>
                </div>
                <div class="col support_info">
                    <p class="support_detail">
                        <span class="date">~04.02(목)</span>
                        <span class="deadlines">1일 전 등록</span>
                    </p>
                </div>
            </div>
            <div class="similar_recruit"></div>
        </div>
        """

        jobs = SaraminScraper.parse_listing_html(html)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].external_id, "53213432")
        self.assertEqual(jobs[0].company_name, "(주)아이샵케어")
        self.assertTrue(jobs[0].is_junior_friendly)
        self.assertTrue(SaraminScraper._is_newbie_label(jobs[0].experience_label))

    def test_saramin_newbie_filter_rejects_mixed_experience(self):
        self.assertTrue(SaraminScraper._is_newbie_label("신입 · 경력 · 정규직"))
        self.assertFalse(SaraminScraper._is_newbie_label("경력무관 · 정규직"))

    def test_map_wanted_item(self):
        job = WantedScraper.map_item(
            {
                "id": 297859,
                "company": {"name": "리얼드로우"},
                "address": {"location": "서울", "district": "마포구"},
                "position": "Backend Engineer (5년 이상)",
                "category_tag": {"parent_id": 518, "id": 873},
                "skill_tags": [{"title": "Python"}, {"title": "Django"}],
                "annual_from": 1,
                "annual_to": 3,
                "is_newbie": False,
                "reward_total": "100만원",
                "employment_type": "regular",
            }
        )

        self.assertEqual(job.external_id, "297859")
        self.assertEqual(job.company_name, "리얼드로우")
        self.assertEqual(job.required_skills, "Python, Django")
        self.assertTrue(job.is_junior_friendly)
        self.assertFalse(WantedScraper._is_newbie_item({"is_newbie": False}))
        self.assertTrue(WantedScraper._is_newbie_item({"is_newbie": True}))


class JobDetailParsingTests(TestCase):
    def test_split_bullets(self):
        items = split_bullets("• 첫번째 항목\n• 두번째 항목\n세번째 항목")
        self.assertEqual(items, ["첫번째 항목", "두번째 항목", "세번째 항목"])

    def test_parse_wanted_detail_html(self):
        html = """
        <script id="__NEXT_DATA__" type="application/json" crossorigin="anonymous">
        {"props":{"pageProps":{"initialData":{
            "address":{"location":"서울","district":"강남구"},
            "company":{"company_name":"테스트회사","logo_image":"https://example.com/logo.png","title_images":["https://example.com/1.png"]},
            "position":"백엔드 개발자",
            "career":"newbie",
            "intro":"회사 소개입니다.",
            "main_tasks":"• API 개발\\n• 배포 자동화",
            "requirements":"• Python 경험",
            "preferred_points":"• Django 경험",
            "benefits":"• 식대 지원"
        }}}}
        </script>
        """

        detail = parse_wanted_detail_html(html)

        self.assertEqual(detail["company_name"], "테스트회사")
        self.assertEqual(detail["title"], "백엔드 개발자")
        self.assertEqual(detail["main_tasks"], ["API 개발", "배포 자동화"])
        self.assertEqual(detail["preferred_points"], ["Django 경험"])

    def test_parse_saramin_detail_payload(self):
        summary_html = """
        <div class="jv_header"><a class="company">(주)테스트</a><h1 class="tit_job">신입 개발자</h1></div>
        <div class="jv_cont jv_summary">
            <dl><dt>경력</dt><dd><strong>신입</strong></dd></dl>
            <dl><dt>학력</dt><dd><strong>학력무관</strong></dd></dl>
            <dl><dt>근무형태</dt><dd><strong>정규직</strong></dd></dl>
        </div><div class="job_divider"></div>
        <div id="map_0"><span class="spr_jview txt_adr">(06210) 서울 강남구</span></div>
        <div class="jv_cont jv_howto">
            <dl class="guide">
                <dt>지원방법</dt><dd class="method">홈페이지 지원</dd>
            </dl>
            <dl class="info_period">
                <dt>시작일</dt><dd>2026.03.10 00:00</dd>
                <dt class="end">마감일</dt><dd>2026.04.02 23:59</dd>
            </dl>
        </div>
        """
        detail_html = """
        <body><div class="user_content">
            <img src="https://example.com/poster.png" alt="채용 포스터">
            <map><area href="https://example.com/apply" alt="지원 링크"></map>
        </div></body>
        """

        detail = parse_saramin_detail_payload(summary_html, detail_html)

        self.assertEqual(detail["company_name"], "(주)테스트")
        self.assertEqual(detail["title"], "신입 개발자")
        self.assertEqual(detail["experience_label"], "신입")
        self.assertEqual(detail["detail_images"], ["https://example.com/poster.png"])
        self.assertEqual(detail["detail_links"][0]["label"], "지원 링크")

    def test_parse_saramin_detail_payload_with_text_sections(self):
        summary_html = """
        <div class="jv_header"><a class="company">(주)메디브</a><h1 class="tit_job">SW Web 개발자 모집</h1></div>
        <div class="jv_cont jv_summary">
            <dl><dt>경력</dt><dd><strong>신입 · 경력</strong></dd></dl>
            <dl><dt>학력</dt><dd><strong>대졸(4년) 이상</strong></dd></dl>
            <dl><dt>근무형태</dt><dd><strong>정규직</strong></dd></dl>
        </div><div class="job_divider"></div>
        <div id="map_0"><span class="spr_jview txt_adr">충북 청주시</span></div>
        <div class="jv_cont jv_howto">
            <dl class="guide">
                <dt>지원방법</dt><dd class="method">사람인 입사지원</dd>
            </dl>
        </div>
        """
        detail_html = """
        <body><div class="user_content">
            <div class="info-block">
                <p class="info-block__title">회사소개</p>
                <div class="info-block__list">
                    <p>AI-SW 플랫폼을 개발합니다.</p>
                </div>
            </div>
            <div class="info-block">
                <p class="info-block__title">주요업무</p>
                <div class="info-block__list">
                    <p>• Web 솔루션 프론트/백엔드 설계 및 개발</p>
                    <p>• Web 솔루션 유지보수 및 고도화</p>
                </div>
            </div>
            <div class="info-block">
                <p class="info-block__title">이런 분을 찾고 있어요</p>
                <div class="info-block__list">
                    <p>• 기술스택 : Django, Docker, TypeScript</p>
                    <p>• 대학교졸업(4년)이상</p>
                </div>
            </div>
            <div class="info-block">
                <p class="info-block__title">이런 분이면 더 좋아요</p>
                <div class="info-block__list">
                    <p>• 풀스택 개발자 우대</p>
                </div>
            </div>
        </div></body>
        """

        detail = parse_saramin_detail_payload(summary_html, detail_html)

        self.assertEqual(detail["company_name"], "(주)메디브")
        self.assertIn("AI-SW 플랫폼을 개발합니다.", detail["overview"])
        self.assertEqual(detail["main_tasks"][0], "Web 솔루션 프론트/백엔드 설계 및 개발")
        self.assertIn("기술스택 : Django, Docker, TypeScript", detail["requirements"])
        self.assertEqual(detail["required_skills"], ["Django", "Docker", "TypeScript"])
        self.assertEqual(detail["preferred_points"][0], "풀스택 개발자 우대")


class JobCardPreviewTests(TestCase):
    def test_build_main_task_preview_uses_detail_main_tasks(self):
        job = JobPosting(
            source="saramin",
            external_id="1",
            external_url="https://example.com/1",
            title="백엔드 개발자",
            company_name="테스트1",
            detail_main_tasks="API 개발\n서버 운영\n테스트 코드 작성\n문서화",
        )

        preview = build_main_task_preview(job)

        self.assertEqual(preview, ["API 개발", "서버 운영", "테스트 코드 작성"])


class JobRecommendationTests(TestCase):
    def test_score_job_for_user_uses_github_and_resume_data(self):
        user = User(
            student_id="20240010",
            name="추천학생",
            github_url="https://github.com/reco-user",
            github_profile_summary="주요 언어 Python, React",
            github_top_languages="Python, TypeScript",
            resume_extracted_text="Python Django AWS Git 프로젝트 경험",
            resume_analysis_summary="백엔드 API 개발과 AWS 배포 경험",
        )
        user.resume_file.name = "resumes/test.pdf"

        job = JobPosting(
            source="wanted",
            external_id="1",
            external_url="https://example.com/job",
            title="백엔드 개발자",
            company_name="테스트회사",
            job_role="Backend Engineer",
            detail_required_skills="Python\nDjango\nAWS\nDocker",
            detail_requirements="Python 경험\nREST API 개발 경험",
            detail_main_tasks="백엔드 API 개발\n서비스 운영",
        )

        result = score_job_for_user(user, job)

        self.assertIsNotNone(result["score"])
        self.assertGreaterEqual(result["score"], 50)
        self.assertIn("python", result["matched_skills"])


class JobMarketAnalysisTests(TestCase):
    def test_build_heuristic_market_breakdown_groups_roles_and_skills(self):
        jobs = [
            JobPosting(
                source="wanted",
                external_id="1",
                external_url="https://example.com/1",
                title="Frontend Developer",
                company_name="A",
                detail_requirements="React TypeScript",
                required_skills="React, TypeScript, HTML",
            ),
            JobPosting(
                source="saramin",
                external_id="2",
                external_url="https://example.com/2",
                title="Backend Engineer",
                company_name="B",
                detail_requirements="Python Django REST API",
                required_skills="Python, Django, AWS",
            ),
            JobPosting(
                source="saramin",
                external_id="3",
                external_url="https://example.com/3",
                title="Backend API Developer",
                company_name="C",
                detail_requirements="Java Spring API",
                required_skills="Java, Spring, SQL",
            ),
        ]

        result = build_heuristic_market_breakdown(jobs)

        self.assertTrue(result["role_breakdown"])
        self.assertEqual(result["role_breakdown"][0]["role"], "Web Backend")
        self.assertIn("Python", result["role_breakdown"][0]["major_skills"])
