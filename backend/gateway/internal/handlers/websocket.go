package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // 允许所有来源(生产环境需要限制)
	},
}

// HandleWebSocket 处理WebSocket连接
func HandleWebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	defer conn.Close()

	log.Println("WebSocket client connected")

	for {
		// 读取消息
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			log.Printf("WebSocket read error: %v", err)
			break
		}

		log.Printf("Received: %s", message)

		// 回显消息(实际应该路由到相应的服务)
		response := []byte("Echo: " + string(message))
		err = conn.WriteMessage(messageType, response)
		if err != nil {
			log.Printf("WebSocket write error: %v", err)
			break
		}
	}

	log.Println("WebSocket client disconnected")
}
