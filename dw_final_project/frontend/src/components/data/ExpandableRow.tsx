"use client";
import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";

interface Props {
  data: Record<string, any>;
}

export default function ExpandableRow({ data }: Props) {
  return (
    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
      {Object.entries(data).map(([key, value]) => (
        <Chip
          key={key}
          label={`${key}: ${typeof value === "object" ? JSON.stringify(value) : value}`}
          variant="outlined"
          size="small"
        />
      ))}
    </Box>
  );
}
