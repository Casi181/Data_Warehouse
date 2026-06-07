"use client";
import React, { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Button from "@mui/material/Button";
import AssetSelector from "@/components/forms/AssetSelector";
import SourceSelector from "@/components/forms/SourceSelector";
import DateRangePicker from "@/components/forms/DateRangePicker";
import LineChart from "@/components/data/LineChart";
import DataTable from "@/components/data/DataTable";
import ExpandableRow from "@/components/data/ExpandableRow";
import LoadingOverlay from "@/components/common/LoadingOverlay";
import EmptyState from "@/components/common/EmptyState";
import ErrorAlert from "@/components/common/ErrorAlert";
import { useAssets } from "@/lib/hooks/useAssets";
import { useDataSources } from "@/lib/hooks/useDataSources";
import { useTimeSeries } from "@/lib/hooks/useTimeSeries";

export default function ExplorerPage() {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState("");
  const [startDate, setStartDate] = useState("2025-06-01");
  const [endDate, setEndDate] = useState("2026-06-07");
  const [fetchTrigger, setFetchTrigger] = useState(false);

  const { data: assetsData } = useAssets(0, 100);
  const { data: sourcesData } = useDataSources(0, 100);

  const assetIds = (assetsData?.items ?? []) as string[];
  const sourceIds = (sourcesData?.items ?? []) as string[];

  const { data: tsData, error, isLoading } = useTimeSeries(
    fetchTrigger ? selectedAsset : null,
    fetchTrigger ? selectedSource : null,
    fetchTrigger ? startDate : null,
    fetchTrigger ? endDate : null,
    true
  );

  const handleFetch = () => {
    if (selectedAsset && selectedSource) {
      setFetchTrigger(false);
      setTimeout(() => setFetchTrigger(true), 0);
    }
  };

  const records = tsData?.data?.records ?? [];
  const chartData: Record<string, any>[] = [...records].reverse().map((r) => ({
    date: r.businessDate,
    ...Object.fromEntries(
      Object.entries(r.values).filter(([_, v]) => typeof v === "number")
    ),
  }));

  const tableColumns = [
    { id: "businessDate", label: "Date" },
    ...Object.keys(records[0]?.values ?? {}).map((k) => ({
      id: k,
      label: k,
      numeric: typeof records[0]?.values[k] === "number",
    })),
  ];

  const tableRows = records.map((r) => ({
    businessDate: r.businessDate,
    ...r.values,
    _raw: r.values,
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Time Series Explorer
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "flex-end" }}>
            <AssetSelector
              assets={assetIds}
              value={selectedAsset}
              onChange={setSelectedAsset}
            />
            <SourceSelector
              sources={sourceIds}
              value={selectedSource}
              onChange={setSelectedSource}
            />
            <DateRangePicker
              startDate={startDate}
              endDate={endDate}
              onStartChange={setStartDate}
              onEndChange={setEndDate}
            />
            <Button
              variant="contained"
              onClick={handleFetch}
              disabled={!selectedAsset || !selectedSource}
            >
              Fetch
            </Button>
          </Box>
        </CardContent>
      </Card>

      {isLoading && <LoadingOverlay message="Loading time series data..." />}
      {error && <ErrorAlert message={error.message} />}

      {!isLoading && records.length > 0 && (
        <>
          <Card sx={{ mb: 3 }}>
            <CardHeader title="Price Chart" />
            <CardContent>
              <LineChart
                data={chartData}
                xKey="date"
                lines={[
                  { key: "Close", color: "#1976d2", name: "Close" },
                  { key: "Open", color: "#ff9800", name: "Open" },
                  { key: "High", color: "#4caf50", name: "High" },
                  { key: "Low", color: "#f44336", name: "Low" },
                ].filter((l) => chartData[0]?.[l.key] !== undefined)}
                height={400}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Records" />
            <CardContent>
              <DataTable
                columns={tableColumns}
                rows={tableRows}
                expandable
                renderExpanded={(row) => <ExpandableRow data={row._raw} />}
              />
            </CardContent>
          </Card>
        </>
      )}

      {!isLoading && !error && records.length === 0 && fetchTrigger && (
        <EmptyState title="No data" message="No records found for the selected parameters." />
      )}
    </Box>
  );
}
