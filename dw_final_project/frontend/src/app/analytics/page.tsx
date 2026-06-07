"use client";
import React, { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import Chip from "@mui/material/Chip";
import BarChart from "@/components/data/BarChart";
import LineChart from "@/components/data/LineChart";
import DataTable from "@/components/data/DataTable";
import LoadingOverlay from "@/components/common/LoadingOverlay";
import EmptyState from "@/components/common/EmptyState";
import ErrorAlert from "@/components/common/ErrorAlert";
import { useTotals, usePredictions } from "@/lib/hooks/useAnalytics";
import { runAggregation, runPrediction } from "@/lib/api";
import { useAssets } from "@/lib/hooks/useAssets";
import { useDataSources } from "@/lib/hooks/useDataSources";
import AssetSelector from "@/components/forms/AssetSelector";
import SourceSelector from "@/components/forms/SourceSelector";
import type { SparkJobResult } from "@/lib/types";

export default function AnalyticsPage() {
  const [tab, setTab] = useState(0);
  const [jobLoading, setJobLoading] = useState(false);
  const [jobMessage, setJobMessage] = useState<string | null>(null);
  const [lastJobResult, setLastJobResult] = useState<SparkJobResult | null>(null);
  const [predAsset, setPredAsset] = useState<string | null>(null);
  const [predSource, setPredSource] = useState("YFINANCE");

  const { data: assetsData } = useAssets(0, 200);
  const { data: sourcesData } = useDataSources(0, 100);
  const assetIds = (assetsData?.items ?? []) as string[];
  const sourceIds = (sourcesData?.items ?? []) as string[];

  // Auto-select first asset once loaded
  React.useEffect(() => {
    if (!predAsset && assetIds.length > 0) {
      setPredAsset(assetIds.find(id => id === "AAPL") ?? assetIds[0]);
    }
  }, [assetIds, predAsset]);

  const { data: totals, error: totalsError, isLoading: totalsLoading, mutate: mutateTotals } = useTotals();
  const { data: predictions, error: predsError, isLoading: predsLoading, mutate: mutatePreds } = usePredictions();

  const handleRunAggregation = async () => {
    setJobLoading(true);
    setJobMessage(null);
    setLastJobResult(null);
    try {
      const res = await runAggregation("YFINANCE");
      setJobMessage(`${res.status}: ${res.message}`);
      setLastJobResult(res);
      mutateTotals();
    } catch (e: any) {
      setJobMessage(`Error: ${e.message}`);
    } finally {
      setJobLoading(false);
    }
  };

  const handleRunPrediction = async () => {
    if (!predAsset || !predSource) return;
    setJobLoading(true);
    setJobMessage(null);
    setLastJobResult(null);
    try {
      const res = await runPrediction(predAsset, predSource);
      setJobMessage(`${res.status}: ${res.message}`);
      setLastJobResult(res);
      mutatePreds();
    } catch (e: any) {
      setJobMessage(`Error: ${e.message}`);
    } finally {
      setJobLoading(false);
    }
  };

  const metrics = lastJobResult?.metrics;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Aggregation" />
        <Tab label="Predictions" />
      </Tabs>

      {jobMessage && (
        <Alert severity={jobMessage.startsWith("Error") ? "error" : "info"} sx={{ mb: 2 }} onClose={() => setJobMessage(null)}>
          {jobMessage}
        </Alert>
      )}

      {tab === 0 && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              onClick={handleRunAggregation}
              disabled={jobLoading}
              startIcon={jobLoading ? <CircularProgress size={20} /> : undefined}
            >
              Run Aggregation
            </Button>
          </Box>

          {totalsLoading && <LoadingOverlay />}
          {totalsError && <ErrorAlert message={totalsError.message} />}
          {!totalsLoading && totals && totals.length > 0 && (
            <>
              <Card sx={{ mb: 3 }}>
                <CardHeader title="Record Counts by Asset and Year" />
                <CardContent>
                  <BarChart
                    data={totals.map((t) => ({
                      label: `${t.asset_id} (${t.business_date_year})`,
                      count: t.cnt,
                    }))}
                    xKey="label"
                    bars={[{ key: "count", color: "#1976d2", name: "Records" }]}
                    height={350}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader title="Raw Totals" />
                <CardContent>
                  <DataTable
                    columns={[
                      { id: "asset_id", label: "Asset" },
                      { id: "business_date_year", label: "Year", numeric: true },
                      { id: "cnt", label: "Count", numeric: true },
                    ]}
                    rows={totals}
                  />
                </CardContent>
              </Card>
            </>
          )}
          {!totalsLoading && (!totals || totals.length === 0) && (
            <EmptyState title="No aggregation data" message="Run an aggregation job to see results." />
          )}
        </Box>
      )}

      {tab === 1 && (
        <Box>
          <Box sx={{ display: "flex", gap: 2, alignItems: "flex-end", mb: 2, flexWrap: "wrap" }}>
            <AssetSelector assets={assetIds} value={predAsset} onChange={setPredAsset} />
            <SourceSelector sources={sourceIds} value={predSource} onChange={setPredSource} />
            <Button
              variant="contained"
              onClick={handleRunPrediction}
              disabled={jobLoading || !predAsset || !predSource}
              startIcon={jobLoading ? <CircularProgress size={20} /> : undefined}
            >
              Run Prediction
            </Button>
          </Box>

          {/* Model Evaluation Metrics Card */}
          {metrics && (
            <Card sx={{ mb: 3 }}>
              <CardHeader
                title="Model Evaluation Metrics"
                action={
                  <Chip
                    label={String(metrics.model_type || "GBTRegressor")}
                    color="primary"
                    size="small"
                  />
                }
              />
              <CardContent>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>RMSE (Root Mean Squared Error)</TableCell>
                      <TableCell align="right">{Number(metrics.rmse).toFixed(6)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>MAE (Mean Absolute Error)</TableCell>
                      <TableCell align="right">{Number(metrics.mae).toFixed(6)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>R-squared</TableCell>
                      <TableCell align="right">{Number(metrics.r2).toFixed(6)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Training Samples</TableCell>
                      <TableCell align="right">{metrics.train_count}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Test Samples</TableCell>
                      <TableCell align="right">{metrics.test_count}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Cross-Validation Folds</TableCell>
                      <TableCell align="right">{metrics.cv_folds}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Best Max Depth</TableCell>
                      <TableCell align="right">{metrics.best_max_depth}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Best Max Iterations</TableCell>
                      <TableCell align="right">{metrics.best_max_iter}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Best Step Size</TableCell>
                      <TableCell align="right">{metrics.best_step_size}</TableCell>
                    </TableRow>
                    {Array.isArray(metrics.features) && (
                      <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Features ({(metrics.features as string[]).length})</TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", justifyContent: "flex-end" }}>
                            {(metrics.features as string[]).map((f) => (
                              <Chip key={f} label={f} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {predsLoading && <LoadingOverlay />}
          {predsError && <ErrorAlert message={predsError.message} />}
          {!predsLoading && predictions && predictions.length > 0 && (
            <>
              <Card sx={{ mb: 3 }}>
                <CardHeader title="Actual vs Predicted (Open Price)" />
                <CardContent>
                  <LineChart
                    data={predictions}
                    xKey="seconds"
                    lines={[
                      { key: "open", color: "#1976d2", name: "Actual Open" },
                      { key: "prediction", color: "#f44336", name: "Predicted" },
                    ]}
                    height={400}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader title="Prediction Results" />
                <CardContent>
                  <DataTable
                    columns={[
                      { id: "seconds", label: "Seconds", numeric: true },
                      { id: "open", label: "Open", numeric: true },
                      { id: "prediction", label: "Prediction", numeric: true },
                    ]}
                    rows={predictions}
                  />
                </CardContent>
              </Card>
            </>
          )}
          {!predsLoading && (!predictions || predictions.length === 0) && (
            <EmptyState title="No predictions" message="Run a prediction job to see results." />
          )}
        </Box>
      )}
    </Box>
  );
}
