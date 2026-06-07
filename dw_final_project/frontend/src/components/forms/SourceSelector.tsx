"use client";
import React from "react";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";

interface Props {
  sources: string[];
  value: string;
  onChange: (val: string) => void;
}

export default function SourceSelector({ sources, value, onChange }: Props) {
  return (
    <FormControl size="small" sx={{ minWidth: 200 }}>
      <InputLabel>Data Source</InputLabel>
      <Select
        value={value}
        label="Data Source"
        onChange={(e) => onChange(e.target.value)}
      >
        {sources.map((s) => (
          <MenuItem key={s} value={s}>
            {s}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
