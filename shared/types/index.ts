/**
 * Synkora — Shared Type Definitions
 *
 * Common types shared between frontend and backend.
 * These types define the API contract.
 */

// ── User Types ──────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  github_connected: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ── Repository Types ────────────────────────────────────────────────

export interface Repository {
  id: string;
  name: string;
  full_name: string;
  description?: string;
  url: string;
  default_branch: string;
  language?: string;
  languages: Record<string, number>;
  stars: number;
  forks: number;
  size_kb: number;
  is_private: boolean;
  last_analyzed_at?: string;
  analysis_status: AnalysisStatus;
  created_at: string;
  updated_at: string;
}

export type AnalysisStatus =
  | "pending"
  | "cloning"
  | "analyzing"
  | "completed"
  | "failed";

// ── Analysis Types ──────────────────────────────────────────────────

export interface AnalysisResult {
  id: string;
  repository_id: string;
  status: AnalysisStatus;
  metrics: CodeMetrics;
  tech_debt: TechDebtReport;
  dependencies: DependencyGraph;
  evolution: EvolutionData;
  started_at: string;
  completed_at?: string;
}

export interface CodeMetrics {
  total_files: number;
  total_lines: number;
  total_functions: number;
  total_classes: number;
  languages: LanguageBreakdown[];
  complexity: ComplexityMetrics;
}

export interface LanguageBreakdown {
  language: string;
  files: number;
  lines: number;
  percentage: number;
  color: string;
}

export interface ComplexityMetrics {
  average_cyclomatic: number;
  max_cyclomatic: number;
  average_cognitive: number;
  max_cognitive: number;
  hotspots: string[]; // file paths with highest complexity
}

// ── Technical Debt ──────────────────────────────────────────────────

export interface TechDebtReport {
  overall_score: number; // 0-100
  total_issues: number;
  issues: TechDebtIssue[];
  categories: TechDebtCategory[];
}

export interface TechDebtIssue {
  id: string;
  type: "code_smell" | "duplication" | "complexity" | "todo" | "security";
  severity: "low" | "medium" | "high" | "critical";
  file_path: string;
  line_number: number;
  message: string;
  suggestion?: string;
}

export interface TechDebtCategory {
  name: string;
  count: number;
  severity_breakdown: Record<string, number>;
}

// ── Dependencies ────────────────────────────────────────────────────

export interface DependencyGraph {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  circular_dependencies: string[][];
}

export interface DependencyNode {
  id: string;
  label: string;
  type: "module" | "package" | "service" | "external";
  size: number;
}

export interface DependencyEdge {
  source: string;
  target: string;
  type: "import" | "dependency" | "dev_dependency";
}

// ── Evolution ───────────────────────────────────────────────────────

export interface EvolutionData {
  commits: CommitData[];
  contributors: ContributorData[];
  file_changes: FileChangeData[];
  activity_heatmap: ActivityHeatmapEntry[];
}

export interface CommitData {
  hash: string;
  message: string;
  author: string;
  author_email: string;
  date: string;
  additions: number;
  deletions: number;
  files_changed: number;
}

export interface ContributorData {
  name: string;
  email: string;
  commits: number;
  additions: number;
  deletions: number;
  first_commit: string;
  last_commit: string;
}

export interface FileChangeData {
  file_path: string;
  change_count: number;
  last_modified: string;
  risk_score: number;
}

export interface ActivityHeatmapEntry {
  date: string;
  count: number;
}

// ── AI Chat ─────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  code_references?: CodeReference[];
  timestamp: string;
}

export interface CodeReference {
  file_path: string;
  start_line: number;
  end_line: number;
  snippet: string;
  language: string;
}

export interface ChatConversation {
  id: string;
  repository_id: string;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

// ── API Response Wrapper ────────────────────────────────────────────

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
