import useSWR from "swr";
import { getTotals, getPredictions } from "../api";

export function useTotals() {
  return useSWR("/analytics/totals", getTotals);
}

export function usePredictions() {
  return useSWR("/analytics/predictions", getPredictions);
}
