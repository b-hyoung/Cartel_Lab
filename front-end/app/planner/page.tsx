export default function PlannerPage() {
  return (
    <div
      style={{
        minHeight: "60vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "12px",
        color: "#868b94",
      }}
    >
      <span style={{ fontSize: "40px" }}>🚧</span>
      <p style={{ fontSize: "18px", fontWeight: 700, color: "#505762" }}>
        준비중입니다...
      </p>
      <p style={{ fontSize: "14px" }}>곧 서비스가 오픈될 예정입니다.</p>
    </div>
  );
}
