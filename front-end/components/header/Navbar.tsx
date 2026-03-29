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
      className={`
        fixed inset-0 z-40 flex flex-col items-stretch gap-[30px] overflow-y-auto
        bg-[#f3f3f5] px-[26px] pb-8 pt-[90px]
        transition-[transform,opacity] duration-[220ms] ease-[ease]
        lg:static lg:flex-row lg:flex-wrap lg:items-center lg:gap-[30px]
        lg:overflow-visible lg:bg-transparent lg:p-0
        lg:translate-y-0 lg:opacity-100 lg:pointer-events-auto
        ${isOpen
          ? "translate-y-0 opacity-100 pointer-events-auto"
          : "-translate-y-2 opacity-0 pointer-events-none"
        }
      `}
    >
      {NAV_LINKS.map(({ href, label }) => {
        const active = pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onClose}
            className={`
              rounded-lg px-[10px] py-[7px] text-[15px] font-semibold
              transition-[color,background-color] duration-200
              lg:text-[15px]
              ${active
                ? "bg-[#fff1e8] text-[#ff6f0f]"
                : "text-[#868b94] hover:bg-[#f1f2f4] hover:text-[#212124]"
              }
              max-lg:rounded-none max-lg:px-0 max-lg:py-[3px]
              max-lg:text-[clamp(38px,9vw,55px)] max-lg:font-black
              max-lg:leading-[1.07] max-lg:tracking-[-0.045em]
              max-lg:text-[#1f2124] max-lg:bg-transparent
              ${active ? "max-lg:text-[#ff6f0f]" : ""}
            `}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
