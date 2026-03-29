"use client";

import Link from "next/link";
import { useState } from "react";
import Navbar from "./Navbar";
import MobileMenuToggle from "./MobileMenuToggle";
import UserDropdown from "./UserDropdown";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-20 border-b border-gray-100 bg-white/94 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1380px] items-center justify-between gap-4 px-6 py-3">
        <Link href="/" className="flex items-center gap-2.5 text-lg font-extrabold tracking-tight text-gray-900">
          <img
            src="/images/teamlab-logo.png"
            alt="Team Lab Logo"
            className="h-[34px] w-[34px] rounded-lg border border-gray-100 object-cover"
          />
          Jvision Lab
        </Link>

        <MobileMenuToggle isOpen={menuOpen} onToggle={() => setMenuOpen((v) => !v)} />

        <Navbar isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
        <UserDropdown />
      </div>
    </header>
  );
}
