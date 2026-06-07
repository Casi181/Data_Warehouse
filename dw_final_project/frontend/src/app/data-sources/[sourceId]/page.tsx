"use client";
import React from "react";
import { useParams } from "next/navigation";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
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
import { useDataSourceDetails } from "@/lib/hooks/useDataSources";

export default function DataSourceDetailPage() {
  const params = useParams();
  const sourceId = decodeURIComponent(params.sourceId as string);
  const { data: versions, error, isLoading } = useDataSourceDetails(sourceId);

  if (isLoading) return <LoadingOverlay />;
  if (error) return <ErrorAlert message={error.message} />;
  if (!versions || versions.length === 0) return <EmptyState title="Data source not found" />;

  const latest = versions[0];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {latest.name || sourceId}
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardHeader title="Details" />
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
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Supported Attributes" />
        <CardContent>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {latest.attributes.map((attr) => (
              <Chip key={attr} label={attr} color="primary" variant="outlined" />
            ))}
          </Box>
          {latest.attributes.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No attributes defined.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
