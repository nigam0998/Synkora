"use client";

import React from "react";
import styles from "./InsightsList.module.css";

export interface Insight {
  id: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  recommendation?: string;
  file_path?: string;
  line_start?: number;
  line_end?: number;
}

interface InsightsListProps {
  insights: Insight[];
}

export function InsightsList({ insights }: InsightsListProps) {
  if (!insights || insights.length === 0) {
    return <div className={styles.emptyState}>No insights found for this analysis run.</div>;
  }

  return (
    <div className={styles.insightsContainer}>
      {insights.map((insight) => (
        <div key={insight.id} className={`${styles.insightCard} ${styles[`severity${insight.severity.toUpperCase()}`]}`}>
          <div className={styles.insightHeader}>
            <span className={styles.severityBadge}>{insight.severity.toUpperCase()}</span>
            <span className={styles.categoryBadge}>{insight.category}</span>
          </div>
          <h4 className={styles.insightTitle}>{insight.title}</h4>
          <p className={styles.insightDescription}>{insight.description}</p>
          
          {insight.file_path && (
            <div className={styles.locationInfo}>
              <strong>Location:</strong> {insight.file_path}
              {insight.line_start && ` (Line ${insight.line_start}${insight.line_end && insight.line_end !== insight.line_start ? `-${insight.line_end}` : ''})`}
            </div>
          )}
          
          {insight.recommendation && (
            <div className={styles.recommendation}>
              <strong>Recommendation:</strong> {insight.recommendation}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
