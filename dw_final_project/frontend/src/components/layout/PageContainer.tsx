"use client";
import React from "react";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Breadcrumbs from "./Breadcrumbs";

const DRAWER_WIDTH = 280;

interface Props {
  children: React.ReactNode;
}

export default function PageContainer({ children }: Props) {
  return (
    <Box
      component="main"
      sx={{
        flexGrow: 1,
        ml: `${DRAWER_WIDTH}px`,
        p: 3,
        maxWidth: "xl",
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <Toolbar />
      <Breadcrumbs />
      {children}
    </Box>
  );
}
