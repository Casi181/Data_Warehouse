"use client";
import React, { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import AssetCard from "@/components/cards/AssetCard";
import LoadingOverlay from "@/components/common/LoadingOverlay";
import EmptyState from "@/components/common/EmptyState";
import ErrorAlert from "@/components/common/ErrorAlert";
import { useAssets } from "@/lib/hooks/useAssets";

const CRYPTO_IDS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD", "BTC/USD", "ETH/USD"];
const COMMODITY_IDS = ["GC=F", "SI=F", "CL=F", "GLD"];
const INDEX_IDS = ["SPY", "QQQ"];

function getAssetType(id: string): string {
  if (CRYPTO_IDS.includes(id)) return "crypto";
  if (COMMODITY_IDS.includes(id)) return "commodity";
  if (INDEX_IDS.includes(id)) return "index";
  return "stock";
}

export default function AssetsPage() {
  const [search, setSearch] = useState("");
  const [limit, setLimit] = useState(20);
  const { data, error, isLoading } = useAssets(0, limit);

  if (isLoading) return <LoadingOverlay message="Loading assets..." />;
  if (error) return <ErrorAlert message={error.message} />;

  const items = (data?.items ?? []) as string[];
  const filtered = items.filter((id) =>
    id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">Assets</Typography>
        <Typography variant="body2" color="text.secondary">
          {data?.total ?? 0} total
        </Typography>
      </Box>

      <TextField
        fullWidth
        size="small"
        placeholder="Search assets..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        sx={{ mb: 3 }}
      />

      {filtered.length === 0 ? (
        <EmptyState title="No assets found" message="No assets match your search criteria." />
      ) : (
        <>
          <Grid container spacing={2}>
            {filtered.map((id) => (
              <Grid item xs={12} sm={6} md={4} key={id}>
                <AssetCard
                  id={id}
                  name={id}
                  type={getAssetType(id)}
                />
              </Grid>
            ))}
          </Grid>
          {data?.has_next && (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
              <Button variant="outlined" onClick={() => setLimit((p) => p + 20)}>
                Load More
              </Button>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}
