"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { RepoBrowser } from "@/components/dashboard/RepoBrowser";
import styles from "./dashboard.module.css";

const LANG_COLORS: Record<string, string> = {
  TypeScript: "#3178C6",
  JavaScript: "#F7DF1E",
  Python: "#3776AB",
  Rust: "#DEA584",
  Go: "#00ADD8",
  Java: "#ED8B00",
  Ruby: "#CC342D",
};

const mockRepos = [
  {
    id: "1",
    name: "synkora",
    full_name: "nigam0998/Synkora",
    description: "AI-Powered Software Evolution Intelligence Platform",
    language: "TypeScript",
    stars: 12,
    forks: 3,
    status: "ready",
    updatedAt: "2 hours ago",
  },
  {
    id: "2",
    name: "api-gateway",
    full_name: "nigam0998/api-gateway",
    description: "High-performance API gateway with rate limiting and auth",
    language: "Go",
    stars: 45,
    forks: 8,
    status: "analyzing",
    updatedAt: "1 day ago",
  },
  {
    id: "3",
    name: "ml-pipeline",
    full_name: "nigam0998/ml-pipeline",
    description: "End-to-end machine learning pipeline with feature store",
    language: "Python",
    stars: 89,
    forks: 21,
    status: "pending",
    updatedAt: "3 days ago",
  },
];

const mockActivity = [
  { icon: "🔬", text: "Analysis completed for synkora", time: "2 hours ago" },
  { icon: "📂", text: "Repository api-gateway connected", time: "1 day ago" },
  { icon: "💡", text: "3 new insights found in ml-pipeline", time: "2 days ago" },
  { icon: "🐛", text: "Bug risk detected in auth module", time: "3 days ago" },
];

function getStatusClass(status: string) {
  switch (status) {
    case "ready": return styles.statusReady;
    case "analyzing": return styles.statusAnalyzing;
    case "pending": return styles.statusPending;
    case "error": return styles.statusError;
    default: return styles.statusPending;
  }
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [repoBrowserOpen, setRepoBrowserOpen] = useState(false);

  return (
    <ProtectedRoute>
      <DashboardHeader
        title={`Welcome back, ${user?.full_name?.split(" ")[0] || "User"}`}
        breadcrumbs={[{ label: "Dashboard" }]}
      />

      <div className={styles.pageContent}>
        {/* ── Stats Grid ──────────────────────────────────── */}
        <div className={styles.statsGrid}>
          {[
            { icon: "📂", label: "Repositories", value: "3", trend: "+1", trendDir: "up", color: "purple" },
            { icon: "🔬", label: "Analyses", value: "12", trend: "+3", trendDir: "up", color: "cyan" },
            { icon: "💡", label: "Insights", value: "47", trend: "+8", trendDir: "up", color: "green" },
            { icon: "⚠️", label: "Open Issues", value: "5", trend: "-2", trendDir: "down", color: "orange" },
          ].map((stat) => (
            <div key={stat.label} className={styles.statCard}>
              <div className={styles.statCardHeader}>
                <div className={`${styles.statCardIcon} ${styles[stat.color]}`}>
                  {stat.icon}
                </div>
                <span className={`${styles.statCardTrend} ${stat.trendDir === "up" ? styles.trendUp : styles.trendDown}`}>
                  {stat.trendDir === "up" ? "↑" : "↓"} {stat.trend}
                </span>
              </div>
              <div className={styles.statCardValue}>{stat.value}</div>
              <div className={styles.statCardLabel}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* ── Repositories ────────────────────────────────── */}
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Your Repositories</h2>
          <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "center" }}>
            <button
              onClick={() => setRepoBrowserOpen(true)}
              className={styles.sectionAction}
              style={{
                background: "linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))",
                color: "white",
                border: "none",
                padding: "var(--space-2) var(--space-4)",
                borderRadius: "var(--radius-md)",
                fontSize: "var(--text-xs)",
                fontWeight: 600,
                cursor: "pointer",
                fontFamily: "var(--font-sans)",
              }}
            >
              + Connect Repo
            </button>
            <Link href="/dashboard/repos" className={styles.sectionAction}>
              View all →
            </Link>
          </div>
        </div>

        <div className={styles.repoGrid}>
          {mockRepos.map((repo) => (
            <Link
              key={repo.id}
              href={`/dashboard/repos/${repo.id}`}
              className={styles.repoCard}
            >
              <div className={styles.repoCardTop}>
                <div>
                  <div className={styles.repoName}>{repo.name}</div>
                  <div className={styles.repoFullName}>{repo.full_name}</div>
                </div>
                <span className={`${styles.repoStatus} ${getStatusClass(repo.status)}`}>
                  {repo.status}
                </span>
              </div>

              <p className={styles.repoDescription}>{repo.description}</p>

              <div className={styles.repoMeta}>
                {repo.language && (
                  <span className={styles.repoMetaItem}>
                    <span
                      className={styles.langDot}
                      style={{ background: LANG_COLORS[repo.language] || "#888" }}
                    />
                    {repo.language}
                  </span>
                )}
                <span className={styles.repoMetaItem}>⭐ {repo.stars}</span>
                <span className={styles.repoMetaItem}>🍴 {repo.forks}</span>
                <span className={styles.repoMetaItem} style={{ marginLeft: "auto" }}>
                  {repo.updatedAt}
                </span>
              </div>
            </Link>
          ))}
        </div>

        {/* ── Recent Activity ─────────────────────────────── */}
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Recent Activity</h2>
        </div>

        <div className={styles.activityList}>
          {mockActivity.map((item, i) => (
            <div key={i} className={styles.activityItem}>
              <div className={styles.activityIcon}>{item.icon}</div>
              <div className={styles.activityContent}>
                <div className={styles.activityText}>{item.text}</div>
                <div className={styles.activityTime}>{item.time}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Repo Browser Modal ─────────────────────────── */}
      <RepoBrowser
        isOpen={repoBrowserOpen}
        onClose={() => setRepoBrowserOpen(false)}
        onConnect={(repos) => {
          // TODO: Call API to import repos
          console.log("Connecting repos:", repos);
        }}
      />
    </ProtectedRoute>
  );
}
