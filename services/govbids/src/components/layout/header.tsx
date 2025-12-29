"use client";

import { UserButton } from "@/components/auth/user-button";
import { MobileNav } from "./mobile-nav";

export function Header() {
  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-background px-4 lg:px-6">
      <MobileNav />
      <div className="flex-1" />
      <UserButton />
    </header>
  );
}
