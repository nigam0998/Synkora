"use client";

import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface TechDebtChartProps {
  data: { date: string; techDebt: number }[];
}

export function TechDebtChart({ data }: TechDebtChartProps) {
  if (!data || data.length === 0) {
    return <div style={{ padding: "var(--space-4)", textAlign: "center", color: "var(--color-text-secondary)" }}>No history available</div>;
  }

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <LineChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis 
            dataKey="date" 
            stroke="var(--color-text-secondary)" 
            tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
            tickMargin={10}
          />
          <YAxis 
            stroke="var(--color-text-secondary)" 
            tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
            tickFormatter={(value) => `${value}h`}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: "var(--color-bg-elevated)", 
              borderColor: "var(--color-border)",
              borderRadius: "var(--radius-md)",
              color: "var(--color-text-primary)"
            }}
            formatter={(value: number) => [`${value.toFixed(1)} hours`, "Tech Debt"]}
            labelStyle={{ color: "var(--color-text-secondary)" }}
          />
          <Line 
            type="monotone" 
            dataKey="techDebt" 
            stroke="var(--color-error)" 
            strokeWidth={3}
            dot={{ r: 4, fill: "var(--color-error)" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
