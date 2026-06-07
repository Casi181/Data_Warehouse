"use client";
import React, { useState } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import SendIcon from "@mui/icons-material/Send";
import CircularProgress from "@mui/material/CircularProgress";

interface Props {
  onSend: (text: string) => void;
  loading?: boolean;
}

export default function ChatInput({ onSend, loading }: Props) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() && !loading) {
      onSend(text.trim());
      setText("");
    }
  };

  return (
    <Box sx={{ p: 2, display: "flex", gap: 1 }}>
      <TextField
        fullWidth
        size="small"
        placeholder="Ask about the data warehouse..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
        disabled={loading}
      />
      <IconButton color="primary" onClick={handleSend} disabled={!text.trim() || loading}>
        {loading ? <CircularProgress size={24} /> : <SendIcon />}
      </IconButton>
    </Box>
  );
}
