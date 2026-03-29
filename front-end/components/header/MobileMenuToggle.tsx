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
      className="fixed right-[14px] top-[12px] z-[60] flex h-[44px] w-[44px] flex-col items-center justify-center gap-[5px] border-none bg-transparent lg:hidden"
    >
      <span
        className={`block h-[2.5px] w-6 rounded-sm bg-[#3a3a3c] transition-transform duration-200 ${
          isOpen ? "translate-y-[5px] rotate-45" : ""
        }`}
      />
      <span
        className={`block h-[2.5px] w-6 rounded-sm bg-[#3a3a3c] transition-opacity duration-200 ${
          isOpen ? "opacity-0" : ""
        }`}
      />
      <span
        className={`block h-[2.5px] w-6 rounded-sm bg-[#3a3a3c] transition-transform duration-200 ${
          isOpen ? "-translate-y-[5px] -rotate-45" : ""
        }`}
      />
    </button>
  );
}
