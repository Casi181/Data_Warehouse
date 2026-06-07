"use client";
import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import MuiBreadcrumbs from "@mui/material/Breadcrumbs";
import MuiLink from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import HomeIcon from "@mui/icons-material/Home";

export default function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <MuiBreadcrumbs sx={{ mb: 2 }}>
      <MuiLink
        component={Link}
        href="/"
        underline="hover"
        color="inherit"
        sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
      >
        <HomeIcon fontSize="small" />
        Dashboard
      </MuiLink>
      {segments.map((seg, idx) => {
        const href = "/" + segments.slice(0, idx + 1).join("/");
        const isLast = idx === segments.length - 1;
        const label = decodeURIComponent(seg)
          .replace(/[-_]/g, " ")
          .replace(/\b\w/g, (c) => c.toUpperCase());

        return isLast ? (
          <Typography key={href} color="text.primary" fontWeight={500}>
            {label}
          </Typography>
        ) : (
          <MuiLink
            key={href}
            component={Link}
            href={href}
            underline="hover"
            color="inherit"
          >
            {label}
          </MuiLink>
        );
      })}
    </MuiBreadcrumbs>
  );
}
