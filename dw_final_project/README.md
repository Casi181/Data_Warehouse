# CASI — Financial Data Warehouse

A full-stack data warehouse system for ingesting, storing, analyzing, and predicting financial time-series data. Built with **FastAPI**, **Apache Cassandra**, **Apache Spark ML**, and **Next.js**.

---

## Architecture

**Services:**

- Frontend (Next.js) → :3000
- Backend (FastAPI) → :8000
- Cassandra (Storage) → :9042

**Connections:**

- Browser → Frontend → Backend (REST API)
- Backend → Cassandra (CQL driver)
- Spark (local mode) → Cassandra (spark-cassandra-connector)

**ETL Pipeline:**

Extractor (yfinance, bitfinex, nasdaq) → Transformer (normalize schemas) → Loader (deduplicate + upsert) → Cassandra

**Analytics Pipeline:**

Cassandra → Spark Aggregation → totals table
Cassandra → Spark GBT Prediction (3-fold CV) → regression_results table

**Serving:**

Cassandra → FastAPI → Next.js dashboard (auto-refreshes every 5s)
Cassandra → FastAPI → MCP tool server → LLM assistants
Cassandra → FastAPI → /chat endpoint → AI Assistant UI

### Key Design Decisions

- **Storage — Apache Cassandra**: Wide-column store ideal for time-series; bi-temporal model (business_date + system_date) enables full audit trail.
- **API — FastAPI**: Async-first, auto-generated OpenAPI docs, dependency injection.
- **ML — Spark MLlib (GBT)**: Local-mode training with 3-fold cross-validation; captures non-linear price dynamics.
- **Frontend — Next.js + MUI**: Hot-reload dev server, side navigation, auto-updating dashboard.
- **AI Assistant — /chat endpoint**: Routes natural language queries to MCP tool handlers for real-time warehouse lookups.
- **Deduplication**: Records are only written when incoming `system_date` is newer than existing — ensures idempotent re-ingestion.

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (only for Cassandra)

### Quick Start

```bash
# 1. Start Cassandra
docker run -d --name cassandra -p 9042:9042 -e CASSANDRA_CLUSTER_NAME=AcmeDW -e CASSANDRA_DC=datacenter1 cassandra:5.0

# 2. Wait for Cassandra to be ready (~30s)
docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES"

# 3. Start Backend (auto-ingests ~41 tickers on first run)
cd dw_final_project/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir .

# 4. Start Frontend (in a separate terminal)
cd dw_final_project/frontend
npm install
npm run dev
```

Or use the convenience script:

```bash
start.bat
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

On first boot the backend automatically ingests ~41 tickers (stocks, crypto, commodities, ETFs) from Yahoo Finance and Bitfinex.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CASSANDRA_HOSTS` | `localhost` | Comma-separated Cassandra contact points |
| `CASSANDRA_PORT` | `9042` | CQL native transport port |
| `CASSANDRA_KEYSPACE` | `acme_dw` | Target keyspace |

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

### Chat with AI Assistant
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the price of AAPL?"}'
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

5. **Analytics** — Spark runs in local mode within the backend process:
   - **Aggregation job**: computes per-asset yearly record counts → `totals` table.
   - **Prediction job**: engineers features (daily return, price range, volatility ratios, lag features), trains a GBT regressor with 3-fold cross-validation, evaluates with RMSE/MAE/R², and writes predictions back to Cassandra.

6. **Serving** — FastAPI exposes RESTful endpoints consumed by the Next.js frontend dashboard (auto-refreshes every 5s) and a chat endpoint that routes natural language queries to MCP tool handlers.

---

## Project Structure

- **backend/main.py** — FastAPI app + auto-ingest lifecycle
- **backend/config/** — Settings & constants
- **backend/database/** — Cassandra connection & schema init
- **backend/etl/** — Extract-Transform-Load pipeline
- **backend/etl/providers/** — yfinance, bitfinex, nasdaq clients
- **backend/mcp_server/** — MCP tool server for LLM integration
- **backend/models/** — Dataclass domain models
- **backend/repositories/** — Cassandra data access layer (with deduplication)
- **backend/routers/** — FastAPI route handlers (assets, data, analytics, chat, ingestion)
- **backend/schemas/** — Pydantic request/response schemas
- **backend/services/** — Business logic layer
- **backend/spark/** — Spark ML jobs (aggregation, prediction with CV)
- **backend/tests/** — Pytest test suite
- **frontend/src/app/** — Next.js pages (dashboard, analytics, assistant, etc.)
- **frontend/src/components/** — Reusable UI components
- **frontend/src/lib/** — API client, hooks, types
- **start.bat** — One-click local startup script
- **scripts/init-cassandra.cql** — Manual CQL bootstrap script
- **scripts/seed-data.py** — Standalone data seeder
