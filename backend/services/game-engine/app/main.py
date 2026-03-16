from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import game, character, actions
from app.database import init_db, get_db
from app.game_logic.game_manager import game_manager
import os

app = FastAPI(
    title="AI-RPG Game Engine",
    description="游戏引擎服务 - 管理游戏状态、角色、任务、世界等",
    version="0.2.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(game.router, prefix="/api/v1", tags=["game"])
app.include_router(character.router, prefix="/api/v1", tags=["character"])
app.include_router(actions.router, prefix="/api/v1", tags=["actions"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    # 初始化数据库
    await init_db()
    
    # 初始化游戏管理器
    async for db in get_db():
        await game_manager.initialize(db)
        break
    
    print("✅ Game Engine Service Started")
    print("🎮 World Manager Initialized")
    print("📦 Database Connected")


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "service": "game-engine",
        "version": "0.2.0",
        "components": {
            "database": "connected",
            "world_manager": "initialized",
            "action_handler": "ready"
        }
    }


@app.get("/")
async def root():
    """根路由"""
    return {
        "service": "AI-RPG Game Engine",
        "version": "0.2.0",
        "endpoints": {
            "game": "/api/v1/game",
            "character": "/api/v1/character",
            "actions": "/api/v1/actions"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
