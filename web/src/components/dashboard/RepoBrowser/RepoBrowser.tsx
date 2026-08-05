"use client";

import React, { useState, useMemo } from "react";
import styles from "./RepoBrowser.module.css";

const LANG_COLORS: Record<string, string> = {
  TypeScript: "#3178C6",
  JavaScript: "#F7DF1E",
  Python: "#3776AB",
  Rust: "#DEA584",
  Go: "#00ADD8",
  Java: "#ED8B00",
  Ruby: "#CC342D",
  "C++": "#F34B7D",
  C: "#555555",
  Swift: "#FA7343",
  Kotlin: "#A97BFF",
};

// Mock GitHub repos for demonstration
const MOCK_GITHUB_REPOS = [
  { id: 101, name: "synkora", full_name: "nigam0998/Synkora", description: "AI-Powered Software Evolution Intelligence Platform", language: "TypeScript", stargazers_count: 12, private: false, updated_at: "2026-08-04T10:00:00Z" },
  { id: 102, name: "api-gateway", full_name: "nigam0998/api-gateway", description: "High-performance API gateway with rate limiting and auth", language: "Go", stargazers_count: 45, private: false, updated_at: "2026-08-03T10:00:00Z" },
  { id: 103, name: "ml-pipeline", full_name: "nigam0998/ml-pipeline", description: "End-to-end ML pipeline with feature store integration", language: "Python", stargazers_count: 89, private: true, updated_at: "2026-08-01T10:00:00Z" },
  { id: 104, name: "design-system", full_name: "nigam0998/design-system", description: "Shared design system components and tokens", language: "TypeScript", stargazers_count: 23, private: false, updated_at: "2026-07-28T10:00:00Z" },
  { id: 105, name: "infra-terraform", full_name: "nigam0998/infra-terraform", description: "Infrastructure as code for AWS deployments", language: "HCL", stargazers_count: 8, private: true, updated_at: "2026-07-25T10:00:00Z" },
  { id: 106, name: "blog-engine", full_name: "nigam0998/blog-engine", description: "Static site generator for technical blogs", language: "Rust", stargazers_count: 156, private: false, updated_at: "2026-07-20T10:00:00Z" },
  { id: 107, name: "data-pipeline", full_name: "nigam0998/data-pipeline", description: "Real-time data ingestion and processing pipeline", language: "Java", stargazers_count: 34, private: false, updated_at: "2026-07-18T10:00:00Z" },
  { id: 108, name: "auth-service", full_name: "nigam0998/auth-service", description: "Microservice for authentication and authorization", language: "Go", stargazers_count: 67, private: true, updated_at: "2026-07-15T10:00:00Z" },
];

interface RepoBrowserProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (repos: typeof MOCK_GITHUB_REPOS) => void;
}

export function RepoBrowser({ isOpen, onClose, onConnect }: RepoBrowserProps) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const filtered = useMemo(() => {
    if (!search.trim()) return MOCK_GITHUB_REPOS;
    const q = search.toLowerCase();
    return MOCK_GITHUB_REPOS.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.full_name.toLowerCase().includes(q) ||
        (r.description && r.description.toLowerCase().includes(q))
    );
  }, [search]);

  const toggleRepo = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleConnect = () => {
    const repos = MOCK_GITHUB_REPOS.filter((r) => selected.has(r.id));
    onConnect(repos);
    setSelected(new Set());
    setSearch("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Connect Repository</h2>
          <button className={styles.closeButton} onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Search */}
        <div className={styles.searchWrapper}>
          <input
            className={styles.searchInput}
            placeholder="Search your GitHub repositories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />
        </div>

        {/* Repo List */}
        <div className={styles.repoList}>
          {filtered.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>🔍</div>
              <div className={styles.emptyText}>No repositories found</div>
            </div>
          ) : (
            filtered.map((repo) => {
              const isSelected = selected.has(repo.id);
              return (
                <div
                  key={repo.id}
                  className={`${styles.repoItem} ${isSelected ? styles.repoItemSelected : ""}`}
                  onClick={() => toggleRepo(repo.id)}
                >
                  <div
                    className={`${styles.checkbox} ${isSelected ? styles.checkboxChecked : ""}`}
                  >
                    ✓
                  </div>

                  <div className={styles.repoInfo}>
                    <div className={styles.repoName}>
                      {repo.name}
                      {repo.private && <span className={styles.privateTag}>Private</span>}
                    </div>
                    {repo.description && (
                      <div className={styles.repoDesc}>{repo.description}</div>
                    )}
                  </div>

                  <div className={styles.repoMeta}>
                    {repo.language && (
                      <span className={styles.metaItem}>
                        <span
                          className={styles.langDot}
                          style={{ background: LANG_COLORS[repo.language] || "#888" }}
                        />
                        {repo.language}
                      </span>
                    )}
                    <span className={styles.metaItem}>⭐ {repo.stargazers_count}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className={styles.modalFooter}>
          <div className={styles.selectedCount}>
            <strong>{selected.size}</strong> {selected.size === 1 ? "repository" : "repositories"} selected
          </div>
          <div className={styles.footerActions}>
            <button className={styles.cancelButton} onClick={onClose}>
              Cancel
            </button>
            <button
              className={styles.connectButton}
              disabled={selected.size === 0}
              onClick={handleConnect}
            >
              Connect {selected.size > 0 ? `(${selected.size})` : ""}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
