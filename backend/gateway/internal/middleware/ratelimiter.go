package middleware

import (
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

type visitor struct {
	lastSeen time.Time
	tokens   int
}

var (
	visitors = make(map[string]*visitor)
	mu       sync.Mutex
)

// RateLimiter 限流中间件
func RateLimiter() gin.HandlerFunc {
	return func(c *gin.Context) {
		ip := c.ClientIP()

		mu.Lock()
		v, exists := visitors[ip]
		if !exists {
			visitors[ip] = &visitor{
				lastSeen: time.Now(),
				tokens:   100, // 每分钟100个请求
			}
			v = visitors[ip]
		}
		mu.Unlock()

		// 补充令牌
		now := time.Now()
		elapsed := now.Sub(v.lastSeen)
		v.tokens += int(elapsed.Seconds()) // 每秒补充1个令牌
		if v.tokens > 100 {
			v.tokens = 100
		}
		v.lastSeen = now

		// 检查令牌
		if v.tokens <= 0 {
			c.JSON(429, gin.H{
				"error": "Too many requests",
			})
			c.Abort()
			return
		}

		v.tokens--

		c.Next()
	}
}
