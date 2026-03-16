# Data Core - RAG 数据库核心目录

⚠️ **重要提示**: 本目录下的所有文件受 [DATA_LICENSE.md](../DATA_LICENSE.md) 约束。

## 目录结构

```
data-core/
├── vectors/           # 向量索引文件
│   └── chroma.sqlite3 # ChromaDB 向量数据库
├── knowledge_base/    # 知识库文件
│   └── metadata.json  # 元数据信息
└── README.md          # 本文件
```

## 许可说明

本目录下的所有数据文件采用 **非商业学习许可协议**：

- ✅ 允许个人学习和研究
- ✅ 允许非商业性实验
- ❌ 禁止商业用途
- ❌ 禁止二次分发

详见 [DATA_LICENSE.md](../DATA_LICENSE.md)

## 构建自己的数据

如需商业使用或分发，请使用 `scripts/build_own_data.py` 构建自己的数据：

```bash
# 准备你的数据文件 (JSONL/JSON/TXT 格式)
mkdir -p my_data
echo '{"id": "1", "text": "故事内容..."}' > my_data/story.jsonl

# 构建向量数据库
python scripts/build_own_data.py --input my_data/ --output my-data-core/

# 验证数据
python scripts/build_own_data.py --validate my-data-core/
```

使用自己构建的数据不受 DATA_LICENSE.md 限制。
