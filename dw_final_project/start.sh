#!/usr/bin/env bash
set -euo pipefail

echo "=== Casi Financial Data Warehouse ==="
echo "Starting all services..."

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

docker compose up --build -d

echo "Waiting for Cassandra to be ready..."
until docker exec casi-cassandra cqlsh -e "DESCRIBE KEYSPACES" > /dev/null 2>&1; do
  sleep 3
  echo "  ...still waiting for Cassandra"
done

echo "Initializing Cassandra schema..."
docker exec -i casi-cassandra cqlsh < scripts/init-cassandra.cql

echo ""
echo "=== All services are up ==="
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Spark UI:  http://localhost:8080"
echo ""
echo "To stop: docker compose down"
