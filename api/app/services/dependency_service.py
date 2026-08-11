"""
Synkora API — Dependency Graph Service

Builds a dependency graph from AST-parsed import data.
Resolves imports to actual files, detects circular dependencies,
and calculates coupling metrics.
"""

from pathlib import Path
from collections import defaultdict
from typing import Optional

from app.schemas.ast import ParsedFile
from app.schemas.dependency import (
    DependencyNode,
    DependencyEdge,
    DependencyGraph,
    CircularDependency,
)
from app.services.ast_service import ASTService
from app.core.logging import get_logger

logger = get_logger("dependency_service")

# Directories to skip during repo scanning
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".next", ".venv",
    "venv", "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
    "target", "vendor", ".kiro",
}


class DependencyService:
    """Service for building and analyzing dependency graphs."""

    # ── Import Resolution ────────────────────────────────────────────────────

    @staticmethod
    def resolve_python_import(
        module_path: str,
        source_file: Path,
        repo_root: Path,
        file_index: dict[str, str],
    ) -> Optional[str]:
        """
        Resolve a Python import string to a file path relative to repo root.

        Examples:
            "app.services.auth_service" → "app/services/auth_service.py"
            "os" → None (stdlib, not in repo)
        """
        # Convert dotted path to filesystem path
        parts = module_path.split(".")
        candidates = [
            "/".join(parts) + ".py",
            "/".join(parts) + "/__init__.py",
        ]

        for candidate in candidates:
            normalized = candidate.replace("\\", "/")
            if normalized in file_index:
                return normalized

        return None

    @staticmethod
    def resolve_js_import(
        module_path: str,
        source_file: Path,
        repo_root: Path,
        file_index: dict[str, str],
    ) -> Optional[str]:
        """
        Resolve a JS/TS import string to a file path relative to repo root.

        Examples:
            "./components/Button" → "src/components/Button.tsx"
            "@/lib/api" → "src/lib/api.ts"
            "react" → None (node_module, not in repo)
        """
        # Skip node_modules / bare imports
        if not module_path.startswith(".") and not module_path.startswith("@/"):
            return None

        # Handle alias imports (@/ → src/)
        if module_path.startswith("@/"):
            module_path = "src/" + module_path[2:]
            base_dir = repo_root
        else:
            # Relative import — resolve from the source file's directory
            base_dir = source_file.parent

        # Try various extensions
        extensions = [".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js"]

        for ext in extensions:
            if module_path.startswith("src/"):
                candidate = module_path + ext
            else:
                try:
                    resolved = (base_dir / module_path).resolve()
                    candidate = str(
                        (resolved.parent / (resolved.name + ext))
                        .relative_to(repo_root)
                    ).replace("\\", "/")
                except (ValueError, OSError):
                    continue

            normalized = candidate.replace("\\", "/")
            if normalized in file_index:
                return normalized

        return None

    @staticmethod
    def resolve_go_import(
        module_path: str,
        source_file: Path,
        repo_root: Path,
        file_index: dict[str, str],
    ) -> Optional[str]:
        """Resolve a Go import to a file path (limited to local packages)."""
        # Go imports are typically full module paths
        # We only resolve local package imports
        parts = module_path.strip('"').split("/")
        # Try the last segment as a package directory
        if len(parts) >= 1:
            pkg_dir = parts[-1]
            for filepath in file_index:
                if f"/{pkg_dir}/" in filepath or filepath.startswith(f"{pkg_dir}/"):
                    return filepath
        return None

    @staticmethod
    def resolve_rust_import(
        module_path: str,
        source_file: Path,
        repo_root: Path,
        file_index: dict[str, str],
    ) -> Optional[str]:
        """Resolve a Rust use declaration to a file path."""
        parts = module_path.replace("::", "/").split("/")
        if len(parts) >= 2:
            # Try "src/<path>.rs" and "src/<path>/mod.rs"
            candidates = [
                "src/" + "/".join(parts[1:]) + ".rs",
                "src/" + "/".join(parts[1:]) + "/mod.rs",
            ]
            for candidate in candidates:
                if candidate in file_index:
                    return candidate
        return None

    # ── Graph Building ───────────────────────────────────────────────────────

    @staticmethod
    def build_graph(repo_path: Path) -> DependencyGraph:
        """
        Build a complete dependency graph for a repository.

        Steps:
        1. Scan all supported source files
        2. Parse ASTs to extract imports
        3. Resolve imports to actual file paths
        4. Build nodes and edges
        5. Detect circular dependencies
        6. Calculate coupling metrics
        """
        repo_path = repo_path.resolve()

        # Step 1: Index all source files
        file_index: dict[str, str] = {}  # relative_path → language
        parsed_files: dict[str, ParsedFile] = {}

        for path in repo_path.rglob("*"):
            if path.is_dir():
                continue

            parts = path.relative_to(repo_path).parts
            if any(part in SKIP_DIRS for part in parts):
                continue

            lang = ASTService.get_language_from_extension(path)
            if lang is None:
                continue

            rel_path = str(path.relative_to(repo_path)).replace("\\", "/")
            file_index[rel_path] = lang

            # Parse AST
            parsed = ASTService.parse_file(path)
            if parsed:
                parsed_files[rel_path] = parsed

        # Step 2: Build edges by resolving imports
        edges: list[DependencyEdge] = []
        in_degree: dict[str, int] = defaultdict(int)
        out_degree: dict[str, int] = defaultdict(int)

        resolvers = {
            "python": DependencyService.resolve_python_import,
            "javascript": DependencyService.resolve_js_import,
            "typescript": DependencyService.resolve_js_import,
            "tsx": DependencyService.resolve_js_import,
            "go": DependencyService.resolve_go_import,
            "rust": DependencyService.resolve_rust_import,
        }

        adjacency: dict[str, set[str]] = defaultdict(set)  # For cycle detection

        for rel_path, parsed in parsed_files.items():
            lang = file_index[rel_path]
            resolver = resolvers.get(lang)
            if not resolver:
                continue

            source_file = repo_path / rel_path

            for imp in parsed.imports:
                target = resolver(
                    imp.module, source_file, repo_path, file_index
                )
                if target and target != rel_path:  # Don't self-reference
                    edges.append(
                        DependencyEdge(
                            source=rel_path,
                            target=target,
                            import_names=imp.imported_names,
                        )
                    )
                    in_degree[target] += 1
                    out_degree[rel_path] += 1
                    adjacency[rel_path].add(target)

        # Step 3: Build nodes
        nodes: list[DependencyNode] = []
        for rel_path, lang in file_index.items():
            parsed = parsed_files.get(rel_path)
            ind = in_degree.get(rel_path, 0)
            outd = out_degree.get(rel_path, 0)

            node = DependencyNode(
                id=rel_path,
                filepath=rel_path,
                language=lang,
                lines_of_code=parsed.total_lines if parsed else 0,
                function_count=parsed.total_functions if parsed else 0,
                class_count=parsed.total_classes if parsed else 0,
                import_count=len(parsed.imports) if parsed else 0,
                in_degree=ind,
                out_degree=outd,
                is_entry_point=(ind == 0 and outd > 0),
                is_utility=(ind >= 3),
            )
            nodes.append(node)

        # Step 4: Detect circular dependencies
        circular_deps = DependencyService._detect_cycles(adjacency)

        # Step 5: Calculate aggregate metrics
        total_in = [n.in_degree for n in nodes if n.in_degree > 0]
        total_out = [n.out_degree for n in nodes if n.out_degree > 0]

        avg_in = sum(total_in) / max(len(total_in), 1)
        avg_out = sum(total_out) / max(len(total_out), 1)
        max_in = max(total_in) if total_in else 0
        max_out = max(total_out) if total_out else 0

        # Top files by in/out degree
        sorted_by_in = sorted(nodes, key=lambda n: n.in_degree, reverse=True)
        sorted_by_out = sorted(nodes, key=lambda n: n.out_degree, reverse=True)

        most_depended = [n.id for n in sorted_by_in[:5] if n.in_degree > 0]
        most_dependent = [n.id for n in sorted_by_out[:5] if n.out_degree > 0]

        # Hotspots: files with high coupling (in + out > 2 * average)
        avg_coupling = avg_in + avg_out
        hotspots = [
            n.id for n in nodes
            if n.coupling_score > max(avg_coupling * 2, 4)
        ]

        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            circular_dependencies=circular_deps,
            total_files=len(nodes),
            total_edges=len(edges),
            avg_in_degree=round(avg_in, 1),
            avg_out_degree=round(avg_out, 1),
            max_in_degree=max_in,
            max_out_degree=max_out,
            most_depended_on=most_depended,
            most_dependent=most_dependent,
            hotspots=hotspots,
        )

    # ── Cycle Detection (DFS-based) ─────────────────────────────────────────

    @staticmethod
    def _detect_cycles(adjacency: dict[str, set[str]]) -> list[CircularDependency]:
        """
        Detect circular dependencies using DFS with coloring.

        Uses a standard 3-color algorithm:
          WHITE = not visited
          GRAY  = in current DFS path (on the stack)
          BLACK = fully processed
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {node: WHITE for node in adjacency}
        cycles: list[list[str]] = []
        path: list[str] = []

        def dfs(node: str):
            color[node] = GRAY
            path.append(node)

            for neighbor in adjacency.get(node, set()):
                if neighbor not in color:
                    color[neighbor] = WHITE

                if color[neighbor] == GRAY:
                    # Found a cycle — extract it from the path
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                elif color[neighbor] == WHITE:
                    dfs(neighbor)

            path.pop()
            color[node] = BLACK

        for node in list(adjacency.keys()):
            if color.get(node, WHITE) == WHITE:
                dfs(node)

        # Deduplicate cycles (same cycle can be found from different starting nodes)
        seen: set[tuple[str, ...]] = set()
        unique_cycles: list[CircularDependency] = []

        for cycle in cycles:
            # Normalize: rotate so the lexicographically smallest element is first
            if len(cycle) > 1:
                min_idx = cycle.index(min(cycle[:-1]))
                normalized = tuple(cycle[min_idx:-1])
                if normalized not in seen:
                    seen.add(normalized)
                    unique_cycles.append(
                        CircularDependency(
                            cycle=list(normalized) + [normalized[0]],
                            length=len(normalized),
                        )
                    )

        return unique_cycles
