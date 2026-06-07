"use client";
import React, { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import { triggerIngestion } from "@/lib/api";
import type { IngestionResult } from "@/lib/types";

const PERIOD_OPTIONS = [
  { value: "1mo", label: "1 Month" },
  { value: "3mo", label: "3 Months" },
  { value: "6mo", label: "6 Months" },
  { value: "1y", label: "1 Year" },
  { value: "2y", label: "2 Years" },
  { value: "5y", label: "5 Years" },
  { value: "10y", label: "10 Years" },
  { value: "max", label: "Max" },
];

export default function IngestionForm() {
  const [provider, setProvider] = useState("YFINANCE");
  const [codes, setCodes] = useState("");
  const [period, setPeriod] = useState("1y");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const dataset_codes = codes.split(",").map((c) => c.trim()).filter(Boolean);
      if (dataset_codes.length === 0) {
        setError("Enter at least one ticker symbol");
        return;
      }
      const res = await triggerIngestion({ provider, dataset_codes, period });
      setResult(res);
    } catch (e: any) {
      setError(e.message || "Ingestion failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader title="Trigger Ingestion" />
      <CardContent>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <TextField
            label="Provider"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            size="small"
          />
          <TextField
            label="Ticker Symbols (comma-separated)"
            value={codes}
            onChange={(e) => setCodes(e.target.value)}
            size="small"
            placeholder="e.g. AAPL, GOOGL, BTC-USD"
          />
          <TextField
            select
            label="History Period"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            size="small"
          >
            {PERIOD_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </TextField>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : undefined}
          >
            {loading ? "Ingesting..." : "Start Ingestion"}
          </Button>
          {error && <Alert severity="error">{error}</Alert>}
          {result && (
            <Alert severity="success">
              Fetched: {result.fetched} | Stored: {result.stored} | Errors: {result.errors}
            </Alert>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
