"use client";

import { useCallback, useEffect, useState } from "react";
import { CONTEST_CATEGORY_OPTIONS } from "@/constants/contests";
import { dbFetch } from "@/lib/api-client";
import type { ContestCategoryOption } from "./_filter-section";
import type { ContestItem } from "./_contest-list-section";
import { pageShellStyle } from "./_styles";
import { HeroSection } from "./_hero-section";
import { FilterSection } from "./_filter-section";
import { ContestListSection } from "./_contest-list-section";

type ContestPageData = {
  generated_at: string;
  current_category: string;
  categories: Array<{
    label: string;
    value: string;
  }>;
  items: ContestItem[];
};

export default function ContestsPage() {
  const [data, setData] = useState<ContestPageData | null>(null);
  const [currentCategory, setCurrentCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await dbFetch("/contests/");
      setData(response);
      setCurrentCategory(response.current_category ?? "");
    } catch (fetchError) {
      console.error(fetchError);
      setError("공모전 목록을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const items = data?.items ?? [];
  const filteredItems = currentCategory ? items.filter((item) => item.category === currentCategory) : items;

  const categories: ContestCategoryOption[] = (data?.categories ?? CONTEST_CATEGORY_OPTIONS).map((category) => ({
    ...category,
    count: category.value ? items.filter((item) => item.category === category.value).length : items.length,
  }));

  const urgentCount = filteredItems.filter((item) => item.d_day !== null && item.d_day <= 7).length;
  const alwaysOpenCount = filteredItems.filter((item) => item.d_day === null).length;
  const earliestItem = filteredItems.find((item) => item.d_day !== null) ?? filteredItems[0] ?? null;
  const earliestDeadlineLabel = earliestItem
    ? earliestItem.d_day_label === "상시"
      ? "상시 모집"
      : earliestItem.d_day_label
    : "-";
  const activeCategoryLabel =
    categories.find((category) => category.value === currentCategory)?.label ?? "전체";

  return (
    <div style={pageShellStyle}>
      <HeroSection
        categoryLabel={activeCategoryLabel}
        totalCount={filteredItems.length}
        urgentCount={urgentCount}
        earliestDeadlineLabel={earliestDeadlineLabel}
        alwaysOpenCount={alwaysOpenCount}
        generatedAt={data?.generated_at ?? null}
      />
      <FilterSection
        categories={categories}
        currentCategory={currentCategory}
        onSelectCategory={setCurrentCategory}
      />
      <ContestListSection
        items={filteredItems}
        loading={loading}
        error={error}
        activeCategoryLabel={activeCategoryLabel}
        onRetry={fetchData}
      />
    </div>
  );
}
