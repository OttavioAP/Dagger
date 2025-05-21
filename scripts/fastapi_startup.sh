#!/bin/bash
set -e

# Start FastAPI server
cd backend/app
exec uvicorn main:app --host 0.0.0.0 --port 8080 