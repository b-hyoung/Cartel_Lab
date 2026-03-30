export default function AttendancePage() {
  return (
    <div className="min-h-screen bg-[#f5f6fa]">
      {/* 히어로 배경 */}
      <div className="relative overflow-hidden bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f3460] px-6 py-16 text-white">
        {/* 배경 장식 */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-10 -right-10 h-64 w-64 rounded-full bg-brand/10 blur-3xl" />
          <div className="absolute bottom-0 left-10 h-48 w-48 rounded-full bg-blue-500/10 blur-2xl" />
        </div>

        <div className="relative mx-auto max-w-[1380px]">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">🗓️</span>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold tracking-wide text-white/70">
              ATTENDANCE
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mb-2">출결 관리</h1>
          <p className="text-white/50 text-sm">출결 현황을 확인하고 관리하세요</p>
        </div>
      </div>

      {/* 준비 중 안내 */}
      <div className="mx-auto max-w-[1380px] px-6 py-16 flex flex-col items-center justify-center gap-4">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white shadow-sm text-4xl">
          🚧
        </div>
        <p className="text-[#868b94] text-sm font-medium">페이지 준비 중입니다</p>
      </div>
    </div>
  );
}
