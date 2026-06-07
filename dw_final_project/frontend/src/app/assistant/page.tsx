"use client";
import React, { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Paper from "@mui/material/Paper";
import type { ChatMessage as ChatMsg } from "@/lib/types";
import ChatMessage from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import { sendChatMessage } from "@/lib/api";

export default function AssistantPage() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I can help you explore assets, data sources, and time series data. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text: string) => {
    const userMsg: ChatMsg = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const reply = await sendChatMessage(text);
      const assistantMsg: ChatMsg = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      const errorMsg: ChatMsg = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${e.message}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI Assistant
      </Typography>

      <Card sx={{ height: "calc(100vh - 220px)", display: "flex", flexDirection: "column" }}>
        <CardContent
          sx={{
            flex: 1,
            overflow: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 1,
            p: 3,
          }}
        >
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && (
            <Paper
              sx={{
                px: 2,
                py: 1,
                maxWidth: "80%",
                bgcolor: "grey.100",
                borderRadius: 2,
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Thinking...
              </Typography>
            </Paper>
          )}
        </CardContent>
        <Box sx={{ borderTop: 1, borderColor: "divider" }}>
          <ChatInput onSend={handleSend} loading={loading} />
        </Box>
      </Card>
    </Box>
  );
}
