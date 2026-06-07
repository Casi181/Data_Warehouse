import useSWR from "swr";
import { getAssets, getAssetDetails } from "../api";

export function useAssets(offset = 0, limit = 20) {
  return useSWR(
    [`/assets`, offset, limit],
    () => getAssets(offset, limit)
  );
}

export function useAssetDetails(assetId: string | null) {
  return useSWR(
    assetId ? [`/assets/${assetId}`] : null,
    () => getAssetDetails(assetId!)
  );
}
