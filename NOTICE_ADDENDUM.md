# ⚠️ 重要许可声明与数据使用限制

## 1. 许可范围区分 (License Scope Separation)

本项目采用 **混合许可模式**：

| 组件类型 | 包含目录 | 许可协议 | 允许商用 | 允许二次分发 |
| :--- | :--- | :--- | :---: | :---: |
| **源代码** | `frontend/`, `backend/`, `gateway/`, `docs/`, `scripts/` | **MIT License** | ✅ 是 | ✅ 是 |
| **RAG 核心数据** | `data-core/`, `database/`, `models/`, `*.bin`, `*.sqlite`, `vectors/` | **NC-ND 学习许可** | 🛑 **否** | 🛑 **否** |

---

## 2. RAG 数据库特别条款

本项目中包含的 **RAG 数据库核心内容**（预置向量、嵌入模型权重、剧情知识库等）仅供**学习和研究使用**。

- ❌ **严禁**将预置的 RAG 数据文件用于任何商业产品或服务
- ❌ **严禁**将预置的 RAG 数据文件二次分发（包括修改后的版本）
- 💡 **建议**：如需商用，请使用本引擎代码架构，并自行采集、清洗和构建符合您业务需求的数据集

---

## 3. 合规使用指南

### 对于开发者
您可以自由 Fork、修改和部署代码部分。在部署时，请确保：
- 移除或替换受限制的 `database/`、`models/` 和 `data-core/` 目录下的预置文件
- 使用 `scripts/build_own_data.py` 构建自己的数据

### 对于研究者
您可以在本地完整运行项目进行学术分析，但：
- 不得公开分享包含预置数据的完整构建包
- 在发表论文时，请引用本项目并说明数据来源

### 对于商业用户
如需商业使用，请：
1. 使用本项目代码（MIT License）
2. 自行构建 RAG 数据库，或
3. 联系作者获取数据商业授权

---

## 4. 技术隔离措施

### 4.1 .gitignore 策略
以下数据文件已从 Git 仓库中排除，仅提供下载链接：

```gitignore
# 数据文件
database/*.sqlite
database/*.db
models/*.bin
models/*.gguf
data-core/vectors/*.hnsw
data-core/vectors/*.index
*.bin
*.sqlite
*.sqlite3
```

### 4.2 启动时检查
后端服务在启动时会检测环境变量：
- 如果 `ENV=PROD` 且检测到预置数据，将输出警告日志
- 建议在生产环境中使用自建数据

---

## 5. 构建自己的数据

我们提供了脚本帮助您构建自己的 RAG 数据库：

```bash
# 构建自定义数据
python scripts/build_own_data.py \
    --input your_story_data/ \
    --output data-core/ \
    --format jsonl

# 验证数据
python scripts/build_own_data.py --validate data-core/
```

---

> **法律声明**：任何忽略此声明并滥用 RAG 数据内容的行为，均视为对作者知识产权的侵犯，作者保留追究法律责任的权利。
