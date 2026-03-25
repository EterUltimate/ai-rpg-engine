@echo off
set PORT=8000
set GAME_ENGINE_URL=http://localhost:8001
set AI_ENGINE_URL=http://localhost:8002
set CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
gateway.exe
