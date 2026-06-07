"use client";
import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import SourceCard from "@/components/cards/SourceCard";
import LoadingOverlay from "@/components/common/LoadingOverlay";
import EmptyState from "@/components/common/EmptyState";
import ErrorAlert from "@/components/common/ErrorAlert";
import { useDataSources } from "@/lib/hooks/useDataSources";

export default function DataSourcesPage() {
  const { data, error, isLoading } = useDataSources(0, 100);

  if (isLoading) return <LoadingOverlay message="Loading data sources..." />;
  if (error) return <ErrorAlert message={error.message} />;

  const items = (data?.items ?? []) as string[];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Data Sources
      </Typography>

      {items.length === 0 ? (
        <EmptyState title="No data sources" message="Ingest data to see data sources here." />
      ) : (
        <Grid container spacing={2}>
          {items.map((id) => (
            <Grid item xs={12} sm={6} md={4} key={id}>
              <SourceCard id={id} name={id} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
