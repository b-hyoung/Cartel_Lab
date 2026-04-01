import { type CSSProperties } from "react";
import { DASHBOARD_PALETTE } from "@/constants/colors";

const PALETTE = DASHBOARD_PALETTE;

export const pagePanelStyle: CSSProperties = {
  background: PALETTE.surface,
  border: `1px solid ${PALETTE.line}`,
  borderRadius: 28,
  boxShadow: "0 1px 0 rgba(18, 18, 18, 0.02)",
};

export const sectionCardStyle: CSSProperties = {
  ...pagePanelStyle,
  borderRadius: 24,
  overflow: "hidden",
};

export const ghostButtonStyle: CSSProperties = {
  border: `1px solid ${PALETTE.line}`,
  borderRadius: 999,
  background: PALETTE.surface,
  color: PALETTE.body,
  padding: "10px 16px",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
};

export const primaryButtonStyle: CSSProperties = {
  border: "none",
  borderRadius: 999,
  background: PALETTE.brand,
  color: "#fff",
  padding: "11px 18px",
  fontSize: 13,
  fontWeight: 800,
  cursor: "pointer",
};

export const filterChipStyle: CSSProperties = {
  borderRadius: 999,
  padding: "9px 14px",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
};

export const modalCardStyle: CSSProperties = {
  width: "100%",
  maxWidth: 860,
  maxHeight: "min(88vh, 920px)",
  overflowY: "auto",
  background: PALETTE.surface,
  borderRadius: 28,
  border: `1px solid ${PALETTE.line}`,
  boxShadow: PALETTE.shadow,
};
