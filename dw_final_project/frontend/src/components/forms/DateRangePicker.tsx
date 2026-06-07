"use client";
import React from "react";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";

interface Props {
  startDate: string;
  endDate: string;
  onStartChange: (val: string) => void;
  onEndChange: (val: string) => void;
}

export default function DateRangePicker({ startDate, endDate, onStartChange, onEndChange }: Props) {
  return (
    <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
      <TextField
        label="Start Date"
        type="date"
        size="small"
        value={startDate}
        onChange={(e) => onStartChange(e.target.value)}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="End Date"
        type="date"
        size="small"
        value={endDate}
        onChange={(e) => onEndChange(e.target.value)}
        InputLabelProps={{ shrink: true }}
      />
    </Box>
  );
}
