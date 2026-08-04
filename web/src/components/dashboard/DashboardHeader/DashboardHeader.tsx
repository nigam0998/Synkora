"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import styles from "./DashboardHeader.module.css";

interface Breadcrumb {
  label: string;
  href?: string;
}

interface DashboardHeaderProps {
  title: string;
  breadcrumbs?: Breadcrumb[];
  onMenuToggle?: () => void;
}

export function DashboardHeader({
  title,
  breadcrumbs,
  onMenuToggle,
}: DashboardHeaderProps) {
  const { logout } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.headerLeft}>
        {/* Mobile menu button */}
        <button
          className={styles.menuButton}
          onClick={onMenuToggle}
          aria-label="Toggle sidebar"
        >
          ☰
        </button>

        <div>
          {/* Breadcrumbs */}
          {breadcrumbs && breadcrumbs.length > 0 && (
            <nav className={styles.breadcrumbs} aria-label="Breadcrumb">
              {breadcrumbs.map((crumb, index) => (
                <React.Fragment key={index}>
                  {index > 0 && (
                    <span className={styles.breadcrumbSep}>/</span>
                  )}
                  {crumb.href ? (
                    <Link href={crumb.href} className={styles.breadcrumbLink}>
                      {crumb.label}
                    </Link>
                  ) : (
                    <span className={styles.breadcrumbCurrent}>
                      {crumb.label}
                    </span>
                  )}
                </React.Fragment>
              ))}
            </nav>
          )}
          <h1 className={styles.pageTitle}>{title}</h1>
        </div>
      </div>

      <div className={styles.headerRight}>
        {/* Search */}
        <div className={styles.searchBar}>
          <span className={styles.searchIcon}>🔍</span>
          <input
            className={styles.searchInput}
            placeholder="Search repositories..."
            type="text"
            readOnly
          />
          <kbd className={styles.searchKbd}>⌘K</kbd>
        </div>

        {/* Notifications */}
        <button className={styles.iconButton} aria-label="Notifications">
          🔔
          <span className={styles.notifDot} />
        </button>

        {/* Logout */}
        <button
          className={styles.iconButton}
          onClick={logout}
          aria-label="Log out"
          title="Log out"
        >
          ↗
        </button>
      </div>
    </header>
  );
}
