package main

import (
	"log"
	"os"

	"github.com/ai-rpg/gateway/internal/handlers"
	"github.com/ai-rpg/gateway/internal/middleware"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	// 设置运行模式
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	// 创建路由
	r := gin.Default()

	// CORS中间件
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:5173", "http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// 限流中间件
	r.Use(middleware.RateLimiter())

	// 健康检查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
			"service": "api-gateway",
		})
	})

	// API路由组
	v1 := r.Group("/api/v1")
	{
		// AI相关路由
		ai := v1.Group("/ai")
		{
			ai.POST("/chat", handlers.HandleChat)
			ai.GET("/chat/stream", handlers.HandleChatStream)
			ai.POST("/generate", handlers.HandleGenerate)
		}

		// 游戏相关路由
		game := v1.Group("/game")
		{
			game.GET("/state/:characterId", handlers.GetGameState)
			game.POST("/save", handlers.SaveGame)
			game.GET("/load/:saveId", handlers.LoadGame)
			game.POST("/action", handlers.PerformAction)
		}

		// 角色相关路由
		character := v1.Group("/character")
		{
			character.GET("/:id", handlers.GetCharacter)
			character.POST("/create", handlers.CreateCharacter)
			character.PUT("/:id", handlers.UpdateCharacter)
		}
	}

	// WebSocket路由
	r.GET("/ws", handlers.HandleWebSocket)

	// 获取端口
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	// 启动服务器
	log.Printf("🚀 API Gateway running on port %s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
