package handlers

import (
	"log"
	"net/http"
	"net/url"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// 允许所有来源（生产环境应收紧）
		return true
	},
	ReadBufferSize:  4096,
	WriteBufferSize: 4096,
}

// HandleWebSocket 将客户端 WebSocket 连接代理到 game-engine
func HandleWebSocket(c *gin.Context) {
	gameEngineURL := os.Getenv("GAME_ENGINE_URL")
	if gameEngineURL == "" {
		gameEngineURL = "http://localhost:8001"
	}

	// 将 http(s) 转换为 ws(s)
	wsTarget, err := buildWSURL(gameEngineURL, "/ws", c.Request.URL.RawQuery)
	if err != nil {
		log.Printf("[ws-proxy] invalid game-engine URL: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "gateway configuration error"})
		return
	}

	log.Printf("[ws-proxy] client %s → upstream %s", c.ClientIP(), wsTarget)

	// ── 升级客户端连接 ──────────────────────────────────────
	clientConn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("[ws-proxy] upgrade client error: %v", err)
		return
	}
	defer clientConn.Close()

	// ── 连接上游 WebSocket ──────────────────────────────────
	upstreamConn, _, err := websocket.DefaultDialer.Dial(wsTarget, nil)
	if err != nil {
		log.Printf("[ws-proxy] dial upstream error: %v", err)
		// 通知客户端上游不可达
		_ = clientConn.WriteMessage(websocket.TextMessage, []byte(
			`{"type":"error","message":"game-engine unavailable"}`,
		))
		return
	}
	defer upstreamConn.Close()

	// ── 双向转发 ────────────────────────────────────────────
	errc := make(chan error, 2)

	// 客户端 → 上游
	go func() {
		for {
			msgType, msg, err := clientConn.ReadMessage()
			if err != nil {
				errc <- err
				return
			}
			if err := upstreamConn.WriteMessage(msgType, msg); err != nil {
				errc <- err
				return
			}
		}
	}()

	// 上游 → 客户端
	go func() {
		for {
			msgType, msg, err := upstreamConn.ReadMessage()
			if err != nil {
				errc <- err
				return
			}
			if err := clientConn.WriteMessage(msgType, msg); err != nil {
				errc <- err
				return
			}
		}
	}()

	// 任意一方断开则结束
	if err := <-errc; err != nil {
		log.Printf("[ws-proxy] connection closed: %v", err)
	}
}

// buildWSURL 将 http://host/path 转换为 ws://host/targetPath?query
func buildWSURL(baseHTTP, targetPath, rawQuery string) (string, error) {
	u, err := url.Parse(baseHTTP)
	if err != nil {
		return "", err
	}

	switch u.Scheme {
	case "https":
		u.Scheme = "wss"
	default:
		u.Scheme = "ws"
	}

	u.Path = targetPath
	u.RawQuery = rawQuery
	return u.String(), nil
}
