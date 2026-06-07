"use client";
import React, { useState } from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import Collapse from "@mui/material/Collapse";

interface Column {
  id: string;
  label: string;
  numeric?: boolean;
}

interface Props {
  columns: Column[];
  rows: Record<string, any>[];
  expandable?: boolean;
  renderExpanded?: (row: Record<string, any>) => React.ReactNode;
}

type Order = "asc" | "desc";

export default function DataTable({ columns, rows, expandable, renderExpanded }: Props) {
  const [order, setOrder] = useState<Order>("asc");
  const [orderBy, setOrderBy] = useState<string>(columns[0]?.id || "");
  const [filter, setFilter] = useState("");
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const handleSort = (colId: string) => {
    setOrder(orderBy === colId && order === "asc" ? "desc" : "asc");
    setOrderBy(colId);
  };

  const filtered = rows.filter((row) =>
    Object.values(row).some((v) =>
      String(v).toLowerCase().includes(filter.toLowerCase())
    )
  );

  const sorted = [...filtered].sort((a, b) => {
    const aVal = a[orderBy];
    const bVal = b[orderBy];
    if (aVal == null) return 1;
    if (bVal == null) return -1;
    const cmp = typeof aVal === "number" ? aVal - bVal : String(aVal).localeCompare(String(bVal));
    return order === "asc" ? cmp : -cmp;
  });

  return (
    <Paper sx={{ width: "100%", overflow: "hidden" }}>
      <Box sx={{ p: 2 }}>
        <TextField
          size="small"
          placeholder="Filter..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          fullWidth
        />
      </Box>
      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {expandable && <TableCell sx={{ width: 48 }} />}
              {columns.map((col) => (
                <TableCell key={col.id} align={col.numeric ? "right" : "left"}>
                  <TableSortLabel
                    active={orderBy === col.id}
                    direction={orderBy === col.id ? order : "asc"}
                    onClick={() => handleSort(col.id)}
                  >
                    {col.label}
                  </TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sorted.map((row, idx) => (
              <React.Fragment key={idx}>
                <TableRow hover>
                  {expandable && (
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => setExpandedRow(expandedRow === idx ? null : idx)}
                      >
                        {expandedRow === idx ? (
                          <KeyboardArrowUpIcon />
                        ) : (
                          <KeyboardArrowDownIcon />
                        )}
                      </IconButton>
                    </TableCell>
                  )}
                  {columns.map((col) => (
                    <TableCell key={col.id} align={col.numeric ? "right" : "left"}>
                      {row[col.id] != null ? String(row[col.id]) : "-"}
                    </TableCell>
                  ))}
                </TableRow>
                {expandable && renderExpanded && (
                  <TableRow>
                    <TableCell colSpan={columns.length + 1} sx={{ py: 0 }}>
                      <Collapse in={expandedRow === idx} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 2 }}>{renderExpanded(row)}</Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
