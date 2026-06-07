const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || err.error || "API Error");
  }
  return res.json();
}

export async function getAssets(offset = 0, limit = 20) {
  return fetchApi<import("./types").PaginatedResponse>(
    `/assets?offset=${offset}&limit=${limit}`
  );
}

export async function getAssetDetails(assetId: string) {
  return fetchApi<import("./types").AssetDetail[]>(`/assets/${assetId}`);
}

export async function getDataSources(offset = 0, limit = 20) {
  return fetchApi<import("./types").PaginatedResponse>(
    `/data-sources?offset=${offset}&limit=${limit}`
  );
}

export async function getDataSourceDetails(sourceId: string) {
  return fetchApi<import("./types").DataSourceDetail[]>(
    `/data-sources/${sourceId}`
  );
}

export async function getTimeSeries(
  assetId: string,
  dataSourceId: string,
  startDate: string,
  endDate: string,
  includeAttributes = false
) {
  const params = new URLSearchParams({
    assetId,
    dataSourceId,
    startBusinessDate: startDate,
    endBusinessDate: endDate,
    includeAttributes: String(includeAttributes),
  });
  return fetchApi<import("./types").TimeSeriesResponse>(`/data?${params}`);
}

export async function triggerIngestion(
  request: import("./types").IngestionRequest
) {
  return fetchApi<import("./types").IngestionResult>("/ingest", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function runAggregation(dataSourceId: string) {
  return fetchApi<import("./types").SparkJobResult>("/analytics/aggregate", {
    method: "POST",
    body: JSON.stringify({ data_source_id: dataSourceId }),
  });
}

export async function runPrediction(
  assetId: string,
  dataSourceId: string
) {
  return fetchApi<import("./types").SparkJobResult>("/analytics/predict", {
    method: "POST",
    body: JSON.stringify({ asset_id: assetId, data_source_id: dataSourceId }),
  });
}

export async function getTotals() {
  return fetchApi<import("./types").TotalsRecord[]>("/analytics/totals");
}

export async function getPredictions() {
  return fetchApi<import("./types").PredictionRecord[]>(
    "/analytics/predictions"
  );
}

export async function getLatestPrices() {
  return fetchApi<import("./types").LatestPrice[]>("/data/latest-prices");
}
