"use client";

type Props = {
  isOpen: boolean;
  onToggle: () => void;
};

export default function MobileMenuToggle({ isOpen, onToggle }: Props) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label="메뉴 열기"
      aria-expanded={isOpen}
      className="flex h-10 w-10 flex-col items-center justify-center gap-1.5 rounded-lg border border-gray-200 bg-white lg:hidden" >
      <span
        className={`block h-0.5 w-4.5 rounded bg-gray-700 transition-transform ${isOpen ? "translate-y-2 rotate-45" : ""}`}
      />
      <span
        className={`block h-0.5 w-4.5 rounded bg-gray-700 transition-opacity ${isOpen ? "opacity-0" : ""}`}
      />
      <span
        className={`block h-0.5 w-4.5 rounded bg-gray-700 transition-transform ${isOpen ? "-translate-y-2 -rotate-45" : ""}`}
      />
    </button>
  );
}
