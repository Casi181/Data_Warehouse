"use client";
import React from "react";
import { useParams } from "next/navigation";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import Chip from "@mui/material/Chip";
import LoadingOverlay from "@/components/common/LoadingOverlay";
import ErrorAlert from "@/components/common/ErrorAlert";
import EmptyState from "@/components/common/EmptyState";
import { useAssetDetails } from "@/lib/hooks/useAssets";

export default function AssetDetailPage() {
  const params = useParams();
  const assetId = decodeURIComponent(params.assetId as string);
  const { data: versions, error, isLoading } = useAssetDetails(assetId);

  if (isLoading) return <LoadingOverlay message="Loading asset details..." />;
  if (error) return <ErrorAlert message={error.message} />;
  if (!versions || versions.length === 0) return <EmptyState title="Asset not found" />;

  const latest = versions[0];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {latest.name || assetId}
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {assetId}
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} md={7}>
          <Card>
            <CardHeader
              title="Current Version"
              action={
                <Chip
                  label={latest.attributes?.deleted === "true" ? "Deleted" : "Active"}
                  color={latest.attributes?.deleted === "true" ? "error" : "success"}
                  size="small"
                />
              }
            />
            <CardContent>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600, width: 150 }}>ID</TableCell>
                    <TableCell>{latest.id}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                    <TableCell>{latest.name}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
                    <TableCell>{latest.description}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>System Time</TableCell>
                    <TableCell>{new Date(latest.system_time).toLocaleString()}</TableCell>
                  </TableRow>
                  {Object.entries(latest.attributes).map(([k, v]) => (
                    <TableRow key={k}>
                      <TableCell sx={{ fontWeight: 600 }}>{k}</TableCell>
                      <TableCell>{v}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card>
            <CardHeader title="Version History" />
            <CardContent>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {versions.map((v, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: 2,
                      pb: 2,
                      borderBottom: idx < versions.length - 1 ? "1px solid" : "none",
                      borderColor: "divider",
                    }}
                  >
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: "50%",
                        bgcolor: idx === 0 ? "primary.main" : "grey.400",
                        mt: 0.5,
                        flexShrink: 0,
                      }}
                    />
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        {new Date(v.system_time).toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {v.name} - {v.description || "No description"}
                      </Typography>
                      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
                        {Object.entries(v.attributes).map(([k, val]) => (
                          <Chip
                            key={k}
                            label={`${k}: ${val}`}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: 11 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
