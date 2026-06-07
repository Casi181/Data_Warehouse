import useSWR from "swr";
import { getTimeSeries } from "../api";

export function useTimeSeries(
  assetId: string | null,
  dataSourceId: string | null,
  startDate: string | null,
  endDate: string | null,
  includeAttributes = false
) {
  const ready = assetId && dataSourceId && startDate && endDate;
  return useSWR(
    ready
      ? [`/data`, assetId, dataSourceId, startDate, endDate, includeAttributes]
      : null,
    () =>
      getTimeSeries(assetId!, dataSourceId!, startDate!, endDate!, includeAttributes)
  );
}
