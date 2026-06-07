"use client";
import React from "react";
import Link from "next/link";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";

interface Props {
  id: string;
  name?: string;
  type?: string;
}

function getTypeColor(type?: string): "primary" | "warning" | "success" | "info" | "secondary" | "default" {
  switch (type?.toLowerCase()) {
    case "stock":
      return "primary";
    case "crypto":
      return "warning";
    case "commodity":
      return "success";
    case "index":
      return "info";
    case "etf":
      return "secondary";
    default:
      return "default";
  }
}

export default function AssetCard({ id, name, type }: Props) {
  return (
    <Card>
      <CardActionArea component={Link} href={`/assets/${encodeURIComponent(id)}`}>
        <CardContent>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
            <Typography variant="h6" fontWeight={600} noWrap sx={{ maxWidth: "70%" }}>
              {id}
            </Typography>
            {type && (
              <Chip label={type} size="small" color={getTypeColor(type)} variant="outlined" />
            )}
          </Box>
          <Typography variant="body2" color="text.secondary" noWrap>
            {name || id}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: "block" }}>
            {id}
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
