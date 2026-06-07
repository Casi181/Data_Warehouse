"use client";
import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import InboxIcon from "@mui/icons-material/Inbox";

interface Props {
  title?: string;
  message?: string;
}

export default function EmptyState({ title = "No data", message = "There is nothing to display yet." }: Props) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 300,
        gap: 1,
        color: "text.secondary",
      }}
    >
      <InboxIcon sx={{ fontSize: 64, opacity: 0.3 }} />
      <Typography variant="h6">{title}</Typography>
      <Typography variant="body2">{message}</Typography>
    </Box>
  );
}
