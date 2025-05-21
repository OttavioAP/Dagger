#!/bin/bash
set -e

# Start Postgres in the background
/app/scripts/start_postgres.sh &
POSTGRES_PID=$!

# Start FastAPI in the foreground
/app/scripts/fastapi_startup.sh &
FASTAPI_PID=$!

# Wait for both processes
wait $POSTGRES_PID
wait $FASTAPI_PID 