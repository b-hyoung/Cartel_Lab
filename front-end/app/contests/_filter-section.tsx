import { sectionCardStyle } from "./_styles";

export type ContestCategoryOption = {
  label: string;
  value: string;
  count: number;
};

type FilterSectionProps = {
  categories: ContestCategoryOption[];
  currentCategory: string;
  onSelectCategory: (value: string) => void;
};

export function FilterSection({
  categories,
  currentCategory,
  onSelectCategory,
}: FilterSectionProps) {
  return (
    <section className="px-6 pt-5">
      <div className="mx-auto max-w-[1380px] px-5 py-5 md:px-6" style={sectionCardStyle}>
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-1">
            <h2 className="text-[22px] font-extrabold tracking-[-0.03em] text-[#212124]">카테고리 필터</h2>
            <p className="text-[14px] text-[#6e7681]">운영 템플릿 분류 기준과 동일하게 공모전을 모아봤습니다.</p>
          </div>
          <p className="text-[13px] text-[#8a9098]">카테고리를 바꾸면 현재 표시 중인 목록만 즉시 갱신됩니다.</p>
        </div>

        <div className="mt-5 flex gap-2 overflow-x-auto pb-1">
          {categories.map((category) => {
            const isActive = currentCategory === category.value;

            return (
              <button
                key={`${category.label}-${category.value}`}
                type="button"
                onClick={() => onSelectCategory(category.value)}
                className="inline-flex shrink-0 items-center gap-2 rounded-full border px-4 py-2.5 text-[14px] font-semibold tracking-[-0.02em] transition-colors"
                style={{
                  borderColor: isActive ? "#ff6f0f" : "#e5e7eb",
                  background: isActive ? "#fff1e8" : "#ffffff",
                  color: isActive ? "#c2560c" : "#4b5563",
                }}
              >
                <span>{category.label}</span>
                <span
                  className="rounded-full px-2 py-0.5 text-[12px]"
                  style={{
                    background: isActive ? "#ffd9bf" : "#f3f4f6",
                    color: isActive ? "#b45309" : "#6b7280",
                  }}
                >
                  {category.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
