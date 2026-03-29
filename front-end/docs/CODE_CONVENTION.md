# 코드 컨벤션

## 언어 및 환경

- **언어** : TypeScript (strict 모드)
- **프레임워크** : Next.js 16 App Router
- **스타일** : Tailwind CSS v4

---

## 네이밍

| 대상 | 방식 | 예시 |
|---|---|---|
| 컴포넌트 파일 | PascalCase | `UserDropdown.tsx` |
| 일반 파일/폴더 | kebab-case | `api-client.ts`, `auth-button.tsx` |
| 컴포넌트 함수 | PascalCase | `export default function Header()` |
| 변수/함수 | camelCase | `menuOpen`, `handleCheckIn` |
| 상수 | UPPER_SNAKE_CASE | `NAV_LINKS` |
| enum | PascalCase (키는 UPPER_SNAKE_CASE) | `Routes.ATTENDANCE` |
| 타입/인터페이스 | PascalCase | `type AttendanceRecord` |

---

## 컴포넌트

```tsx
// ✅ 함수 선언식 사용
export default function Header() { ... }

// ❌ 화살표 함수 default export 지양
const Header = () => { ... }
export default Header;
```

- 클라이언트 컴포넌트는 파일 최상단에 `"use client"` 선언
- 서버 컴포넌트가 기본값, 필요할 때만 `"use client"` 사용
- props 타입은 컴포넌트 바로 위에 `type Props` 로 정의

```tsx
type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export default function Navbar({ isOpen, onClose }: Props) { ... }
```

---

## 폴더 구조

- 페이지 전용 컴포넌트는 해당 페이지 폴더 안 `_components/` 에 위치
- `_components/` 는 Next.js 라우팅에서 자동 제외됨

```
app/
└── attendance/
    ├── page.tsx
    └── _components/
        ├── AttendanceList.tsx
        └── DailyGoalModal.tsx
```

---

## 상수/경로

- 하드코딩 경로 사용 금지, 반드시 `@/constants/enums` 의 enum 사용
- 페이지 경로 조합 방식

```ts
// ✅
href={`${Routes.USERS}/${Pages.EDIT}`}  // → /users/edit

// ❌
href="/users/edit"
```

---

## Import 순서

```ts
// 1. React / Next.js
import { useState } from "react";
import Link from "next/link";

// 2. 외부 라이브러리
import { useSession } from "next-auth/react";

// 3. 내부 컴포넌트
import UserDropdown from "./UserDropdown";

// 4. 상수 / 타입 / 유틸
import { Routes, Pages } from "@/constants/enums";
import { cn } from "@/lib/utils";
```

---

## API 호출

- 모든 API 호출은 `@/lib/api-client.ts` 를 통해서만 처리
- 미완성 API는 반드시 `// TODO: GET /api/...` 주석 명시

```ts
// TODO: GET /api/attendance/list/
const fetchList = async () => { ... };
```
