#!/bin/bash

# Script to run the Slack Backend

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your credentials"
    exit 1
fi

# Run the FastAPI app
echo "Starting Slack Backend on http://localhost:3000"
echo "Health check: http://localhost:3000/healthz"
echo "Slack events endpoint: http://localhost:3000/slack/events"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run as a module from the project root
# Only watch ai_system directory for changes (ignore venv, __pycache__, etc.)
uvicorn ai_system.slack_backend.app:app --reload --reload-dir ai_system --host 0.0.0.0 --port 3000

