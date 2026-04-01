"use client";

import { useState } from "react";
import { DASHBOARD_PALETTE } from "@/constants/colors";
import type { JobCategory, JobPosting } from "@/types/jobs";
import { filterChipStyle, ghostButtonStyle, primaryButtonStyle, sectionCardStyle } from "./_styles";

const PALETTE = DASHBOARD_PALETTE;

export function JobsListSection({
  jobs,
  categories,
  loading,
  error,
  scoringEnabled,
  onRetry,
  onSelect,
}: {
  jobs: JobPosting[];
  categories: JobCategory[];
  loading: boolean;
  error: string | null;
  scoringEnabled: boolean;
  onRetry: () => void;
  onSelect: (job: JobPosting) => void;
}) {
  const [selectedCategory, setSelectedCategory] = useState("all");

  const filteredJobs =
    selectedCategory === "all"
      ? jobs
      : jobs.filter((job) =>
          job.ui_categories.includes(selectedCategory) || job.job_role === selectedCategory,
        );

  return (
    <section className="grid gap-5">
      <div
        style={{
          ...sectionCardStyle,
          padding: 28,
          background:
            "radial-gradient(circle at top right, rgba(255,111,15,0.12), transparent 28%), linear-gradient(180deg, rgba(255,247,242,1) 0%, rgba(255,255,255,1) 58%)",
        }}
      >
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)] lg:items-end">
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 12px",
                borderRadius: 999,
                background: PALETTE.surface,
                border: `1px solid ${PALETTE.brandSoftStrong}`,
                color: PALETTE.brandText,
                fontSize: 12,
                fontWeight: 800,
                marginBottom: 14,
              }}
            >
              JOB DISCOVERY
            </div>
            <h1
              style={{
                margin: 0,
                fontSize: "clamp(32px, 4vw, 48px)",
                lineHeight: 1.06,
                letterSpacing: "-0.05em",
                fontWeight: 900,
                color: PALETTE.ink,
              }}
            >
              학생이 바로 지원할 수 있는 채용 정보를 빠르게 고르는 화면
            </h1>
            <p
              style={{
                margin: "14px 0 0",
                maxWidth: 720,
                fontSize: 15,
                lineHeight: 1.75,
                color: PALETTE.body,
              }}
            >
              공고를 기술 스택과 직무 기준으로 정리했습니다. 카테고리만 빠르게 좁히고, 카드에서 핵심만 확인한 뒤 상세에서 바로 지원 링크까지 이어집니다.
            </p>
          </div>

          <div
            style={{
              borderRadius: 22,
              background: PALETTE.surface,
              border: `1px solid ${PALETTE.line}`,
              padding: 18,
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 800, color: PALETTE.muted, marginBottom: 8 }}>
              현재 상태
            </div>
            <div style={{ fontSize: 22, fontWeight: 900, letterSpacing: "-0.04em", color: PALETTE.ink }}>
              총 {jobs.length}개 공고
            </div>
            <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: PALETTE.body }}>
              {scoringEnabled
                ? "로그인 상태에서는 추천 점수를 함께 확인할 수 있습니다."
                : "비로그인 상태에서는 공고 목록만 먼저 볼 수 있습니다."}
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={() => setSelectedCategory("all")}
          style={{
            ...filterChipStyle,
            border: `1px solid ${selectedCategory === "all" ? PALETTE.brand : PALETTE.line}`,
            background: selectedCategory === "all" ? PALETTE.brandSoft : PALETTE.surface,
            color: selectedCategory === "all" ? PALETTE.brandText : PALETTE.body,
          }}
        >
          전체
        </button>
        {categories.map((category) => {
          const active = selectedCategory === category.key;
          return (
            <button
              key={category.key}
              onClick={() => setSelectedCategory(category.key)}
              style={{
                ...filterChipStyle,
                border: `1px solid ${active ? PALETTE.brand : PALETTE.line}`,
                background: active ? PALETTE.brandSoft : PALETTE.surface,
                color: active ? PALETTE.brandText : PALETTE.body,
              }}
            >
              {category.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div style={{ ...sectionCardStyle, padding: 32, textAlign: "center", color: PALETTE.muted }}>
          채용 정보를 불러오는 중입니다.
        </div>
      ) : error ? (
        <div style={{ ...sectionCardStyle, padding: 28 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: PALETTE.ink }}>공고를 불러오지 못했습니다.</div>
          <p style={{ margin: "8px 0 16px", fontSize: 14, color: PALETTE.body }}>{error}</p>
          <button onClick={onRetry} style={primaryButtonStyle}>
            다시 불러오기
          </button>
        </div>
      ) : filteredJobs.length === 0 ? (
        <div style={{ ...sectionCardStyle, padding: 32 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: PALETTE.ink }}>조건에 맞는 공고가 없습니다.</div>
          <p style={{ margin: "8px 0 0", fontSize: 14, color: PALETTE.body }}>
            다른 카테고리를 선택해서 다시 확인해 보세요.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {filteredJobs.map((job) => (
            <button
              key={job.id}
              onClick={() => onSelect(job)}
              style={{
                ...sectionCardStyle,
                padding: 22,
                textAlign: "left",
                display: "grid",
                gap: 18,
                background: PALETTE.surface,
                cursor: "pointer",
              }}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 42,
                        height: 42,
                        borderRadius: 14,
                        background: PALETTE.surfaceTint,
                        color: PALETTE.brandText,
                        fontSize: 14,
                        fontWeight: 900,
                        flexShrink: 0,
                      }}
                    >
                      {job.ui_company_mark || job.company_name.slice(0, 2)}
                    </span>
                    <div className="min-w-0">
                      <div style={{ fontSize: 13, fontWeight: 700, color: PALETTE.muted }}>
                        {job.company_name}
                      </div>
                      <div
                        style={{
                          marginTop: 4,
                          fontSize: 24,
                          lineHeight: 1.12,
                          letterSpacing: "-0.04em",
                          fontWeight: 900,
                          color: PALETTE.ink,
                        }}
                      >
                        {job.title}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                  {job.ui_deadline_label && (
                    <span
                      style={{
                        borderRadius: 999,
                        background: PALETTE.warningSoft,
                        color: "#b45309",
                        padding: "6px 10px",
                        fontSize: 12,
                        fontWeight: 800,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {job.ui_deadline_label}
                    </span>
                  )}
                  {scoringEnabled && job.ui_recommendation_score !== null && (
                    <span
                      style={{
                        borderRadius: 999,
                        background: PALETTE.brandSoft,
                        color: PALETTE.brandText,
                        padding: "6px 10px",
                        fontSize: 12,
                        fontWeight: 800,
                        whiteSpace: "nowrap",
                      }}
                    >
                      매칭도 {job.ui_recommendation_score}점
                    </span>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {[job.location, job.employment_type, job.experience_label].filter(Boolean).map((item) => (
                  <span
                    key={`${job.id}-${item}`}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      borderRadius: 999,
                      background: PALETTE.surfaceSubtle,
                      color: PALETTE.body,
                      padding: "7px 12px",
                      fontSize: 12,
                      fontWeight: 700,
                    }}
                  >
                    {item}
                  </span>
                ))}
                {job.is_junior_friendly && (
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      borderRadius: 999,
                      background: PALETTE.successSoft,
                      color: PALETTE.success,
                      padding: "7px 12px",
                      fontSize: 12,
                      fontWeight: 800,
                    }}
                  >
                    신입 우대
                  </span>
                )}
              </div>

              <div style={{ fontSize: 14, lineHeight: 1.8, color: PALETTE.body }}>
                {job.ui_main_tasks.length > 0 ? job.ui_main_tasks.slice(0, 2).join(" · ") : job.required_skills}
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {job.ui_tags.map((tag) => (
                  <span
                    key={`${job.id}-${tag}`}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      borderRadius: 999,
                      background: PALETTE.surface,
                      border: `1px solid ${PALETTE.line}`,
                      color: PALETTE.muted,
                      padding: "6px 10px",
                      fontSize: 12,
                      fontWeight: 700,
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between gap-4">
                <div style={{ fontSize: 13, color: PALETTE.muted }}>
                  {job.ui_recommendation_reasons[0] && scoringEnabled
                    ? job.ui_recommendation_reasons[0]
                    : `출처 ${job.source}`}
                </div>
                <span style={{ ...ghostButtonStyle, padding: "9px 14px", color: PALETTE.ink }}>
                  자세히 보기
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
