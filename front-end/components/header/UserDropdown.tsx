"use client";

import { useState, useRef, useEffect } from "react";
import { useSession, signOut } from "next-auth/react";
import Link from "next/link";
import { Routes, Pages } from "@/constants/enums";

export default function UserDropdown() {
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // 외부 클릭 시 닫기
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (!session) {
    return (
      <Link
        href="/login"
        className="rounded-lg px-2.5 py-1.5 text-sm font-semibold text-gray-500 hover:bg-gray-100 hover:text-gray-900 transition-colors"
      >
        로그인
      </Link>
    );
  }

  const user = session.user;
  const initial = user?.name?.slice(0, 1) ?? "?";

  return (
    <div ref={ref} className="relative ml-1.5">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-semibold text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900"
      >
        {user?.image ? (
          <img src={user.image} className="h-6 w-6 rounded-full object-cover border border-gray-200" />
        ) : (
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
            {initial}
          </span>
        )}
        {user?.name}
        <svg
          className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`}
          viewBox="0 0 16 16" fill="none"
        >
          <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 top-[calc(100%+8px)] z-50 min-w-[180px] rounded-2xl border border-gray-100 bg-white p-1.5 shadow-lg">
          <Link href={`${Routes.USERS}/${Pages.EDIT}`} onClick={() => setOpen(false)} className="dropdown-item">
            <EditIcon /> 내 정보 변경
          </Link>
          <Link href={Routes.USERS} onClick={() => setOpen(false)} className="dropdown-item">
            <ProfileIcon /> 내 정보 및 이력서 분석
          </Link>
          <div className="my-1 h-px bg-gray-100" />
          <button
            onClick={() => signOut()}
            className="dropdown-item w-full text-red-600 hover:bg-red-50"
          >
            <LogoutIcon /> 로그아웃
          </button>
        </div>
      )}
    </div>
  );
}

const EditIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
  </svg>
);

const ProfileIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="4"/>
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
  </svg>
);

const LogoutIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
    <polyline points="16 17 21 12 16 7"/>
    <line x1="21" y1="12" x2="9" y2="12"/>
  </svg>
);
