"use client";
import React from "react";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";

interface Props {
  assets: string[];
  value: string | null;
  onChange: (val: string | null) => void;
  loading?: boolean;
}

export default function AssetSelector({ assets, value, onChange, loading }: Props) {
  return (
    <Autocomplete
      options={assets}
      value={value}
      onChange={(_, newVal) => onChange(newVal)}
      loading={loading}
      size="small"
      sx={{ minWidth: 250 }}
      renderInput={(params) => (
        <TextField {...params} label="Select Asset" variant="outlined" />
      )}
    />
  );
}
