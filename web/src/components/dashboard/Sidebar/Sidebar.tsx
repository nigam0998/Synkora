"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { 
  LayoutDashboard, FolderOpen, Activity, Lightbulb, 
  Bot, Search, Network, Settings, Dna 
} from "lucide-react";
import styles from "./Sidebar.module.css";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
}

const mainNav: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard size={18} /> },
  { label: "Repositories", href: "/dashboard/repos", icon: <FolderOpen size={18} /> },
  { label: "Analysis", href: "/dashboard/analysis", icon: <Activity size={18} /> },
  { label: "Insights", href: "/dashboard/insights", icon: <Lightbulb size={18} /> },
];

const toolsNav: NavItem[] = [
  { label: "AI Assistant", href: "/dashboard/chat", icon: <Bot size={18} />, badge: "Beta" },
  { label: "Code Search", href: "/dashboard/search", icon: <Search size={18} /> },
  { label: "Dep Graph", href: "/dashboard/dependencies", icon: <Network size={18} /> },
];

const bottomNav: NavItem[] = [
  { label: "Settings", href: "/dashboard/settings", icon: <Settings size={18} /> },
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
        <span className={styles.logoIcon}><Dna size={24} color="var(--color-primary)" /></span>
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
