"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import styles from "../dashboard.module.css";

type SettingsTab = "profile" | "security" | "notifications" | "danger";

const tabs: { id: SettingsTab; label: string; icon: string }[] = [
  { id: "profile", label: "Profile", icon: "👤" },
  { id: "security", label: "Security", icon: "🔒" },
  { id: "notifications", label: "Notifications", icon: "🔔" },
  { id: "danger", label: "Danger Zone", icon: "⚠️" },
];

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "var(--space-3) var(--space-4)",
  background: "var(--color-bg-tertiary)",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--color-text-primary)",
  fontSize: "var(--text-sm)",
  fontFamily: "var(--font-sans)",
  outline: "none",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "var(--text-sm)",
  fontWeight: 600,
  color: "var(--color-text-secondary)",
  marginBottom: "var(--space-2)",
};

const btnPrimary: React.CSSProperties = {
  padding: "var(--space-2) var(--space-5)",
  background: "linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))",
  color: "white",
  border: "none",
  borderRadius: "var(--radius-md)",
  fontWeight: 600,
  fontSize: "var(--text-sm)",
  cursor: "pointer",
  fontFamily: "var(--font-sans)",
};

const btnDanger: React.CSSProperties = {
  padding: "var(--space-2) var(--space-5)",
  background: "rgba(255, 82, 82, 0.1)",
  color: "var(--color-error)",
  border: "1px solid rgba(255, 82, 82, 0.3)",
  borderRadius: "var(--radius-md)",
  fontWeight: 600,
  fontSize: "var(--text-sm)",
  cursor: "pointer",
  fontFamily: "var(--font-sans)",
};

export default function SettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [email] = useState(user?.email || "");

  return (
    <ProtectedRoute>
      <DashboardHeader
        title="Settings"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Settings" },
        ]}
      />

      <div className={styles.pageContent}>
        <div className={styles.settingsGrid}>
          {/* ── Settings Nav ──────────────────────────────── */}
          <nav className={styles.settingsNav}>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`${styles.settingsNavLink} ${activeTab === tab.id ? styles.settingsNavActive : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>

          {/* ── Settings Panel ────────────────────────────── */}
          <div className={styles.settingsPanel}>
            {activeTab === "profile" && (
              <div className={styles.settingsSection}>
                <h2 className={styles.settingsSectionTitle}>Profile</h2>
                <p className={styles.settingsSectionDesc}>
                  Manage your personal information and account details.
                </p>

                <form className={styles.settingsForm} onSubmit={(e) => e.preventDefault()}>
                  <div className={styles.settingsRow}>
                    <div>
                      <label style={labelStyle}>Full Name</label>
                      <input
                        style={inputStyle}
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Your name"
                      />
                    </div>
                    <div>
                      <label style={labelStyle}>Email</label>
                      <input
                        style={{ ...inputStyle, opacity: 0.6 }}
                        value={email}
                        readOnly
                        title="Email cannot be changed"
                      />
                    </div>
                  </div>

                  <div>
                    <label style={labelStyle}>Avatar URL</label>
                    <input
                      style={inputStyle}
                      placeholder="https://example.com/avatar.jpg"
                    />
                  </div>

                  <div>
                    <button type="submit" style={btnPrimary}>
                      Save Changes
                    </button>
                  </div>
                </form>
              </div>
            )}

            {activeTab === "security" && (
              <div className={styles.settingsSection}>
                <h2 className={styles.settingsSectionTitle}>Security</h2>
                <p className={styles.settingsSectionDesc}>
                  Update your password and manage security settings.
                </p>

                <form className={styles.settingsForm} onSubmit={(e) => e.preventDefault()}>
                  <div>
                    <label style={labelStyle}>Current Password</label>
                    <input style={inputStyle} type="password" placeholder="••••••••" />
                  </div>
                  <div className={styles.settingsRow}>
                    <div>
                      <label style={labelStyle}>New Password</label>
                      <input style={inputStyle} type="password" placeholder="••••••••" />
                    </div>
                    <div>
                      <label style={labelStyle}>Confirm New Password</label>
                      <input style={inputStyle} type="password" placeholder="••••••••" />
                    </div>
                  </div>
                  <div>
                    <button type="submit" style={btnPrimary}>
                      Update Password
                    </button>
                  </div>
                </form>

                <div style={{ marginTop: "var(--space-10)" }}>
                  <h3 className={styles.settingsSectionTitle} style={{ fontSize: "var(--text-base)" }}>
                    Connected Accounts
                  </h3>
                  <p className={styles.settingsSectionDesc}>
                    Manage your connected third-party accounts.
                  </p>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "var(--space-4)",
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-md)",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                      <span style={{ fontSize: "var(--text-2xl)" }}>🐙</span>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: "var(--text-sm)" }}>GitHub</div>
                        <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-tertiary)" }}>
                          Not connected
                        </div>
                      </div>
                    </div>
                    <button style={{
                      ...btnPrimary,
                      padding: "var(--space-1) var(--space-4)",
                      fontSize: "var(--text-xs)",
                    }}>
                      Connect
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "notifications" && (
              <div className={styles.settingsSection}>
                <h2 className={styles.settingsSectionTitle}>Notifications</h2>
                <p className={styles.settingsSectionDesc}>
                  Control which notifications you receive.
                </p>
                <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--text-sm)" }}>
                  Notification preferences coming soon.
                </div>
              </div>
            )}

            {activeTab === "danger" && (
              <div className={styles.settingsSection}>
                <h2 className={styles.settingsSectionTitle} style={{ color: "var(--color-error)" }}>
                  Danger Zone
                </h2>
                <p className={styles.settingsSectionDesc}>
                  Irreversible and destructive actions.
                </p>
                <div className={styles.dangerZone}>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "var(--space-4)",
                  }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "var(--text-sm)", marginBottom: "var(--space-1)" }}>
                        Delete Account
                      </div>
                      <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-tertiary)" }}>
                        Permanently delete your account and all associated data.
                      </div>
                    </div>
                    <button style={btnDanger}>Delete</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
