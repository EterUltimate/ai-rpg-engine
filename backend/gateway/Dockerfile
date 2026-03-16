FROM golang:1.22-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 编译
RUN CGO_ENABLED=0 GOOS=linux go build -o gateway cmd/main.go

# 运行阶段
FROM alpine:latest

WORKDIR /app

# 复制编译产物
COPY --from=builder /app/gateway .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["./gateway"]
