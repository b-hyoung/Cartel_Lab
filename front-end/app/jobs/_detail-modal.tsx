"use client";

import { useEffect, useState } from "react";
import { DASHBOARD_PALETTE } from "@/constants/colors";
import { useAuthFetch } from "@/lib/use-auth-fetch";
import type { JobDetail } from "@/types/jobs";
import { ghostButtonStyle, modalCardStyle, primaryButtonStyle } from "./_styles";

const PALETTE = DASHBOARD_PALETTE;

function DetailList({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;

  return (
    <section style={{ display: "grid", gap: 10 }}>
      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: PALETTE.ink }}>{title}</h3>
      <ul style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 8, color: PALETTE.body, lineHeight: 1.7 }}>
        {items.map((item) => (
          <li key={`${title}-${item}`}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export function JobDetailModal({
  jobId,
  onClose,
}: {
  jobId: number | null;
  onClose: () => void;
}) {
  const authFetch = useAuthFetch();
  const [detail, setDetail] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setDetail(null);

    authFetch(`/api/jobs/${jobId}/detail/?ai=0`)
      .then((data: JobDetail) => {
        if (!cancelled) setDetail(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "상세 정보를 불러오지 못했습니다.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [jobId, authFetch]);

  if (!jobId) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        background: PALETTE.overlay,
      }}
      onClick={onClose}
    >
      <div style={modalCardStyle} onClick={(e) => e.stopPropagation()}>
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 2,
            background: "rgba(255,255,255,0.95)",
            backdropFilter: "blur(10px)",
            borderBottom: `1px solid ${PALETTE.line}`,
            padding: "24px 24px 20px",
          }}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div style={{ fontSize: 12, fontWeight: 800, color: PALETTE.brandText, marginBottom: 8 }}>
                JOB DETAIL
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: PALETTE.muted }}>
                {detail?.company_name ?? "채용 정보"}
              </div>
              <h2
                style={{
                  margin: "6px 0 0",
                  fontSize: "clamp(28px, 4vw, 38px)",
                  lineHeight: 1.08,
                  letterSpacing: "-0.05em",
                  fontWeight: 900,
                  color: PALETTE.ink,
                }}
              >
                {detail?.title ?? "상세 정보를 불러오는 중"}
              </h2>
            </div>
            <button
              onClick={onClose}
              style={{
                ...ghostButtonStyle,
                width: 42,
                height: 42,
                padding: 0,
                flexShrink: 0,
                color: PALETTE.muted,
              }}
            >
              ×
            </button>
          </div>
        </div>

        <div style={{ padding: 24, display: "grid", gap: 22 }}>
          {loading ? (
            <div style={{ padding: "18px 0", fontSize: 14, color: PALETTE.muted }}>
              상세 정보를 불러오는 중입니다.
            </div>
          ) : error ? (
            <div style={{ display: "grid", gap: 12 }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: PALETTE.ink }}>
                상세 정보를 불러오지 못했습니다.
              </div>
              <div style={{ fontSize: 14, color: PALETTE.body }}>{error}</div>
            </div>
          ) : detail ? (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    borderRadius: 999,
                    background: PALETTE.surfaceTint,
                    color: PALETTE.brandText,
                    padding: "8px 12px",
                    fontSize: 12,
                    fontWeight: 800,
                  }}
                >
                  {detail.job_role}
                </span>
                {detail.recommendation_score !== null && (
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      borderRadius: 999,
                      background: PALETTE.brandSoft,
                      color: PALETTE.brandText,
                      padding: "8px 12px",
                      fontSize: 12,
                      fontWeight: 800,
                    }}
                  >
                    추천도 {detail.recommendation_score}점
                  </span>
                )}
              </div>

              {detail.overview && (
                <section style={{ display: "grid", gap: 10 }}>
                  <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: PALETTE.ink }}>공고 개요</h3>
                  <p style={{ margin: 0, fontSize: 14, lineHeight: 1.8, color: PALETTE.body }}>{detail.overview}</p>
                </section>
              )}

              {detail.required_skills.length > 0 && (
                <section style={{ display: "grid", gap: 10 }}>
                  <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: PALETTE.ink }}>필수 기술</h3>
                  <div className="flex flex-wrap gap-2">
                    {detail.required_skills.map((skill) => (
                      <span
                        key={skill}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          borderRadius: 999,
                          background: PALETTE.surfaceSubtle,
                          border: `1px solid ${PALETTE.line}`,
                          color: PALETTE.body,
                          padding: "7px 12px",
                          fontSize: 12,
                          fontWeight: 700,
                        }}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </section>
              )}

              <DetailList title="주요 업무" items={detail.main_tasks} />
              <DetailList title="자격 요건" items={detail.requirements} />
              <DetailList title="우대 사항" items={detail.preferred_points} />
              <DetailList title="복지 및 혜택" items={detail.benefits} />
              <DetailList title="추천 이유" items={detail.recommendation_reasons} />

              <div className="flex flex-wrap gap-3 pt-2">
                <a
                  href={detail.external_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ ...primaryButtonStyle, textDecoration: "none" }}
                >
                  공고 원문 보기
                </a>
                <button onClick={onClose} style={ghostButtonStyle}>
                  닫기
                </button>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
