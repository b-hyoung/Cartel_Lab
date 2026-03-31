"use client";

import { useSession } from "next-auth/react";
import { useEffect, useRef, useState } from "react";
import { useAuthFetch } from "@/lib/use-auth-fetch";
import { Routes, ApiPaths, Methods } from "@/constants/enums";
import type { User, Profile } from "@/types/user";

export default function MyPage() {
  const { data: session } = useSession();
  const authFetch = useAuthFetch();
  const [me, setMe] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [githubLoading, setGithubLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [resumeUploading, setResumeUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!session) return;

    const params = new URLSearchParams(window.location.search);
    if (params.get("github") === "success") {
      window.history.replaceState({}, "", "/users");
    }

    Promise.all([
      authFetch(`${Routes.AUTH}${ApiPaths.ME}`).then(setMe).catch(() => null),
      authFetch(`${Routes.AUTH}${ApiPaths.PROFILE}`).then(setProfile).catch(() => null),
    ]).finally(() => setProfileLoading(false));
  }, [session]);

  const name = me?.name ?? session?.user?.name ?? "";
  const DEFAULT_PROFILE_IMAGES = ["/images/default_01.png", "/images/default_02.png", "/images/default_03.png", "/images/default_04.png"];
  // 헤더와 동일한 로직
  const profileImage = me?.profile_image || (session?.user
    ? (session.user.image || DEFAULT_PROFILE_IMAGES[Number(session.user.id) % DEFAULT_PROFILE_IMAGES.length])
    : null);

  async function handleGithubConnect() {
    setGithubLoading(true);
    try {
      const callbackUri = `${window.location.origin}/api/github/callback`;
      const data = await authFetch(
        `${Routes.AUTH}${ApiPaths.GITHUB_CONNECT}?redirect_uri=${encodeURIComponent(callbackUri)}`
      );
      window.location.href = data.oauth_url;
    } catch {
      setGithubLoading(false);
    }
  }

  async function handleGithubDisconnect() {
    await authFetch(`${Routes.AUTH}${ApiPaths.PROFILE_GITHUB}`, {
      method: Methods.POST,
      body: JSON.stringify({ github_url: "" }),
    }).catch(() => null);
    setProfile((prev) => prev ? { ...prev, github_url: "", github_username: "" } : prev);
  }

  function handleFileChange(file: File | null) {
    if (!file) return;
    const allowed = ["application/pdf", "text/plain"];
    if (!allowed.includes(file.type)) return;
    if (file.size > 10 * 1024 * 1024) return;
    setSelectedFile(file);
  }

  async function handleResumeUpload() {
    if (!selectedFile) return;
    setResumeUploading(true);
    try {
      const formData = new FormData();
      formData.append("resume_file", selectedFile);
      const updated = await authFetch(`${Routes.AUTH}${ApiPaths.PROFILE_RESUME}`, {
        method: Methods.POST,
        body: formData,
      });
      setProfile((prev) => prev ? { ...prev, resume_file: updated.resume_file ?? prev.resume_file } : prev);
      setSelectedFile(null);
    } catch {
      // 업로드 실패 시 조용히 무시
    } finally {
      setResumeUploading(false);
    }
  }

  async function handleResumeDelete() {
    await authFetch(`${Routes.AUTH}${ApiPaths.PROFILE_RESUME}`, {
      method: Methods.DELETE,
    }).catch(() => null);
    setProfile((prev) => prev ? { ...prev, resume_file: null } : prev);
    setSelectedFile(null);
  }

  return (
    <div className="bg-[#f5f6f8] min-h-screen px-6 py-8">
      <div className="mx-auto max-w-[1380px]">
      <div style={{ background: "#fff", borderRadius: 28, border: "1px solid #e8eaed", overflow: "hidden" }}>

        {/* 히어로는 카드 안에 바로, 나머지는 패딩 영역 안에 */}
        <div style={{ display: "grid", gap: 20, padding: "0 0 28px" }}>

        {/* 히어로 */}
        <div style={{
          padding: 28, borderRadius: 26, border: "1px solid #ebecef",
          background: "radial-gradient(circle at top right,rgba(255,111,15,0.14),transparent 26%),linear-gradient(180deg,#fff7f2 0%,#ffffff 100%)",
        }}>
          <span style={{
            display: "inline-flex", alignItems: "center", padding: "4px 12px",
            borderRadius: 999, background: "#fff0e7", color: "#c2560c",
            fontSize: 13, fontWeight: 700, marginBottom: 16,
          }}>
            학생 프로필
          </span>

          <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 16, flexWrap: "wrap" }}>
            {/* 프로필 사진 */}
            {profileImage ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={profileImage} alt="프로필"
                style={{ width: 80, height: 80, borderRadius: "50%", objectFit: "cover", border: "3px solid #e2e5e9", flexShrink: 0 }}
              />
            ) : (
              <div style={{
                width: 80, height: 80, borderRadius: "50%",
                background: "#dbeafe", display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 32, fontWeight: 700,
                color: "#1d4ed8", border: "3px solid #e2e5e9", flexShrink: 0,
              }}>
                {name.slice(0, 1)}
              </div>
            )}
            <div>
              <h1 style={{ margin: "0 0 4px", fontSize: "clamp(28px,4vw,44px)", letterSpacing: "-0.04em" }}>
                {name}님의 분석 프로필
              </h1>
            </div>
          </div>

          {/* 메타 pills */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {me?.student_id && (
              <span style={{ display: "inline-flex", alignItems: "center", padding: "8px 12px", borderRadius: 999, background: "#f6f7f9", color: "#5f6672", fontSize: 14, fontWeight: 700 }}>
                학번 {me.student_id}
              </span>
            )}
            {me?.grade && (
              <span style={{ display: "inline-flex", alignItems: "center", padding: "8px 12px", borderRadius: 999, background: "#f6f7f9", color: "#5f6672", fontSize: 14, fontWeight: 700 }}>
                {me.grade}학년
              </span>
            )}
            {me?.class_group && (
              <span style={{ display: "inline-flex", alignItems: "center", padding: "8px 12px", borderRadius: 999, background: "#f6f7f9", color: "#5f6672", fontSize: 14, fontWeight: 700 }}>
                {me.class_group}반
              </span>
            )}
            {profile?.github_username && (
              <span style={{ display: "inline-flex", alignItems: "center", padding: "8px 12px", borderRadius: 999, background: "#f6f7f9", color: "#5f6672", fontSize: 14, fontWeight: 700 }}>
                GitHub @{profile.github_username}
              </span>
            )}
            <span style={{ display: "inline-flex", alignItems: "center", padding: "8px 12px", borderRadius: 999, background: "#f6f7f9", color: "#5f6672", fontSize: 14, fontWeight: 700 }}>
              마지막 분석{" "}
              {profile?.profile_analyzed_at
                ? new Date(profile.profile_analyzed_at).toLocaleString("ko-KR", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })
                : "Unknown"}
            </span>
          </div>
        </div>

        {/* 패널 그리드 */}
        <div style={{ display: "grid", gridTemplateColumns: "minmax(0,1.05fr) minmax(0,0.95fr)", gap: 18, alignItems: "start" }}>

          {/* GitHub 연동 */}
          <section style={{ padding: 24, border: "1px solid #ebecef", borderRadius: 22, background: "#fff" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 36, height: 36, borderRadius: 10, background: "#f0f0f0", flexShrink: 0 }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="#24292e">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
                </svg>
              </span>
              <h2 style={{ margin: 0, fontSize: 20, letterSpacing: "-0.03em" }}>GitHub 연동</h2>
            </div>
            <p style={{ margin: "0 0 18px", color: "#6b7280", lineHeight: 1.7 }}>
              GitHub를 연동하면 프로젝트 기반으로 맞춤 분석을 받을 수 있습니다.
            </p>
            {profileLoading ? (
              <p style={{ color: "#9ca3af", fontSize: 14 }}>불러오는 중...</p>
            ) : profile?.github_username ? (
              <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 14px", border: "1px solid #e2e5e9", borderRadius: 12, background: "#f9f9fb" }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#24292e">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
                </svg>
                <span style={{ fontWeight: 600 }}>@{profile.github_username}</span>
                <button
                  onClick={handleGithubDisconnect}
                  style={{ marginLeft: "auto", fontSize: 13, color: "#c2410c", background: "none", border: "none", cursor: "pointer", fontWeight: 600 }}
                >
                  연동 해제
                </button>
              </div>
            ) : (
              <button
                onClick={handleGithubConnect}
                disabled={githubLoading}
                style={{
                  display: "inline-flex", alignItems: "center", gap: 8,
                  padding: "12px 16px", border: "1px solid #e2e5e9", borderRadius: 12,
                  background: "#fff", color: "#333", fontSize: 14, fontWeight: 600,
                  cursor: githubLoading ? "not-allowed" : "pointer", opacity: githubLoading ? 0.5 : 1,
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#24292e">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
                </svg>
                {githubLoading ? "이동 중..." : "GitHub 연동하기"}
              </button>
            )}
          </section>

          {/* 이력서 등록 */}
          <section style={{ padding: 24, border: "1px solid #ebecef", borderRadius: 22, background: "#fff" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 36, height: 36, borderRadius: 10, background: "#fff7f2", flexShrink: 0 }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff6f0f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
              </span>
              <h2 style={{ margin: 0, fontSize: 20, letterSpacing: "-0.03em" }}>이력서 등록</h2>
            </div>
            <p style={{ margin: "0 0 18px", color: "#6b7280", lineHeight: 1.7 }}>
              PDF 또는 텍스트 파일을 업로드하면 AI가 분석해드립니다.
            </p>

            {profile?.resume_file && !selectedFile ? (
              /* 등록된 이력서 상태 */
              <div style={{ border: "1px solid #e2e5e9", borderRadius: 14, overflow: "hidden" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "14px 16px", background: "#f9f9fb" }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff6f0f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
                  </svg>
                  <span style={{ fontSize: 14, fontWeight: 600, color: "#39404a", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {profile.resume_file}
                  </span>
                </div>
                <div style={{ display: "flex", borderTop: "1px solid #e2e5e9" }}>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    style={{ flex: 1, padding: "10px 0", background: "none", border: "none", fontSize: 13, fontWeight: 600, color: "#5f6672", cursor: "pointer" }}
                  >
                    수정
                  </button>
                  <div style={{ width: 1, background: "#e2e5e9" }} />
                  <button
                    onClick={handleResumeDelete}
                    style={{ flex: 1, padding: "10px 0", background: "none", border: "none", fontSize: 13, fontWeight: 600, color: "#c2410c", cursor: "pointer" }}
                  >
                    삭제
                  </button>
                </div>
              </div>
            ) : (
              /* 드롭존 */
              <>
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFileChange(e.dataTransfer.files[0] ?? null); }}
                  style={{
                    border: `2px dashed ${dragOver ? "#ff6f0f" : "#dfe3ea"}`,
                    borderRadius: 14, padding: "24px 16px",
                    textAlign: "center", cursor: "pointer",
                    background: dragOver ? "#fff7f2" : "#fafafa",
                    transition: "border-color 0.15s, background 0.15s",
                  }}
                >
                  {selectedFile ? (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff6f0f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
                      </svg>
                      <span style={{ fontSize: 14, fontWeight: 600, color: "#39404a" }}>{selectedFile.name}</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                        style={{ marginLeft: 4, fontSize: 13, color: "#c2410c", background: "none", border: "none", cursor: "pointer", fontWeight: 600 }}
                      >
                        제거
                      </button>
                    </div>
                  ) : (
                    <>
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: "0 auto 8px" }}>
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                      <p style={{ margin: "0 0 4px", fontSize: 14, fontWeight: 600, color: "#39404a" }}>
                        파일을 여기에 드래그하거나 클릭해서 선택
                      </p>
                      <p style={{ margin: 0, fontSize: 12, color: "#9ca3af" }}>PDF 또는 TXT · 최대 10MB</p>
                    </>
                  )}
                </div>
                {selectedFile && (
                  <button
                    onClick={handleResumeUpload}
                    disabled={resumeUploading}
                    style={{
                      marginTop: 12, width: "100%", padding: "11px 16px",
                      border: "none", borderRadius: 12,
                      background: resumeUploading ? "#e5e7eb" : "#ff6f0f",
                      color: resumeUploading ? "#9ca3af" : "#fff",
                      fontSize: 14, fontWeight: 700,
                      cursor: resumeUploading ? "not-allowed" : "pointer",
                    }}
                  >
                    {resumeUploading ? "업로드 중..." : "업로드"}
                  </button>
                )}
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt"
              style={{ display: "none" }}
              onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
            />
          </section>
        </div>

        {/* AI 분석 결과 */}
        <section style={{ padding: 24, border: "1px solid #ebecef", borderRadius: 22, background: "#fff" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 36, height: 36, borderRadius: 10, background: "#f0f7ff", flexShrink: 0 }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </span>
            <h2 style={{ margin: 0, fontSize: 20, letterSpacing: "-0.03em" }}>저장된 분석 결과</h2>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
            {profile?.remaining_analysis_count !== undefined && (
              <p style={{ margin: 0, color: "#6b7280", fontSize: 13 }}>
                오늘 남은 횟수 {profile.remaining_analysis_count}회
              </p>
            )}
            {(() => {
              const canAnalyze = !!(profile?.github_username && profile?.resume_file);
              return (
                <button
                  disabled={!canAnalyze}
                  style={{
                    marginLeft: "auto", display: "inline-flex", alignItems: "center", gap: 6,
                    padding: "9px 16px", border: "none", borderRadius: 10,
                    background: canAnalyze ? "#ff6f0f" : "#e5e7eb",
                    color: canAnalyze ? "#fff" : "#9ca3af",
                    fontSize: 13, fontWeight: 700,
                    cursor: canAnalyze ? "pointer" : "not-allowed",
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  {canAnalyze ? "AI 분석하기" : "GitHub + 이력서 등록 후 분석 가능"}
                </button>
              );
            })()}
          </div>
          {profile?.profile_analyzed_at ? (
            <div style={{ display: "grid", gap: 16 }}>
              {profile.ai_profile_summary && (
                <article style={{ padding: 18, borderRadius: 18, background: "#fbfbfc", border: "1px solid #eef0f3" }}>
                  <h3 style={{ margin: "0 0 10px", fontSize: 17, letterSpacing: "-0.02em" }}>AI 요약</h3>
                  <p style={{ margin: 0, color: "#39404a", lineHeight: 1.7 }}>{profile.ai_profile_summary}</p>
                </article>
              )}
              {profile.github_profile_summary && (
                <article style={{ padding: 18, borderRadius: 18, background: "#fbfbfc", border: "1px solid #eef0f3" }}>
                  <h3 style={{ margin: "0 0 10px", fontSize: 17, letterSpacing: "-0.02em" }}>GitHub 분석</h3>
                  <p style={{ margin: 0, color: "#39404a", lineHeight: 1.7 }}>{profile.github_profile_summary}</p>
                </article>
              )}
              {profile.resume_analysis_summary && (
                <article style={{ padding: 18, borderRadius: 18, background: "#fbfbfc", border: "1px solid #eef0f3" }}>
                  <h3 style={{ margin: "0 0 10px", fontSize: 17, letterSpacing: "-0.02em" }}>이력서 분석</h3>
                  <p style={{ margin: 0, color: "#39404a", lineHeight: 1.7 }}>{profile.resume_analysis_summary}</p>
                </article>
              )}
            </div>
          ) : (
            <p style={{ color: "#6b7280", lineHeight: 1.7 }}>
              GitHub 또는 이력서를 등록하면 AI 분석 결과가 여기에 표시됩니다.
            </p>
          )}
        </section>

        </div>
      </div>
      </div>
    </div>
  );
}
