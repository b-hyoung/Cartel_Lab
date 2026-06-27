# Jvision Lab (Cartel_Lab)

학과 1·2학년이 함께 쓰는 학습 관리 플랫폼입니다. 출결, 주간계획, 시험·자격증 D-day 같은 기본 기능에 더해, 2학년 멘토가 낸 코딩 문제를 1학년이 풀고 AI가 1차 채점하는 흐름이 GitHub과 붙어 돌아갑니다. 백엔드는 Django, 프론트는 Next.js로 분리했고 모바일(React Native)도 같이 둡니다.

## 코딩 문제 자동화 (mentor-problems 연동)

문제 출제부터 채점까지 사람이 반복으로 손대는 구간을 줄였습니다. 짝이 되는 저장소 [jvision-mentor-problems](https://github.com/b-hyoung/jvision-mentor-problems)와 GitHub Actions로 맞물립니다.

1. 2학년 멘토가 mentor-problems에 문제 마크다운을 PR로 올립니다.
2. 머지되면 Actions가 GPT로 채점 설정(힌트·엣지케이스)을 만들고, 이 플랫폼에 퀴즈로 자동 등록합니다.
3. 1학년이 자기 브랜치에서 답안을 PR로 올리면, AI가 기본·심화 테스트를 돌려 통과 여부와 힌트를 코멘트로 답니다.
4. 채점 결과가 Discord로 담당 멘토에게 갑니다. 멘토가 코드를 직접 보고 고칠 부분·개선점을 짚어준 뒤, 괜찮으면 main에 올립니다.

AI는 1차 거름망입니다. 최종 판단은 멘토가 코드를 직접 보고 합니다. master 직접 푸시를 막고, 답안 머지는 허용된 멘토의 승인이 있어야만 통과하도록 Actions에서 한 번 더 검사합니다(`.github/workflows/allowed-reviewer-check.yml`). AI 코멘트가 통과를 줘도 멘토가 코드를 안 보면 main에 못 올라갑니다.

## 프로젝트 역할 분담 (4인)

### 박형석 (PM · 구조 설계 · 채용 추천)
- Django 모놀리식을 Next.js 프론트로 분리하고, AI 코딩 도구가 작업하기 좋게 컴포넌트·타입·컨벤션 구조를 먼저 잡음
- mentor-problems와 묶은 AI 채점·자동화 파이프라인 설계 (위 "코딩 문제 자동화" 참고)
- 이력서·GitHub를 분석해 강·약점 피드백 (`users/ai_services.py`)
- 채용 공고 수집 파이프라인: 사람인·원티드에서 정기 동기화, 소스별 최신 300건 유지 (`planner/services/job_sync.py`, 소스는 `.env`로 교체 가능)
- 이력서·GitHub 기반 기업 추천 점수 집계 (`planner/services/recommendation.py`, gpt-4.1-mini)

### 유현기
- 위치데이터 기반 출결
- 출결 달성률

### 조우진
- 주간계획
- 개인목표 리스트

### 황현준
- 회원가입 및 로그인
- 학과 시간표 등록
- 시험/자격증 D-day 캘린더

## 이후 확장 기능
- 사람인/당근 등 최근 일자리 정보 검색 결과 100개 조회
- AI 기반 이력서 매칭 기능 추가

## 일자리 정보 패치 정책
- 최근 일자리 정보는 `주 1회` 패치 방식으로 운영
- 소스별 활성 공고는 최신 기준 `300건` 유지 (`saramin`, `wanted`)
- 설정 파일: `.env`의 `JOB_ACTIVE_LIMIT_PER_SOURCE`, `JOB_ACTIVE_SOURCES`
- 활성 건수 정리 명령:
```bash
python manage.py enforce_job_active_limit
```

## 패키지 설치 후 requirements 반영
팀원이 로컬에서 새 패키지를 설치했다면 아래 순서로 `requirements.txt`에 반영합니다.

## 1. 프로젝트 이동
```bash
cd team_lab
```

## 2. 가상환경(venv) 생성
처음 한 번만 실행합니다.
macOS / Linux:
```bash
python3 -m venv venv
```

Windows (PowerShell):
```powershell
python -m venv venv
```

## 3. 가상환경 활성화
macOS / Linux:
```bash
source venv/bin/activate
```

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
venv\Scripts\activate.bat
```

## 4. 의존성 설치
macOS / Linux:
```bash
pip install -r requirements.txt
```

Windows (PowerShell/CMD):
```powershell
pip install -r requirements.txt
```

# 라이브러리 설치 시 해야할 행동
1. 패키지 설치
```bash
pip install <패키지명>
```

2. 동결 파일 갱신
```bash
pip freeze > requirements.txt
```


## 5. Django 점검 및 DB 반영
모델을 추가하거나 수정했으면 아래 `makemigrations`, `migrate`를 다시 실행해야 합니다.

macOS / Linux:
```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
```

Windows (PowerShell/CMD):
```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
```

예시:
- 회원가입/로그인처럼 사용자 모델이 바뀐 경우에도 반드시 `python manage.py makemigrations` 후 `python manage.py migrate`를 실행합니다.

## 6. 서버 실행
macOS / Linux:
```bash
python manage.py runserver
```

Windows (PowerShell/CMD):
```powershell
python manage.py runserver
```

브라우저 접속:
- `http://127.0.0.1:8000/`

## 7. 작업 종료
macOS / Linux:
```bash
deactivate
```

Windows (PowerShell/CMD):
```powershell
deactivate
```

## 참고
- 이미 `venv` 폴더가 있으면 `2번(가상환경 생성)`은 생략하고 `3번`부터 진행하면 됩니다.
- Windows PowerShell에서 실행 정책 에러가 나면 관리자 권한 PowerShell에서 아래 1회 실행 후 다시 활성화하세요.
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Redis 캐시 설정 (Upstash)

AI 추천 결과 및 반복 DB 쿼리 캐싱을 위해 Upstash Redis를 사용합니다.

### 환경변수 설정
```
REDIS_URL=rediss://default:<password>@<host>:6379
```
- 로컬: `.env`에 추가
- 배포: Railway 대시보드 Variables에 추가

`REDIS_URL`이 없으면 자동으로 로컬 메모리 캐시로 폴백합니다.

### 캐시 적용 목록

| 대상 | 캐시 키 | TTL | 무효화 시점 |
|------|---------|-----|------------|
| jobs 공고 목록 + 스코어링 | `jobs_index_{user_id}` | 24시간 | DB 자정 초기화 시 자동 만료 |
| AI 공고 추천 결과 | `ai_job_rec_{user_id}_{job_id}` | 24시간 | DB 자정 초기화 시 자동 만료 |
| 시장 분석 스냅샷 | `market_snapshot` | 1시간 | 매일 12시 갱신 후 자동 만료 |
| 출결 시간 설정 | `attendance_time_setting` | 24시간 | 설정 변경 시 즉시 삭제 |
| 출결 위치 설정 | `attendance_location_setting` | 24시간 | 위치 변경 시 즉시 삭제 |
| 오늘 퀴즈 | `quiz_today_{date}` | 자정까지 | 날짜 바뀌면 자동 만료 |

## DB Guide
- Team MySQL setup: `docs/DB_MYSQL_SETUP.md`

## Docker Guide
- Docker 실행 방법: `docs/DOCKER.md`

## 문서 목록
- 상세 문서는 `docs/` 폴더에서 관리합니다.
- 작업 우선순위: `docs/PRIORITY.md`
