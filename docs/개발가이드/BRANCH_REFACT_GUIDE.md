# refact_front_to_nextjs 브랜치 작업 가이드

> AI 도구(Claude 등) 참고용 문서입니다.
> 이 브랜치에서 작업하거나, 다른 브랜치 변경사항을 머지할 때 반드시 읽어주세요.

---

## 브랜치 목적

기존 Django 템플릿 기반 프론트엔드를 **Next.js 16 (App Router)** 로 전환하는 작업입니다.

| 구분 | 기존 (master / develop) | 이 브랜치 |
|---|---|---|
| 프론트엔드 | `Back-end/templates/*.html` | `front-end/` (Next.js) |
| 스타일 | Django static CSS/JS | Tailwind CSS v4 |
| 인증 | Django session | NextAuth v4 (JWT) |
| 프론트 실행 | Django runserver | `npm run dev` (port 3000) |
| 백엔드 역할 | 템플릿 렌더링 + API | **API 전용** |

---

## 폴더 구조

```
team_lab/
├── Back-end/          # Django (API 서버)
├── front-end/         # Next.js (이 브랜치에서 새로 추가)
│   ├── app/           # 페이지 라우팅 (App Router)
│   ├── components/    # 공용 컴포넌트
│   ├── server/        # 서버 액션, NextAuth 설정
│   ├── store/         # Redux Toolkit
│   └── .env.local     # 로컬 환경변수 (gitignore)
├── Mobile/            # React Native 앱
├── docker-compose.yml # 전체 스택 실행용
└── docs/
```

---

## 충돌 주의 포인트

### 1. `Back-end/templates/` 수정 → 이 브랜치에서 의미 없음
다른 브랜치에서 `.html` 파일을 수정해도 이 브랜치에서는 Next.js가 프론트를 담당합니다.
**Django 템플릿 변경사항은 이 브랜치에 머지하지 마세요.**

### 2. 백엔드 views — 반드시 JSON 반환
이 브랜치에서 백엔드 views는 `render()` 대신 `JsonResponse` 또는 DRF Response만 사용해야 합니다.

```python
# ❌ 이 브랜치에서 사용 금지
return render(request, 'attendance/index.html', context)

# ✅
return JsonResponse({"data": ...})
```

### 3. `Back-end/config/urls.py` — `api/` 접두사 유지
모든 라우트는 `/api/...` 형태를 유지해야 Next.js에서 호출 가능합니다.
현재 모든 라우트가 `api/`로 시작하도록 정리된 상태입니다. 새 앱 추가 시 동일하게 따라주세요.

```python
# ✅
path('api/새기능/', include('새기능.urls')),
```

### 4. 새 페이지 추가
다른 브랜치에서 Django 템플릿으로 페이지를 추가했다면, 이 브랜치에서는 `front-end/app/` 아래에 Next.js 페이지로 구현해야 합니다.

```
# 예: 출결 페이지 추가 시
front-end/app/attendance/
├── page.tsx
└── _components/
    └── AttendanceList.tsx
```

---

## 로컬 실행 방법

### 전체 스택 (Docker)
```bash
# 루트 디렉토리에서
docker-compose up --build
# 백엔드: http://localhost:8000
# 프론트: http://localhost:3000
```

### 개별 실행
```bash
# 백엔드
cd Back-end && python manage.py runserver

# 프론트 (별도 터미널)
cd front-end && npm run dev
```

### 환경변수 설정 (최초 1회)
```bash
cp front-end/.env.example front-end/.env.local
# .env.local 열어서 값 채우기
```

---

## 현재 Next.js 구현 현황

| 기능 | 상태 |
|---|---|
| 레이아웃 / 헤더 / 푸터 | ✅ 완료 |
| 로그인 (NextAuth) | ✅ 완료 |
| 모바일 메뉴 | ✅ 완료 |
| 출결 / 플래너 / 퀴즈 등 | ⬜ 미구현 |

---

## 새 기능 작업 시 체크리스트

- [ ] 백엔드 view가 JSON을 반환하는가?
- [ ] URL이 `/api/...` 형태인가?
- [ ] 프론트 페이지는 `front-end/app/` 아래에 만들었는가?
- [ ] API 호출은 `@/lib/api-client.ts` 의 `dbFetch` 를 사용하는가?
- [ ] `Back-end/templates/` 는 건드리지 않았는가?
