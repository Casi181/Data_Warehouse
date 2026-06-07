"use client";
import React from "react";
import Link from "next/link";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import StorageIcon from "@mui/icons-material/Storage";
import Box from "@mui/material/Box";

interface Props {
  id: string;
  name?: string;
  description?: string;
}

export default function SourceCard({ id, name, description }: Props) {
  return (
    <Card>
      <CardActionArea component={Link} href={`/data-sources/${encodeURIComponent(id)}`}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
            <StorageIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              {name || id}
            </Typography>
          </Box>
          {description && (
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          )}
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: "block" }}>
            ID: {id}
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
