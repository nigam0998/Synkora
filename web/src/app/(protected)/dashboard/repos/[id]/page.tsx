"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { api } from "@/lib/api";
import styles from "../../dashboard.module.css";
import { LanguageChart } from "@/components/dashboard/AnalysisCharts/LanguageChart";
import { TechDebtChart } from "@/components/dashboard/AnalysisCharts/TechDebtChart";
import { InsightsList, Insight } from "@/components/dashboard/InsightsList/InsightsList";
import { RepoChatWidget } from "@/components/dashboard/RepoChatWidget/RepoChatWidget";

interface Repository {
  id: string;
  name: string;
  full_name: string;
  description: string;
  analysis_status: string;
}

interface AnalysisDetail {
  analysis: {
    id: string;
    total_files: number;
    total_lines: number;
    avg_complexity: number;
    tech_debt_score: number;
    language_breakdown: Record<string, number>;
    updated_at: string;
  };
  insights: Insight[];
  insight_summary: Record<string, number>;
}

export default function RepoDashboardPage() {
  const { id } = useParams() as { id: string };
  const [repo, setRepo] = useState<Repository | null>(null);
  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [history, setHistory] = useState<{ date: string; techDebt: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // Fetch Repo
        const repoRes = await api.get<Repository>(`/api/v1/repositories/${id}`);
        if (!repoRes.success || !repoRes.data) {
          throw new Error("Repository not found");
        }
        setRepo(repoRes.data);

        // Fetch Latest Analysis
        const analysisRes = await api.get<AnalysisDetail>(`/api/v1/analysis/${id}/latest`);
        if (analysisRes.success && analysisRes.data) {
          setDetail(analysisRes.data);
        }

        // Fetch History
        const historyRes = await api.get<{ history: { created_at: string; tech_debt_score: number }[] }>(`/api/v1/analysis/${id}/history`);
        if (historyRes.success && historyRes.data) {
          const chartData = historyRes.data.history.map((a) => ({
            date: new Date(a.created_at).toLocaleDateString(),
            techDebt: a.tech_debt_score || 0,
          }));
          setHistory(chartData);
        }

      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message || "Failed to load repository data");
        } else {
          setError("Failed to load repository data");
        }
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      fetchData();
    }
  }, [id]);

  if (loading) {
    return (
      <ProtectedRoute>
        <div style={{ display: "flex", justifyContent: "center", padding: "100px" }}>
          Loading analysis results...
        </div>
      </ProtectedRoute>
    );
  }

  if (error || !repo) {
    return (
      <ProtectedRoute>
        <DashboardHeader
          title="Error"
          breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Error" }]}
        />
        <div style={{ padding: "var(--space-6)", color: "var(--color-error)", textAlign: "center" }}>
          {error || "Could not load repository."}
        </div>
      </ProtectedRoute>
    );
  }

  // Calculate Tech Debt Grade
  let grade = "A";
  let gradeColor = "var(--color-success)";
  if (detail?.analysis?.tech_debt_score !== undefined) {
    const score = detail.analysis.tech_debt_score;
    if (score > 10) { grade = "F"; gradeColor = "var(--color-error)"; }
    else if (score > 5) { grade = "D"; gradeColor = "var(--color-error)"; }
    else if (score > 2) { grade = "C"; gradeColor = "var(--color-warning)"; }
    else if (score > 0.5) { grade = "B"; gradeColor = "var(--color-primary)"; }
  }

  return (
    <ProtectedRoute>
      <DashboardHeader
        title={repo.name}
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: repo.full_name }
        ]}
      />

      <div className={styles.pageContent}>
        {/* ── Top Level Stats ──────────────────────────────────── */}
        <div className={styles.statsGrid}>
          <div className={styles.statCard} style={{ borderTop: `4px solid ${gradeColor}` }}>
            <div className={styles.statCardHeader}>
              <div className={`${styles.statCardIcon}`} style={{ color: gradeColor }}>
                🏅
              </div>
            </div>
            <div className={styles.statCardValue} style={{ color: gradeColor }}>{grade}</div>
            <div className={styles.statCardLabel}>Tech Debt Grade</div>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statCardHeader}>
              <div className={`${styles.statCardIcon} ${styles.cyan}`}>
                📄
              </div>
            </div>
            <div className={styles.statCardValue}>{detail?.analysis?.total_files || 0}</div>
            <div className={styles.statCardLabel}>Total Files</div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statCardHeader}>
              <div className={`${styles.statCardIcon} ${styles.purple}`}>
                💻
              </div>
            </div>
            <div className={styles.statCardValue}>
              {detail?.analysis?.total_lines.toLocaleString() || 0}
            </div>
            <div className={styles.statCardLabel}>Lines of Code</div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statCardHeader}>
              <div className={`${styles.statCardIcon} ${styles.orange}`}>
                🧠
              </div>
            </div>
            <div className={styles.statCardValue}>
              {detail?.analysis?.avg_complexity?.toFixed(1) || 0}
            </div>
            <div className={styles.statCardLabel}>Avg Complexity</div>
          </div>
        </div>

        {/* ── Charts Row ───────────────────────────────────────── */}
        {detail ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-6)", marginTop: "var(--space-6)" }}>
            <div style={{ backgroundColor: "var(--color-bg-elevated)", padding: "var(--space-4)", borderRadius: "var(--radius-lg)", border: "1px solid var(--color-border)" }}>
              <h3 style={{ marginBottom: "var(--space-4)", fontSize: "var(--text-lg)" }}>Language Breakdown</h3>
              <LanguageChart data={detail.analysis.language_breakdown} />
            </div>
            <div style={{ backgroundColor: "var(--color-bg-elevated)", padding: "var(--space-4)", borderRadius: "var(--radius-lg)", border: "1px solid var(--color-border)" }}>
              <h3 style={{ marginBottom: "var(--space-4)", fontSize: "var(--text-lg)" }}>Tech Debt History</h3>
              <TechDebtChart data={history} />
            </div>
          </div>
        ) : (
          <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--color-text-secondary)", backgroundColor: "var(--color-bg-elevated)", borderRadius: "var(--radius-lg)", marginTop: "var(--space-6)" }}>
            No analysis results available yet. Trigger an analysis to see insights.
          </div>
        )}

        {/* ── Insights List ────────────────────────────────────── */}
        {detail && detail.insights && detail.insights.length > 0 && (
          <div style={{ marginTop: "var(--space-8)" }}>
            <h2 className={styles.sectionTitle}>Detected Insights</h2>
            <div style={{ marginTop: "var(--space-4)" }}>
              <InsightsList insights={detail.insights} />
            </div>
          </div>
        )}
      </div>

      {/* Floating Chat Widget */}
      <RepoChatWidget repositoryId={repo.id} />
    </ProtectedRoute>
  );
}
