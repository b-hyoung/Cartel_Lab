import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.utils import timezone
from contests.models import Contest

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 수집할 Wevity 카테고리 (cidx: 이름)
# 페이지네이션이 동작하지 않아 카테고리별 1페이지씩 수집
WEVITY_CATEGORIES = {
    20: "웹/모바일",
    21: "게임/소프트웨어",
    22: "과학/공학",
    10: "영상/UCC",
}

class WevityScraper:
    BASE_URL = "https://www.wevity.com"
    LIST_URL_TEMPLATE = "https://www.wevity.com/?c=find&s=1&gub=1&cidx={cidx}&page=1"

    def fetch(self) -> list:
        headers = {"User-Agent": USER_AGENT}
        contest_list = []
        seen_ids = set()
        today = timezone.now().date()

        for cidx in WEVITY_CATEGORIES:
            url = self.LIST_URL_TEMPLATE.format(cidx=cidx)
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
            except Exception as e:
                print(f"Error fetching cidx={cidx}: {e}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('ul.list > li')

            for row in rows:
                title_tag = row.select_one('.tit a')
                if not title_tag: continue

                title = title_tag.get_text(strip=True)
                relative_link = title_tag.get('href', '')

                # ID 추출 및 중복 제거
                external_id_match = re.search(r'(?:ix|id)=(\d+)', relative_link)
                external_id = external_id_match.group(1) if external_id_match else relative_link
                if external_id in seen_ids:
                    continue
                seen_ids.add(external_id)

                # URL 절대 경로 보장
                if relative_link.startswith('http'):
                    external_url = relative_link
                else:
                    path = relative_link if relative_link.startswith('/') else '/' + relative_link
                    external_url = self.BASE_URL + path

                host = row.select_one('.organ').get_text(strip=True) if row.select_one('.organ') else "주최사 정보 없음"

                # 마감일 처리 및 활성 상태 판별
                day_tag = row.select_one('.day')
                deadline_str = day_tag.get_text(strip=True) if day_tag else ""
                deadline_at = None
                is_active = True

                if any(k in deadline_str for k in ['D+', '종료', '종료된']) or \
                   ('마감' in deadline_str and '마감임박' not in deadline_str) or \
                   '[마감]' in title:
                    is_active = False

                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', deadline_str)
                if date_match:
                    try:
                        deadline_at = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                        if deadline_at < today:
                            is_active = False
                    except ValueError:
                        pass
                else:
                    d_day_match = re.search(r'D-(\d+)', deadline_str)
                    if d_day_match:
                        days_left = int(d_day_match.group(1))
                        deadline_at = today + timedelta(days=days_left)
                    elif '오늘마감' in deadline_str or 'D-0' in deadline_str:
                        deadline_at = today

                # 카테고리 분류
                title_lower = title.lower()
                ai_keywords = ['생성형', 'ai', '인공지능', 'llm', 'gpt', '딥러닝', '머신러닝', '데이터', '빅데이터', '챗봇', '영상ai', 'ai영상']
                dev_keywords = ['개발', '해커톤', 'sw', '소프트웨어', '알고리즘', '코딩', '웹', '앱', '프로그래밍', '백엔드', '프론트엔드']
                video_keywords = ['영상', 'ucc', '숏폼', '유튜브', '촬영', '홍보영상', '영화', '다큐']

                category = "기타 IT"
                if any(k in title_lower for k in ai_keywords):
                    category = "생성형 AI"
                elif any(k in title_lower for k in dev_keywords):
                    category = "SW 개발"
                elif any(k in title_lower for k in video_keywords):
                    category = "영상/UCC"

                contest_list.append({
                    'source': 'wevity',
                    'external_id': external_id,
                    'external_url': external_url,
                    'title': title,
                    'host': host,
                    'category': category,
                    'deadline_at': deadline_at,
                    'is_active': is_active,
                    'image_url': '',
                })

        return contest_list


def fetch_wevity_image(external_url: str) -> str:
    """Wevity 상세 페이지에서 OG 이미지 URL 추출"""
    try:
        res = requests.get(external_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.select_one('meta[property="og:image"]')
        if og and og.get('content'):
            return og['content']
    except Exception:
        pass
    return ''


def sync_contests():
    scraper = WevityScraper()
    contests = scraper.fetch()

    created_count = 0
    updated_count = 0

    for data in contests:
        obj, created = Contest.objects.update_or_create(
            source=data['source'],
            external_id=data['external_id'],
            defaults={
                'title': data['title'],
                'host': data['host'],
                'category': data['category'],
                'external_url': data['external_url'],
                'deadline_at': data['deadline_at'],
                'is_active': data['is_active'],
            }
        )
        # 신규 공모전이거나 이미지가 없는 경우에만 상세 페이지에서 이미지 수집
        if created or not obj.image_url:
            image_url = fetch_wevity_image(data['external_url'])
            if image_url:
                obj.image_url = image_url
                obj.save(update_fields=['image_url'])

        if created: created_count += 1
        else: updated_count += 1

    return {"created": created_count, "updated": updated_count}
