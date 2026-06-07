"use client";
import React from "react";
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface DataItem {
  name: string;
  value: number;
}

interface Props {
  data: DataItem[];
  colors?: string[];
  height?: number;
}

const DEFAULT_COLORS = ["#1976d2", "#ff9800", "#4caf50", "#9c27b0", "#f44336", "#00bcd4"];

export default function PieChart({ data, colors = DEFAULT_COLORS, height = 300 }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
        >
          {data.map((_, idx) => (
            <Cell key={idx} fill={colors[idx % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </RechartsPieChart>
    </ResponsiveContainer>
  );
}
