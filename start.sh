#!/bin/bash
echo "======================================"
echo "Starting Mom Voice ChatBot Services..."
echo "======================================"

# 1. Start Redis Server
echo "Starting Redis server in background..."
redis-server --daemonize yes

# 2. Start RQ Worker for AI Pipeline Background processing
echo "Starting RQ Worker in background..."
source mom_voice_env/bin/activate 2>/dev/null || echo "Virtualenv not found, using global python"
nohup rq worker -u redis://localhost:6379/0 default > worker.log 2>&1 &

# 3. Start Auto Push Daemon
echo "Starting Auto Push daemon in background..."
nohup ./scripts/auto_push.sh > auto_push.log 2>&1 &

# 4. Start FastAPI Server
echo "Starting FastAPI Server on Port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
