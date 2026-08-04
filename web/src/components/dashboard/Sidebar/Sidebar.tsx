"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import styles from "./Sidebar.module.css";

interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: string;
}

const mainNav: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: "📊" },
  { label: "Repositories", href: "/dashboard/repos", icon: "📂" },
  { label: "Analysis", href: "/dashboard/analysis", icon: "🔬" },
  { label: "Insights", href: "/dashboard/insights", icon: "💡" },
];

const toolsNav: NavItem[] = [
  { label: "AI Assistant", href: "/dashboard/chat", icon: "🤖", badge: "Beta" },
  { label: "Code Search", href: "/dashboard/search", icon: "🔍" },
  { label: "Dep Graph", href: "/dashboard/dependencies", icon: "🕸️" },
];

const bottomNav: NavItem[] = [
  { label: "Settings", href: "/dashboard/settings", icon: "⚙️" },
];

interface SidebarProps {
  isOpen?: boolean;
}

export function Sidebar({ isOpen }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();

  const initials = user?.full_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2) || "??";

  const renderNavItems = (items: NavItem[]) =>
    items.map((item) => {
      const isActive = pathname === item.href;
      return (
        <Link
          key={item.href}
          href={item.href}
          className={`${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
        >
          <span className={styles.navIcon}>{item.icon}</span>
          {item.label}
          {item.badge && <span className={styles.navBadge}>{item.badge}</span>}
        </Link>
      );
    });

  return (
    <aside className={`${styles.sidebar} ${isOpen ? styles.sidebarOpen : ""}`}>
      {/* Logo */}
      <Link href="/dashboard" className={styles.logo}>
        <span className={styles.logoIcon}>🧬</span>
        <span className={styles.logoText}>Synkora</span>
      </Link>

      {/* Navigation */}
      <nav className={styles.nav}>
        <div className={styles.navSection}>
          <div className={styles.navSectionLabel}>Main</div>
          {renderNavItems(mainNav)}
        </div>

        <div className={styles.navSection}>
          <div className={styles.navSectionLabel}>Tools</div>
          {renderNavItems(toolsNav)}
        </div>

        <div style={{ flex: 1 }} />

        <div className={styles.navSection}>
          {renderNavItems(bottomNav)}
        </div>
      </nav>

      {/* User Card */}
      <div className={styles.sidebarFooter}>
        <Link href="/dashboard/settings" className={styles.userCard}>
          <div className={styles.userAvatar}>{initials}</div>
          <div style={{ overflow: "hidden" }}>
            <div className={styles.userName}>{user?.full_name || "User"}</div>
            <div className={styles.userEmail}>{user?.email || ""}</div>
          </div>
        </Link>
      </div>
    </aside>
  );
}
