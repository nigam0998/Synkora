"use client";

import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS = ["#3178C6", "#F7DF1E", "#3776AB", "#DEA584", "#00ADD8", "#ED8B00", "#CC342D", "#8884d8"];

interface LanguageChartProps {
  data: Record<string, number> | null;
}

export function LanguageChart({ data }: LanguageChartProps) {
  if (!data || Object.keys(data).length === 0) {
    return <div style={{ padding: "var(--space-4)", textAlign: "center", color: "var(--color-text-secondary)" }}>No language data available</div>;
  }

  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: "var(--color-bg-elevated)", 
              borderColor: "var(--color-border)",
              borderRadius: "var(--radius-md)",
              color: "var(--color-text-primary)"
            }} 
          />
          <Legend verticalAlign="bottom" height={36} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
