#!/usr/bin/env python3
"""
RAG 数据库构建脚本
用于构建自定义的 RAG 数据库，规避 DATA_LICENSE.md 的许可限制

使用方法:
    python scripts/build_own_data.py --input your_data/ --output data-core/
    python scripts/build_own_data.py --validate data-core/
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("警告: 缺少依赖库，请安装: pip install sentence-transformers chromadb")


def load_data(input_path: str) -> List[Dict[str, Any]]:
    """
    从输入目录加载数据文件
    
    支持格式:
    - .jsonl: JSON Lines 格式
    - .json: JSON 数组格式
    - .txt: 纯文本格式（每行一条记录）
    """
    data = []
    input_dir = Path(input_path)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_path}")
    
    for file_path in input_dir.rglob("*"):
        if file_path.suffix == ".jsonl":
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        
        elif file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
                else:
                    data.append(file_data)
        
        elif file_path.suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if line.strip():
                        data.append({
                            "id": f"{file_path.stem}_{i}",
                            "text": line.strip(),
                            "source": str(file_path)
                        })
    
    print(f"已加载 {len(data)} 条数据记录")
    return data


def build_embeddings(
    data: List[Dict[str, Any]],
    text_field: str = "text",
    model_name: str = "all-MiniLM-L6-v2"
) -> tuple:
    """
    使用 sentence-transformers 构建嵌入向量
    """
    if not HAS_DEPS:
        raise ImportError("请先安装依赖: pip install sentence-transformers chromadb")
    
    print(f"加载嵌入模型: {model_name}...")
    model = SentenceTransformer(model_name)
    
    texts = [item.get(text_field, "") for item in data]
    print(f"生成 {len(texts)} 条文本的嵌入向量...")
    
    embeddings = model.encode(texts, show_progress_bar=True)
    
    return embeddings, model


def build_vector_store(
    data: List[Dict[str, Any]],
    embeddings: List,
    output_path: str,
    collection_name: str = "rag_knowledge_base"
):
    """
    构建 ChromaDB 向量存储
    """
    if not HAS_DEPS:
        raise ImportError("请先安装依赖: pip install chromadb")
    
    output_dir = Path(output_path)
    vectors_dir = output_dir / "vectors"
    vectors_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"创建向量存储: {vectors_dir}...")
    
    # 初始化 ChromaDB
    client = chromadb.PersistentClient(path=str(vectors_dir))
    
    # 删除已存在的集合
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    # 创建新集合
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "RAG Knowledge Base"}
    )
    
    # 添加数据
    ids = [item.get("id", f"doc_{i}") for i, item in enumerate(data)]
    texts = [item.get("text", "") for item in data]
    metadatas = [{k: str(v) for k, v in item.items() if k != "text"} for item in data]
    
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )
    
    print(f"向量存储创建完成，共 {len(ids)} 条记录")
    
    # 保存元数据
    metadata = {
        "total_documents": len(data),
        "collection_name": collection_name,
        "created_by": "build_own_data.py"
    }
    
    with open(output_dir / "knowledge_base" / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return collection


def validate_data(data_path: str) -> Dict[str, Any]:
    """
    验证数据目录的结构和内容
    """
    data_dir = Path(data_path)
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    # 检查目录结构
    if not (data_dir / "vectors").exists():
        results["errors"].append("缺少 vectors 目录")
        results["valid"] = False
    
    if not (data_dir / "knowledge_base").exists():
        results["warnings"].append("缺少 knowledge_base 目录")
    
    # 检查元数据
    metadata_path = data_dir / "knowledge_base" / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            results["stats"] = metadata
    else:
        results["warnings"].append("缺少 metadata.json")
    
    # 检查向量文件
    vectors_dir = data_dir / "vectors"
    if vectors_dir.exists():
        chroma_files = list(vectors_dir.glob("chroma.sqlite3"))
        if chroma_files:
            results["stats"]["has_vector_db"] = True
        else:
            results["warnings"].append("未找到 ChromaDB 数据库文件")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="构建自定义 RAG 数据库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从数据目录构建 RAG 数据库
  python scripts/build_own_data.py --input your_data/ --output data-core/
  
  # 使用不同的嵌入模型
  python scripts/build_own_data.py --input your_data/ --output data-core/ --model paraphrase-multilingual-MiniLM-L12-v2
  
  # 验证数据目录
  python scripts/build_own_data.py --validate data-core/

数据格式要求:
  - JSONL: 每行一个 JSON 对象，必须包含 "text" 字段
  - JSON: JSON 数组，每个对象必须包含 "text" 字段
  - TXT: 每行一条文本记录

注意: 使用此脚本构建的数据完全属于您自己，不受 DATA_LICENSE.md 的限制。
        """
    )
    
    parser.add_argument("--input", "-i", help="输入数据目录")
    parser.add_argument("--output", "-o", default="data-core/", help="输出目录 (默认: data-core/)")
    parser.add_argument("--model", "-m", default="all-MiniLM-L6-v2", help="嵌入模型名称 (默认: all-MiniLM-L6-v2)")
    parser.add_argument("--text-field", "-t", default="text", help="文本字段名称 (默认: text)")
    parser.add_argument("--collection", "-c", default="rag_knowledge_base", help="向量集合名称")
    parser.add_argument("--validate", "-v", action="store_true", help="验证数据目录")
    
    args = parser.parse_args()
    
    if args.validate:
        print(f"验证数据目录: {args.output}")
        results = validate_data(args.output)
        
        print("\n验证结果:")
        print(f"  状态: {'✓ 有效' if results['valid'] else '✗ 无效'}")
        
        if results["errors"]:
            print("\n错误:")
            for error in results["errors"]:
                print(f"  - {error}")
        
        if results["warnings"]:
            print("\n警告:")
            for warning in results["warnings"]:
                print(f"  - {warning}")
        
        if results["stats"]:
            print("\n统计信息:")
            for key, value in results["stats"].items():
                print(f"  {key}: {value}")
        
        return 0 if results["valid"] else 1
    
    if not args.input:
        parser.error("请指定输入目录: --input <path>")
    
    print("=" * 60)
    print("RAG 数据库构建工具")
    print("=" * 60)
    print(f"\n输入目录: {args.input}")
    print(f"输出目录: {args.output}")
    print(f"嵌入模型: {args.model}")
    print()
    
    # 加载数据
    print("步骤 1/3: 加载数据...")
    data = load_data(args.input)
    
    if not data:
        print("错误: 未找到任何数据")
        return 1
    
    # 构建嵌入
    print("\n步骤 2/3: 构建嵌入向量...")
    embeddings, model = build_embeddings(data, args.text_field, args.model)
    
    # 构建向量存储
    print("\n步骤 3/3: 构建向量存储...")
    build_vector_store(data, embeddings, args.output, args.collection)
    
    print("\n" + "=" * 60)
    print("✓ 构建完成!")
    print("=" * 60)
    print(f"\n数据已保存到: {args.output}")
    print("\n重要提示:")
    print("  使用此脚本构建的数据完全属于您自己，")
    print("  不受 DATA_LICENSE.md 的非商业许可限制。")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
