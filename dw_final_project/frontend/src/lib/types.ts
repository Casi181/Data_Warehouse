export interface PaginatedResponse<T = string> {
  items: T[];
  offset: number;
  limit: number;
  total: number;
  has_next: boolean;
}

export interface AssetDetail {
  id: string;
  system_time: string;
  name: string;
  description: string;
  attributes: Record<string, string>;
}

export interface DataSourceDetail {
  id: string;
  system_time: string;
  name: string;
  description: string;
  attributes: string[];
}

export interface TimeSeriesRecord {
  businessDate: string;
  values: Record<string, number | string>;
}

export interface TimeSeriesResponse {
  data: {
    assetId: string;
    datasourceId: string;
    records: TimeSeriesRecord[];
  };
  attributes?: string[];
}

export interface IngestionRequest {
  provider: string;
  dataset_codes: string[];
  period?: string;
}

export interface IngestionResult {
  fetched: number;
  stored: number;
  skipped: number;
  errors: number;
}

export interface TotalsRecord {
  asset_id: string;
  business_date_year: number;
  cnt: number;
}

export interface PredictionRecord {
  seconds: number;
  open: number;
  prediction: number;
}

export interface SparkJobResult {
  status: string;
  rows_processed: number;
  message: string;
  metrics?: Record<string, number | string | string[]>;
}

export interface LatestPrice {
  id: string;
  name: string;
  asset_class: string;
  region: string;
  exchange: string;
  provider: string;
  close: number;
  change: number;
  change_pct: number;
  date: string;
  open: number;
  high: number;
  low: number;
  volume: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}
