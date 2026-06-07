"use client";
import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import Drawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import DashboardIcon from "@mui/icons-material/Dashboard";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import StorageIcon from "@mui/icons-material/Storage";
import ExploreIcon from "@mui/icons-material/Explore";
import BarChartIcon from "@mui/icons-material/BarChart";
import SmartToyIcon from "@mui/icons-material/SmartToy";

const DRAWER_WIDTH = 280;

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const sections: { title: string; items: NavItem[] }[] = [
  {
    title: "Overview",
    items: [
      { label: "Dashboard", href: "/", icon: <DashboardIcon /> },
    ],
  },
  {
    title: "Data",
    items: [
      { label: "Assets", href: "/assets", icon: <AccountBalanceIcon /> },
      { label: "Data Sources", href: "/data-sources", icon: <StorageIcon /> },
      { label: "Explorer", href: "/explorer", icon: <ExploreIcon /> },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Analytics", href: "/analytics", icon: <BarChartIcon /> },
    ],
  },
  {
    title: "AI",
    items: [
      { label: "Assistant", href: "/assistant", icon: <SmartToyIcon /> },
    ],
  },
];

export default function DrawerNav() {
  const pathname = usePathname();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          borderRight: "1px solid",
          borderColor: "divider",
        },
      }}
    >
      <Toolbar />
      {sections.map((section, idx) => (
        <React.Fragment key={section.title}>
          {idx > 0 && <Divider />}
          <Typography
            variant="overline"
            sx={{ px: 2, pt: 2, pb: 0.5, color: "text.secondary" }}
          >
            {section.title}
          </Typography>
          <List disablePadding>
            {section.items.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <ListItem key={item.href} disablePadding>
                  <ListItemButton
                    component={Link}
                    href={item.href}
                    selected={active}
                    sx={{
                      mx: 1,
                      borderRadius: 2,
                      "&.Mui-selected": {
                        bgcolor: "primary.main",
                        color: "white",
                        "&:hover": { bgcolor: "primary.dark" },
                        "& .MuiListItemIcon-root": { color: "white" },
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </React.Fragment>
      ))}
    </Drawer>
  );
}
