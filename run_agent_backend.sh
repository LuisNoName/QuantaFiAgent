#!/bin/bash

# Script to run the Agent Backend

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found (not required for agent backend)"
fi

# Run the FastAPI app
echo "Starting Agent Backend on http://localhost:8000"
echo "Health check: http://localhost:8000/healthz"
echo "Agent invoke endpoint: http://localhost:8000/agent/invoke"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run as a module from the project root
# Only watch ai_system directory for changes (ignore venv, __pycache__, etc.)
uvicorn ai_system.agent_backend.main:app --reload --reload-dir ai_system --host 0.0.0.0 --port 8000

