"use client";
import React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";

interface Props {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  color?: string;
}

export default function MetricCard({ title, value, icon, trend, color = "#1976d2" }: Props) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700}>
              {value}
            </Typography>
            {trend !== undefined && (
              <Box sx={{ display: "flex", alignItems: "center", mt: 0.5, gap: 0.5 }}>
                {trend >= 0 ? (
                  <TrendingUpIcon sx={{ color: "success.main", fontSize: 18 }} />
                ) : (
                  <TrendingDownIcon sx={{ color: "error.main", fontSize: 18 }} />
                )}
                <Typography
                  variant="body2"
                  sx={{ color: trend >= 0 ? "success.main" : "error.main" }}
                >
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              bgcolor: `${color}15`,
              borderRadius: 2,
              p: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: color,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
