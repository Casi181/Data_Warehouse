# CASI — Financial Data Warehouse

A full-stack data warehouse system for ingesting, storing, analyzing, and predicting financial time-series data. Built with **FastAPI**, **Apache Cassandra**, **Apache Spark ML**, and **Next.js**.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            Docker Compose                                 │
├────────────┬────────────┬──────────────────┬────────────────────────────┤
│  Frontend  │  Backend   │    Cassandra     │       Spark Master         │
│  (Next.js) │  (FastAPI) │   (Storage)      │       (Analytics)          │
│  :3000     │  :8000     │   :9042          │       :7077 / :8080        │
└─────┬──────┴─────┬──────┴────────┬─────────┴──────────────┬─────────────┘
      │            │               │                         │
      │  REST API  │   CQL Driver  │    Spark-Cassandra      │
      ▼            ▼               ▼       Connector         ▼
┌──────────┐ ┌──────────────────────────────────────────────────────────┐
│  Browser │ │                     Data Flow                             │
└──────────┘ │                                                          │
             │  ┌─────────┐    ┌─────────────┐    ┌──────────┐         │
             │  │Extractor│───▶│ Transformer │───▶│  Loader  │         │
             │  │(yfinance│    │ (normalize) │    │(dedupe + │         │
             │  │ bitfinex│    └─────────────┘    │ upsert)  │         │
             │  │ nasdaq) │                       └─────┬────┘         │
             │  └─────────┘                             │              │
             │                                          ▼              │
             │  ┌───────────────────────────────────────────────┐      │
             │  │            Cassandra (Bi-temporal)             │      │
             │  │  asset | data_source | data | totals | reg_*  │      │
             │  └───────────────────────────┬───────────────────┘      │
             │                              │                          │
             │                    Spark ML Pipeline                     │
             │              (Aggregation + GBT Prediction              │
             │               with 3-fold Cross-Validation)             │
             └──────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Storage | Apache Cassandra | Wide-column store ideal for time-series; bi-temporal model (business_date + system_date) enables full audit trail |
| API | FastAPI | Async-first, auto-generated OpenAPI docs, dependency injection |
| ML | Spark MLlib (GBT) | Distributed training with cross-validation; captures non-linear price dynamics |
| Frontend | Next.js + MUI | Server-side rendering, component library |
| AI Assist | MCP Server | Model Context Protocol tools for LLM-driven financial queries |

---

## Setup Instructions

### Prerequisites

- Docker & Docker Compose
- (Optional for local dev) Python 3.12+, Node.js 18+

### Quick Start (Docker)

```bash
cd dw_final_project
docker compose up --build
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Spark Master UI**: http://localhost:8080

On first boot the backend automatically ingests ~41 tickers (stocks, crypto, commodities, ETFs) from Yahoo Finance and Bitfinex.

### Local Development (without Docker)

```bash
# 1. Start Cassandra (or point to an existing instance)
docker run -d --name cassandra -p 9042:9042 cassandra:5.0

# 2. Backend
cd dw_final_project/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Frontend
cd dw_final_project/frontend
npm install
npm run dev
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CASSANDRA_HOSTS` | `localhost` | Comma-separated Cassandra contact points |
| `CASSANDRA_PORT` | `9042` | CQL native transport port |
| `CASSANDRA_KEYSPACE` | `acme_dw` | Target keyspace |
| `SPARK_MASTER` | `spark://localhost:7077` | Spark master URL |

---

## Sample API Calls

### List all assets
```bash
curl http://localhost:8000/api/v1/assets?offset=0&limit=10
```

### Get asset details
```bash
curl http://localhost:8000/api/v1/assets/AAPL
```

### Get latest prices (dashboard ticker feed)
```bash
curl http://localhost:8000/api/v1/data/latest-prices
```

### Query time-series data
```bash
curl "http://localhost:8000/api/v1/data?asset_id=AAPL&data_source_id=YFINANCE&start=2024-01-01&end=2024-12-31"
```

### Trigger manual ingestion
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "YFINANCE",
    "dataset_codes": ["AAPL", "MSFT"],
    "period": "1y"
  }'
```

### Run Spark aggregation
```bash
curl -X POST http://localhost:8000/api/v1/analytics/aggregate \
  -H "Content-Type: application/json" \
  -d '{"data_source_id": "YFINANCE"}'
```

### Run Spark ML prediction (with cross-validation)
```bash
curl -X POST http://localhost:8000/api/v1/analytics/predict \
  -H "Content-Type: application/json" \
  -d '{"asset_id": "AAPL", "data_source_id": "YFINANCE"}'
```

### Get prediction results
```bash
curl http://localhost:8000/api/v1/analytics/predictions
```

### List data sources
```bash
curl http://localhost:8000/api/v1/data-sources
```

---

## Data Flow Narrative

1. **Extraction** — The `Extractor` pulls raw OHLCV market data from configured providers (Yahoo Finance for stocks/crypto/commodities, Bitfinex for crypto order-book data). Data is fetched in paginated batches with cursor-based pagination.

2. **Transformation** — The `Transformer` normalizes heterogeneous provider schemas into a unified `TimeSeriesRecord` with typed value maps (`values_double`, `values_int`, `values_text`). Column names are standardized (Open, High, Low, Close, Volume).

3. **Deduplication & Loading** — Before writing, the `Loader` checks if a record for `(asset_id, data_source_id, business_date)` already exists. If it does, the record is only overwritten when the incoming `system_date` is strictly newer — ensuring idempotent re-ingestion without data loss.

4. **Storage** — Cassandra stores data in a bi-temporal model partitioned by `(asset_id, data_source_id, business_date_year)` with clustering on `(business_date DESC, system_date DESC)`. This allows efficient range scans and full version history.

5. **Analytics** — Spark reads directly from Cassandra via the spark-cassandra-connector:
   - **Aggregation job**: computes per-asset yearly record counts → `totals` table.
   - **Prediction job**: engineers features (daily return, price range, volatility ratios, lag features), trains a GBT regressor with 3-fold cross-validation and hyperparameter grid search, evaluates with RMSE/MAE/R², and writes predictions back to Cassandra.

6. **Serving** — FastAPI exposes RESTful endpoints consumed by the Next.js frontend dashboard and an MCP tool server that allows LLM assistants to query the warehouse programmatically.

---

## Project Structure

```
dw_final_project/
├── docker-compose.yml          # Service orchestration
├── backend/
│   ├── main.py                 # FastAPI app + auto-ingest lifecycle
│   ├── config/                 # Settings & constants
│   ├── database/               # Cassandra connection & schema init
│   ├── etl/                    # Extract-Transform-Load pipeline
│   │   └── providers/          # yfinance, bitfinex, nasdaq clients
│   ├── mcp_server/             # MCP tool server for LLM integration
│   ├── models/                 # Dataclass domain models
│   ├── repositories/           # Cassandra data access layer
│   ├── routers/                # FastAPI route handlers
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic layer
│   ├── spark/                  # Spark ML jobs (aggregation, prediction)
│   └── tests/                  # Pytest test suite
├── frontend/
│   └── src/
│       ├── app/                # Next.js pages (dashboard, analytics, etc.)
│       ├── components/         # Reusable UI components
│       └── lib/                # API client, hooks, types
└── scripts/
    ├── init-cassandra.cql      # Manual CQL bootstrap script
    └── seed-data.py            # Standalone data seeder
```
