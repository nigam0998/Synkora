"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div style={{
        padding: "var(--space-8)",
        maxWidth: "1200px",
        margin: "0 auto",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        gap: "var(--space-8)"
      }}>
        <header style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          paddingBottom: "var(--space-6)",
          borderBottom: "1px solid var(--color-border)"
        }}>
          <div>
            <h1 style={{ fontSize: "var(--text-3xl)", fontWeight: 800, marginBottom: "var(--space-2)" }}>
              Dashboard
            </h1>
            <p style={{ color: "var(--color-text-secondary)" }}>
              Welcome back, {user?.full_name}!
            </p>
          </div>
          <button
            onClick={logout}
            style={{
              padding: "var(--space-2) var(--space-4)",
              background: "var(--color-bg-tertiary)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-md)",
              color: "var(--color-text-primary)",
              cursor: "pointer",
              transition: "all var(--transition-fast)"
            }}
            onMouseOver={(e) => (e.currentTarget.style.borderColor = "var(--color-primary-light)")}
            onMouseOut={(e) => (e.currentTarget.style.borderColor = "var(--color-border)")}
          >
            Log Out
          </button>
        </header>

        <main>
          <div style={{
            background: "var(--color-bg-card)",
            padding: "var(--space-6)",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--color-border)",
            textAlign: "center"
          }}>
            <h2 style={{ marginBottom: "var(--space-4)" }}>Your Repositories</h2>
            <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-6)" }}>
              You haven&apos;t connected any repositories yet.
            </p>
            <button style={{
              padding: "var(--space-3) var(--space-6)",
              background: "linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))",
              color: "white",
              border: "none",
              borderRadius: "var(--radius-lg)",
              fontWeight: 600,
              cursor: "pointer",
              boxShadow: "var(--shadow-glow-primary)"
            }}>
              Connect GitHub Repository
            </button>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
