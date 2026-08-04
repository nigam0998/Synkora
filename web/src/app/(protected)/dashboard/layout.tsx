"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/dashboard/Sidebar";
import styles from "./dashboard.module.css";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className={styles.dashboardWrapper}>
      <Sidebar isOpen={sidebarOpen} />
      <main className={styles.mainArea}>
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child as React.ReactElement<{ onMenuToggle?: () => void }>, {
              onMenuToggle: () => setSidebarOpen((prev) => !prev),
            });
          }
          return child;
        })}
      </main>
    </div>
  );
}
