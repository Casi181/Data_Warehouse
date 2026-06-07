"use client";
import React from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import LoadingOverlay from "@/components/common/LoadingOverlay";
import ErrorAlert from "@/components/common/ErrorAlert";
import useSWR from "swr";
import { getLatestPrices } from "@/lib/api";
import type { LatestPrice } from "@/lib/types";

function fmt(n: number) {
  if (n >= 1_000_000_000) return (n / 1_000_000_000).toFixed(1) + "B";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return n.toLocaleString();
}

function fmtPrice(n: number) {
  if (n >= 1000) return "$" + n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (n >= 1) return "$" + n.toFixed(2);
  return "$" + n.toFixed(4);
}

export default function DashboardPage() {
  const { data: prices, error, isLoading } = useSWR<LatestPrice[]>(
    "/data/latest-prices",
    getLatestPrices,
    { refreshInterval: 5000, revalidateOnFocus: true }
  );

  if (isLoading) return <LoadingOverlay message="Loading market data..." />;
  if (error) return <ErrorAlert message={error.message} />;

  const stocks = (prices ?? []).filter(p => p.asset_class === "stock");
  const crypto = (prices ?? []).filter(p => p.asset_class === "cryptocurrency");
  const commodities = (prices ?? []).filter(p => ["commodity", "etf", "index"].includes(p.asset_class));

  const gainers = [...(prices ?? [])].sort((a, b) => b.change_pct - a.change_pct).slice(0, 3);
  const losers = [...(prices ?? [])].sort((a, b) => a.change_pct - b.change_pct).slice(0, 3);

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h4" fontWeight={700}>Market Overview</Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: "success.main", animation: "pulse 2s infinite", "@keyframes pulse": { "0%, 100%": { opacity: 1 }, "50%": { opacity: 0.3 } } }} />
          <Typography variant="caption" color="text.secondary">
            Live · {prices?.length ?? 0} assets · Refreshes every 10s
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: "flex", gap: 2, mb: 3, overflowX: "auto", pb: 1 }}>
        {gainers.map(p => (
          <Card key={p.id} sx={{ minWidth: 180, flex: "0 0 auto", borderLeft: 3, borderColor: "success.main" }}>
            <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
              <Typography variant="body2" fontWeight={700}>{p.id}</Typography>
              <Typography variant="caption" color="text.secondary">{p.name}</Typography>
              <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
                <Typography variant="body2" fontWeight={600}>{fmtPrice(p.close)}</Typography>
                <Typography variant="body2" color="success.main" fontWeight={600}>+{p.change_pct.toFixed(2)}%</Typography>
              </Box>
            </CardContent>
          </Card>
        ))}
        {losers.map(p => (
          <Card key={p.id} sx={{ minWidth: 180, flex: "0 0 auto", borderLeft: 3, borderColor: "error.main" }}>
            <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
              <Typography variant="body2" fontWeight={700}>{p.id}</Typography>
              <Typography variant="caption" color="text.secondary">{p.name}</Typography>
              <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
                <Typography variant="body2" fontWeight={600}>{fmtPrice(p.close)}</Typography>
                <Typography variant="body2" color="error.main" fontWeight={600}>{p.change_pct.toFixed(2)}%</Typography>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Stocks" titleTypographyProps={{ variant: "h6", fontWeight: 700 }} action={<Chip label={`${stocks.length} assets`} size="small" />} sx={{ pb: 0 }} />
            <CardContent sx={{ p: 0 }}><TickerTable items={stocks} /></CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Cryptocurrency" titleTypographyProps={{ variant: "h6", fontWeight: 700 }} action={<Chip label={`${crypto.length}`} size="small" color="warning" />} sx={{ pb: 0 }} />
            <CardContent sx={{ p: 0 }}><TickerTable items={crypto} /></CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Commodities & ETFs" titleTypographyProps={{ variant: "h6", fontWeight: 700 }} action={<Chip label={`${commodities.length}`} size="small" color="success" />} sx={{ pb: 0 }} />
            <CardContent sx={{ p: 0 }}><TickerTable items={commodities} /></CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function TickerTable({ items }: { items: LatestPrice[] }) {
  return (
    <TableContainer sx={{ maxHeight: 500 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 700, bgcolor: "background.paper" }}>Symbol</TableCell>
            <TableCell sx={{ fontWeight: 700, bgcolor: "background.paper" }}>Name</TableCell>
            <TableCell align="right" sx={{ fontWeight: 700, bgcolor: "background.paper" }}>Price</TableCell>
            <TableCell align="right" sx={{ fontWeight: 700, bgcolor: "background.paper" }}>Change</TableCell>
            <TableCell align="right" sx={{ fontWeight: 700, bgcolor: "background.paper" }}>%</TableCell>
            <TableCell align="right" sx={{ fontWeight: 700, bgcolor: "background.paper" }}>Volume</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map(p => {
            const isUp = p.change >= 0;
            const color = isUp ? "success.main" : "error.main";
            return (
              <TableRow key={p.id + p.provider} hover sx={{ "&:last-child td": { border: 0 } }}>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                    <Typography variant="body2" fontWeight={700}>{p.id}</Typography>
                    <Chip label={p.exchange} size="small" variant="outlined" sx={{ height: 18, fontSize: 10 }} />
                  </Box>
                </TableCell>
                <TableCell><Typography variant="body2" noWrap sx={{ maxWidth: 180 }}>{p.name}</Typography></TableCell>
                <TableCell align="right"><Typography variant="body2" fontWeight={600}>{fmtPrice(p.close)}</Typography></TableCell>
                <TableCell align="right">
                  <Box sx={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 0.3, color }}>
                    {isUp ? <TrendingUpIcon sx={{ fontSize: 14 }} /> : <TrendingDownIcon sx={{ fontSize: 14 }} />}
                    <Typography variant="body2">{isUp ? "+" : ""}{p.change.toFixed(2)}</Typography>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" sx={{ color, fontWeight: 600 }}>{isUp ? "+" : ""}{p.change_pct.toFixed(2)}%</Typography>
                </TableCell>
                <TableCell align="right"><Typography variant="body2" color="text.secondary">{fmt(p.volume)}</Typography></TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
