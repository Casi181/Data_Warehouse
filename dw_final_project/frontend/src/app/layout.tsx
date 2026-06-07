import React from "react";
import type { Metadata } from "next";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import theme from "@/lib/theme";
import AppBar from "@/components/layout/AppBar";
import DrawerNav from "@/components/layout/DrawerNav";
import PageContainer from "@/components/layout/PageContainer";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Casi - Financial Data Warehouse",
  description: "Acme Ltd Financial Data Warehouse Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Box sx={{ display: "flex" }}>
            <AppBar />
            <DrawerNav />
            <PageContainer>{children}</PageContainer>
          </Box>
        </ThemeProvider>
      </body>
    </html>
  );
}
