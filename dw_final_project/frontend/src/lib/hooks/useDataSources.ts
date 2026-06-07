import useSWR from "swr";
import { getDataSources, getDataSourceDetails } from "../api";

export function useDataSources(offset = 0, limit = 20) {
  return useSWR(
    [`/data-sources`, offset, limit],
    () => getDataSources(offset, limit)
  );
}

export function useDataSourceDetails(sourceId: string | null) {
  return useSWR(
    sourceId ? [`/data-sources/${sourceId}`] : null,
    () => getDataSourceDetails(sourceId!)
  );
}
