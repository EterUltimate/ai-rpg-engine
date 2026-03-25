package proxy

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// ServiceProxy 持有指向单个下游服务的反向代理
type ServiceProxy struct {
	target   *url.URL
	proxy    *httputil.ReverseProxy
	name     string
}

// New 创建一个到 targetURL 的反向代理
// name 仅用于日志标识（如 "ai-engine"）
func New(targetURL, name string) (*ServiceProxy, error) {
	u, err := url.Parse(targetURL)
	if err != nil {
		return nil, fmt.Errorf("invalid target URL %q: %w", targetURL, err)
	}

	rp := httputil.NewSingleHostReverseProxy(u)

	// 自定义 Director：修正 Host 头，避免下游服务因 Host 不匹配而报错
	originalDirector := rp.Director
	rp.Director = func(req *http.Request) {
		originalDirector(req)
		req.Host = u.Host
		req.Header.Set("X-Forwarded-By", "ai-rpg-gateway")
	}

	// 自定义错误处理：下游不可达时返回 502，而不是空响应
	rp.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		log.Printf("[proxy/%s] upstream error: %v", name, err)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadGateway)
		_, _ = w.Write([]byte(fmt.Sprintf(
			`{"error":"upstream service unavailable","service":"%s","detail":"%s"}`,
			name, err.Error(),
		)))
	}

	// 调整传输层超时
	rp.Transport = &http.Transport{
		ResponseHeaderTimeout: 120 * time.Second,
		IdleConnTimeout:       90 * time.Second,
	}

	return &ServiceProxy{target: u, proxy: rp, name: name}, nil
}

// Handler 返回一个 gin.HandlerFunc，将请求原样转发到下游服务
// stripPrefix：转发前是否去掉路径前缀（一般不需要，下游服务路径与网关路径一致）
func (sp *ServiceProxy) Handler() gin.HandlerFunc {
	return func(c *gin.Context) {
		log.Printf("[proxy/%s] %s %s", sp.name, c.Request.Method, c.Request.URL.Path)
		sp.proxy.ServeHTTP(c.Writer, c.Request)
	}
}

// SSEHandler 专门处理 SSE（Server-Sent Events）流式响应
// 标准 ReverseProxy 会缓冲响应体，SSE 必须禁用缓冲
func (sp *ServiceProxy) SSEHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		log.Printf("[proxy/%s][SSE] %s %s", sp.name, c.Request.Method, c.Request.URL.Path)

		// 构建上游请求 URL
		targetURL := *sp.target
		targetURL.Path = strings.TrimRight(targetURL.Path, "/") + c.Request.URL.Path
		targetURL.RawQuery = c.Request.URL.RawQuery

		// 创建上游请求（复制原始请求的 Header）
		upstreamReq, err := http.NewRequestWithContext(
			c.Request.Context(),
			c.Request.Method,
			targetURL.String(),
			c.Request.Body,
		)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to build upstream request"})
			return
		}
		for k, vv := range c.Request.Header {
			for _, v := range vv {
				upstreamReq.Header.Add(k, v)
			}
		}
		upstreamReq.Host = sp.target.Host

		// 直连上游，不经过缓冲层
		client := &http.Client{Timeout: 0} // SSE 不设超时
		resp, err := client.Do(upstreamReq)
		if err != nil {
			log.Printf("[proxy/%s][SSE] upstream error: %v", sp.name, err)
			c.JSON(http.StatusBadGateway, gin.H{
				"error":   "upstream service unavailable",
				"service": sp.name,
				"detail":  err.Error(),
			})
			return
		}
		defer resp.Body.Close()

		// 复制响应头
		for k, vv := range resp.Header {
			for _, v := range vv {
				c.Header(k, v)
			}
		}
		c.Status(resp.StatusCode)

		// 流式复制响应体（逐 flush）
		flusher, canFlush := c.Writer.(http.Flusher)
		buf := make([]byte, 4096)
		for {
			n, readErr := resp.Body.Read(buf)
			if n > 0 {
				_, writeErr := c.Writer.Write(buf[:n])
				if writeErr != nil {
					break
				}
				if canFlush {
					flusher.Flush()
				}
			}
			if readErr == io.EOF {
				break
			}
			if readErr != nil {
				log.Printf("[proxy/%s][SSE] read error: %v", sp.name, readErr)
				break
			}
		}
	}
}
