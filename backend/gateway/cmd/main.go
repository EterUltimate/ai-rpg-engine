package main

import (
	"log"
	"os"

	"github.com/ai-rpg/gateway/internal/handlers"
	"github.com/ai-rpg/gateway/internal/middleware"
	"github.com/ai-rpg/gateway/internal/proxy"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	// ── 运行模式 ──────────────────────────────────────────
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	// ── 下游服务地址（从环境变量读取，本地开发有默认值）──────
	gameEngineURL := getEnv("GAME_ENGINE_URL", "http://localhost:8001")
	aiEngineURL   := getEnv("AI_ENGINE_URL",   "http://localhost:8002")

	// ── 初始化反向代理 ─────────────────────────────────────
	gameProxy, err := proxy.New(gameEngineURL, "game-engine")
	if err != nil {
		log.Fatalf("Failed to init game-engine proxy: %v", err)
	}

	aiProxy, err := proxy.New(aiEngineURL, "ai-engine")
	if err != nil {
		log.Fatalf("Failed to init ai-engine proxy: %v", err)
	}

	// ── 路由 ───────────────────────────────────────────────
	r := gin.Default()

	// CORS：允许的 Origin 从环境变量读取，支持多值（逗号分隔）
	allowedOrigins := getAllowedOrigins()
	r.Use(cors.New(cors.Config{
		AllowOrigins:     allowedOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization", "Accept"},
		ExposeHeaders:    []string{"Content-Length", "Content-Type"},
		AllowCredentials: true,
	}))

	// 限流
	r.Use(middleware.RateLimiter())

	// 网关自身健康检查（不代理，直接响应）
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"service": "api-gateway",
			"upstreams": gin.H{
				"game_engine": gameEngineURL,
				"ai_engine":   aiEngineURL,
			},
		})
	})

	// WebSocket（代理到 game-engine）
	r.GET("/ws", handlers.HandleWebSocket)

	// ── API v1 路由组 ───────────────────────────────────────
	v1 := r.Group("/api/v1")
	{
		// ── AI Engine 路由 (/api/v1/ai/*) ───────────────────
		// POST /api/v1/ai/chat            → ai-engine 普通对话
		// GET  /api/v1/ai/chat/stream     → ai-engine SSE 流式对话
		// POST /api/v1/ai/generate        → ai-engine 内容生成
		ai := v1.Group("/ai")
		{
			ai.POST("/chat",         aiProxy.Handler())
			ai.GET("/chat/stream",   aiProxy.SSEHandler())  // SSE 需要单独处理
			ai.POST("/generate",     aiProxy.Handler())
		}

		// ── Game Engine 路由 (/api/v1/game/*) ───────────────
		// GET  /api/v1/game/state/:id     → game-engine 获取游戏状态
		// POST /api/v1/game/save          → game-engine 保存游戏
		// GET  /api/v1/game/load/:id      → game-engine 加载游戏
		// POST /api/v1/game/action        → game-engine 执行动作（旧接口兼容）
		game := v1.Group("/game")
		{
			game.GET("/state/:characterId", gameProxy.Handler())
			game.POST("/save",              gameProxy.Handler())
			game.GET("/load/:saveId",       gameProxy.Handler())
			game.POST("/action",            gameProxy.Handler())
		}

		// ── Character 路由 (/api/v1/character/*) ────────────
		// GET  /api/v1/character/:id
		// POST /api/v1/character/create
		// PUT  /api/v1/character/:id
		// GET  /api/v1/character/:id/inventory
		character := v1.Group("/character")
		{
			character.GET("/:id",            gameProxy.Handler())
			character.POST("/create",        gameProxy.Handler())
			character.PUT("/:id",            gameProxy.Handler())
			character.GET("/:id/inventory",  gameProxy.Handler())
		}

		// ── Actions 路由 (/api/v1/actions/*) ────────────────
		// POST /api/v1/actions/perform
		// GET  /api/v1/actions/available/:id
		// POST /api/v1/actions/move
		// POST /api/v1/actions/talk
		// POST /api/v1/actions/investigate
		// POST /api/v1/actions/rest
		// POST /api/v1/actions/quest/accept
		// POST /api/v1/actions/quest/complete
		actions := v1.Group("/actions")
		{
			actions.POST("/perform",              gameProxy.Handler())
			actions.GET("/available/:characterId", gameProxy.Handler())
			actions.POST("/move",                 gameProxy.Handler())
			actions.POST("/talk",                 gameProxy.Handler())
			actions.POST("/investigate",          gameProxy.Handler())
			actions.POST("/rest",                 gameProxy.Handler())
			actions.POST("/quest/accept",         gameProxy.Handler())
			actions.POST("/quest/complete",       gameProxy.Handler())
		}
	}

	// ── 启动 ───────────────────────────────────────────────
	port := getEnv("PORT", "8000")
	log.Printf("🚀 API Gateway running on :%s", port)
	log.Printf("   game-engine → %s", gameEngineURL)
	log.Printf("   ai-engine   → %s", aiEngineURL)

	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

// getEnv 读取环境变量，fallback 到默认值
func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// getAllowedOrigins 从 CORS_ALLOWED_ORIGINS 环境变量读取（逗号分隔）
// 本地开发默认放行 localhost:5173 和 localhost:3000
func getAllowedOrigins() []string {
	if v := os.Getenv("CORS_ALLOWED_ORIGINS"); v != "" {
		parts := splitAndTrim(v, ",")
		if len(parts) > 0 {
			return parts
		}
	}
	return []string{
		"http://localhost:5173",
		"http://localhost:3000",
	}
}

// splitAndTrim 分割字符串并去除空格
func splitAndTrim(s, sep string) []string {
	var result []string
	for _, part := range splitString(s, sep) {
		trimmed := trimSpace(part)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

func splitString(s, sep string) []string {
	var parts []string
	start := 0
	for i := 0; i <= len(s)-len(sep); i++ {
		if s[i:i+len(sep)] == sep {
			parts = append(parts, s[start:i])
			start = i + len(sep)
			i += len(sep) - 1
		}
	}
	parts = append(parts, s[start:])
	return parts
}

func trimSpace(s string) string {
	start := 0
	end := len(s)
	for start < end && (s[start] == ' ' || s[start] == '\t') {
		start++
	}
	for end > start && (s[end-1] == ' ' || s[end-1] == '\t') {
		end--
	}
	return s[start:end]
}
