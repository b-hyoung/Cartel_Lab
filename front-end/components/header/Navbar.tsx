"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_LINKS } from "@/constants/navigation";

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export default function Navbar({ isOpen, onClose }: Props) {
  const pathname = usePathname();

  return (
    <nav
      className={`fixed inset-0 z-40 flex flex-col gap-8 bg-[#f3f3f5] px-6 pt-24 transition-all duration-200
        lg:static lg:flex-row lg:items-center lg:gap-8 lg:bg-transparent lg:p-0 lg:opacity-100
        ${isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none lg:opacity-100 lg:pointer-events-auto"}`}
    >
      {NAV_LINKS.map(({ href, label }) => {
        const active = pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onClose}
            className={`rounded-lg px-2.5 py-1.5 text-[15px] font-semibold transition-colors
              ${active
                ? "bg-orange-50 text-orange-500"
                : "text-gray-500 hover:bg-gray-100 hover:text-gray-900"
              }`}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
