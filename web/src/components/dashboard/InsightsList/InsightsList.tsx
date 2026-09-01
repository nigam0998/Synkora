"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { api } from "@/lib/api";
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

export function InsightsList({ insights: initialInsights }: InsightsListProps) {
  const [insightsList, setInsightsList] = useState<Insight[]>(initialInsights);
  const [loadingMap, setLoadingMap] = useState<Record<string, boolean>>({});

  if (!insightsList || insightsList.length === 0) {
    return <div className={styles.emptyState}>No insights found for this analysis run.</div>;
  }

  const handleGenerateFix = async (insightId: string) => {
    setLoadingMap(prev => ({ ...prev, [insightId]: true }));
    try {
      const res = await api.post<{ message: string; recommendation: string }>(`/api/v1/ai/insight/${insightId}/enrich`, {});
      if (res.success && res.data) {
        setInsightsList(prev => 
          prev.map(ins => 
            ins.id === insightId ? { ...ins, recommendation: res.data!.recommendation } : ins
          )
        );
      }
    } catch (error) {
      console.error("Failed to generate AI fix", error);
    } finally {
      setLoadingMap(prev => ({ ...prev, [insightId]: false }));
    }
  };

  return (
    <div className={styles.insightsContainer}>
      {insightsList.map((insight) => {
        const isAiGenerated = insight.recommendation?.includes("```") || insight.recommendation?.includes("**");
        const hasBasicRecommendation = insight.recommendation && !isAiGenerated;
        
        return (
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
            
            {(hasBasicRecommendation || !insight.recommendation) && (
              <button 
                className={styles.generateButton} 
                onClick={() => handleGenerateFix(insight.id)}
                disabled={loadingMap[insight.id]}
              >
                {loadingMap[insight.id] ? <div className={styles.loadingSpinner} /> : "✨"}
                {loadingMap[insight.id] ? "Generating AI Refactoring..." : "Generate AI Fix"}
              </button>
            )}

            {isAiGenerated && (
              <div className={`${styles.recommendation} ${styles.markdownContent}`}>
                <div className={styles.aiHeader}>
                  ✨ AI Refactoring Suggestion
                </div>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ inline, className, children, ...props }: React.ComponentPropsWithoutRef<"code"> & { inline?: boolean }) {
                      const match = /language-(\w+)/.exec(className || "");
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={vscDarkPlus as any}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, "")}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {insight.recommendation || ""}
                </ReactMarkdown>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
