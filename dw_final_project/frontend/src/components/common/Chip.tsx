"use client";
import React from "react";
import MuiChip from "@mui/material/Chip";

interface Props {
  label: string;
  status?: "active" | "deleted" | "pending" | "default";
}

function getColor(status?: string): "success" | "error" | "warning" | "default" {
  switch (status) {
    case "active":
      return "success";
    case "deleted":
      return "error";
    case "pending":
      return "warning";
    default:
      return "default";
  }
}

export default function Chip({ label, status }: Props) {
  return <MuiChip label={label} color={getColor(status)} size="small" variant="outlined" />;
}
