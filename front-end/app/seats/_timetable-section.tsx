"use client";

import * as React from "react";

import { modalCardStyle, modalOverlayStyle, neutralBadgeStyle, timetableTableStyle } from "./_styles";

type SeatTimetableSectionProps = {
  classGroup: string | null | undefined;
  open: boolean;
  onClose: () => void;
};

type TimetableRow = {
  period: string;
  monday: string;
  tuesday: string;
  wednesday: string;
  thursday: string;
  friday: string;
};

const timetableA: TimetableRow[] = [
  { period: "1 (09:00 ~ 09:50)", monday: "-", tuesday: "-", wednesday: "-", thursday: "-", friday: "-" },
  { period: "2 (10:00 ~ 10:50)", monday: "데이터베이스\n한종진 / 2411", tuesday: "데이터베이스\n한종진 / 2411", wednesday: "객체지향프로그래밍\n이훈주 / 2411", thursday: "AI프롬프트엔지니어링\n최미란 / 2411", friday: "객체지향프로그래밍\n이훈주 / 2411" },
  { period: "3 (11:00 ~ 11:50)", monday: "데이터베이스\n한종진 / 2411", tuesday: "데이터베이스\n한종진 / 2411", wednesday: "객체지향프로그래밍\n이훈주 / 2411", thursday: "AI프롬프트엔지니어링\n최미란 / 2411", friday: "객체지향프로그래밍\n이훈주 / 2411" },
  { period: "4 (12:00 ~ 12:50)", monday: "-", tuesday: "-", wednesday: "-", thursday: "AI프롬프트엔지니어링\n최미란 / 2411", friday: "-" },
  { period: "5 (13:00 ~ 13:50)", monday: "디지털포렌식\n이성원 / 2408", tuesday: "해킹 및 침해대응\n이성원 / 2412", wednesday: "캡스톤디자인\n장진수 / 2412", thursday: "-", friday: "-" },
  { period: "6 (14:00 ~ 14:50)", monday: "디지털포렌식\n이성원 / 2408", tuesday: "해킹 및 침해대응\n이성원 / 2412", wednesday: "캡스톤디자인\n장진수 / 2412", thursday: "-", friday: "-" },
  { period: "7 (15:00 ~ 15:50)", monday: "디지털포렌식\n이성원 / 2408", tuesday: "해킹 및 침해대응\n이성원 / 2412", wednesday: "-", thursday: "취업과창업\n최미란 / 2408", friday: "-" },
  { period: "8 (16:00 ~ 16:50)", monday: "-", tuesday: "함께하는 여행\n박한규 / 2409", wednesday: "-", thursday: "취업과창업\n최미란 / 2408", friday: "-" },
];

const timetableB: TimetableRow[] = [
  { period: "1 (09:00 ~ 09:50)", monday: "-", tuesday: "-", wednesday: "-", thursday: "-", friday: "-" },
  { period: "2 (10:00 ~ 10:50)", monday: "AI프롬프트엔지니어링\n최미란 / 2408", tuesday: "모바일프로그래밍\n최대림 / 2408", wednesday: "JAVA프로그래밍 실무\n권숙연 / 2408", thursday: "-", friday: "웹프로그래밍 실무\n김석진 / 2408" },
  { period: "3 (11:00 ~ 11:50)", monday: "AI프롬프트엔지니어링\n최미란 / 2408", tuesday: "모바일프로그래밍\n최대림 / 2408", wednesday: "JAVA프로그래밍 실무\n권숙연 / 2408", thursday: "-", friday: "웹프로그래밍 실무\n김석진 / 2408" },
  { period: "4 (12:00 ~ 12:50)", monday: "AI프롬프트엔지니어링\n최미란 / 2408", tuesday: "모바일프로그래밍\n최대림 / 2408", wednesday: "-", thursday: "-", friday: "웹프로그래밍 실무\n김석진 / 2408" },
  { period: "5 (13:00 ~ 13:50)", monday: "-", tuesday: "-", wednesday: "캡스톤디자인\n권숙연 / 2412", thursday: "JAVA프로그래밍 실무\n권숙연 / 2408", friday: "-" },
  { period: "6 (14:00 ~ 14:50)", monday: "-", tuesday: "데이터베이스\n한종진 / 2411", wednesday: "캡스톤디자인\n권숙연 / 2412", thursday: "JAVA프로그래밍 실무\n권숙연 / 2408", friday: "-" },
  { period: "7 (15:00 ~ 15:50)", monday: "데이터베이스\n한종진 / 2411", tuesday: "데이터베이스\n한종진 / 2411", wednesday: "-", thursday: "취업과창업\n최미란 / 2408", friday: "-" },
  { period: "8 (16:00 ~ 16:50)", monday: "데이터베이스\n한종진 / 2411", tuesday: "함께하는 여행\n박한규 / 2409", wednesday: "-", thursday: "취업과창업\n최미란 / 2408", friday: "-" },
];

export function SeatTimetableSection({ classGroup, open, onClose }: SeatTimetableSectionProps) {
  if (!open) return null;

  const modalTitle =
    classGroup === "A"
      ? "2학년 A반 강의시간표 (2026학년 1학기)"
      : classGroup === "B"
        ? "2학년 B반 강의시간표 (2026학년 1학기)"
        : "강의시간표";
  const cards =
    classGroup === "A"
      ? [<TimetableCard key="A" title="A반 시간표" rows={timetableA} accent="orange" />]
      : classGroup === "B"
        ? [<TimetableCard key="B" title="B반 시간표" rows={timetableB} accent="green" />]
        : [
            <TimetableCard key="A" title="A반 시간표" rows={timetableA} accent="orange" />,
            <TimetableCard key="B" title="B반 시간표" rows={timetableB} accent="green" />,
          ];

  return (
    <div style={modalOverlayStyle} onClick={onClose}>
      <div style={modalCardStyle} onClick={(event) => event.stopPropagation()}>
        <div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-[#eceef2] bg-white/95 px-6 py-5 backdrop-blur sm:px-8">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span style={neutralBadgeStyle}>시간표 확인</span>
              {classGroup ? <span style={neutralBadgeStyle}>{classGroup}반</span> : null}
            </div>
            <h3 className="text-[26px] font-[800] tracking-[-0.04em] text-[#212124]">{modalTitle}</h3>
            {classGroup ? null : (
              <p className="mt-1 text-sm text-[#6b7280]">
                반 정보가 없어도 전체 시간표는 볼 수 있습니다. 반을 설정하면 해당 반 시간표를 먼저 보여드립니다.
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[#dde2e8] bg-white text-lg font-bold text-[#57606a]"
            aria-label="시간표 닫기"
          >
            ×
          </button>
        </div>

        <div className="space-y-8 px-6 py-6 sm:px-8 sm:py-8">
          {cards}
        </div>
      </div>
    </div>
  );
}

function TimetableCard({
  title,
  rows,
  accent,
}: {
  title: string;
  rows: TimetableRow[];
  accent: "orange" | "green";
}) {
  const accentStyle =
    accent === "orange"
      ? { borderColor: "#ff6f0f", background: "#fff7f1", color: "#9a3412" }
      : { borderColor: "#22a06b", background: "#effaf5", color: "#166534" };

  return (
    <section className="rounded-[24px] border border-[#eceff3] bg-[#fcfcfd] p-4 sm:p-5">
      <div className="mb-4 flex items-center gap-3">
        <span className="h-7 w-1.5 rounded-full" style={{ background: accentStyle.borderColor }} />
        <h4 className="text-[20px] font-[800] tracking-[-0.03em]" style={{ color: accentStyle.color }}>
          {title}
        </h4>
      </div>

      <div className="overflow-x-auto rounded-[20px] border border-[#e6e9ee] bg-white">
        <table style={timetableTableStyle}>
          <thead>
            <tr>
              <HeaderCell style={accentStyle}>교시</HeaderCell>
              <HeaderCell style={accentStyle}>월</HeaderCell>
              <HeaderCell style={accentStyle}>화</HeaderCell>
              <HeaderCell style={accentStyle}>수</HeaderCell>
              <HeaderCell style={accentStyle}>목</HeaderCell>
              <HeaderCell style={accentStyle}>금</HeaderCell>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.period}>
                <BodyCell muted>{row.period}</BodyCell>
                <CourseCell value={row.monday} accent={accent} />
                <CourseCell value={row.tuesday} accent={accent} />
                <CourseCell value={row.wednesday} accent={accent} />
                <CourseCell value={row.thursday} accent={accent} />
                <CourseCell value={row.friday} accent={accent} />
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function HeaderCell({
  children,
  style,
}: {
  children: React.ReactNode;
  style: { borderColor: string; background: string; color: string };
}) {
  return (
    <th
      style={{
        border: "1px solid #e3e7ec",
        background: style.background,
        color: style.color,
        padding: "12px 10px",
        fontSize: 13,
        fontWeight: 800,
      }}
    >
      {children}
    </th>
  );
}

function BodyCell({ children, muted = false }: { children: React.ReactNode; muted?: boolean }) {
  return (
    <td
      style={{
        border: "1px solid #e3e7ec",
        padding: "12px 10px",
        textAlign: "center",
        verticalAlign: "middle",
        fontSize: 13,
        fontWeight: muted ? 700 : 600,
        color: muted ? "#667085" : "#2c3440",
        background: muted ? "#fafbfc" : "#ffffff",
        minWidth: muted ? 132 : 136,
      }}
    >
      {children}
    </td>
  );
}

function CourseCell({ value, accent }: { value: string; accent: "orange" | "green" }) {
  if (value === "-") {
    return <BodyCell muted={false}>-</BodyCell>;
  }

  const [course, detail] = value.split("\n");
  const background = accent === "orange" ? "#fff4ea" : "#effaf5";
  const color = accent === "orange" ? "#9a3412" : "#166534";

  return (
    <td
      style={{
        border: "1px solid #e3e7ec",
        padding: "12px 8px",
        textAlign: "center",
        verticalAlign: "middle",
        background,
        color,
        minWidth: 136,
      }}
    >
      <div className="text-[13px] font-[800] leading-5">{course}</div>
      <div className="mt-1 text-[11px] font-[700] opacity-80">{detail}</div>
    </td>
  );
}
