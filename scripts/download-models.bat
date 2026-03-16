@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM AI模型下载脚本

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 模型下载工具           ║
echo ╚════════════════════════════════════════╝
echo.
echo [开始时间: %date% %time%]
echo.

REM 检查Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo     [✗] Python 未安装
    echo.
    echo     请先安装Python: https://www.python.org/
    pause
    exit /b 1
)

echo ┌─────────────────────────────────────────┐
echo │ 本次将下载以下模型:                     │
echo └─────────────────────────────────────────┘
echo.
echo   1. 嵌入模型 (Embedding)
echo      名称: all-MiniLM-L6-v2
echo      大小: ~90MB
echo      用途: 文本向量化,用于RAG检索
echo.
echo   2. 重排序模型 (Reranker)
echo      名称: cross-encoder/ms-marco-MiniLM-L-6-v2
echo      大小: ~80MB
echo      用途: 检索结果重排序,提高准确率
echo.
echo   3. LLM模型 (大语言模型)
echo      状态: 需要手动下载
echo      原因: 文件较大(2-16GB),请参考 models\README.md
echo.

set TOTAL_STEPS=3
set CURRENT_STEP=0

REM ============================================
REM 步骤1: 创建模型目录
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !CURRENT_STEP!/!TOTAL_STEPS!] 创建模型目录         │
echo └─────────────────────────────────────────┘
echo.

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 创建必要的目录...
echo.

if not exist "models\embeddings" (
    mkdir models\embeddings
    echo     [✓] 创建 models\embeddings
) else (
    echo     [✓] models\embeddings 已存在
)

if not exist "models\rerankers" (
    mkdir models\rerankers
    echo     [✓] 创建 models\rerankers
) else (
    echo     [✓] models\rerankers 已存在
)

if not exist "models\llm" (
    mkdir models\llm
    echo     [✓] 创建 models\llm
) else (
    echo     [✓] models\llm 已存在
)

echo.
echo     ✓ 目录创建完成
echo.

REM ============================================
REM 步骤2: 下载嵌入模型
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !CURRENT_STEP!/!TOTAL_STEPS!] 下载嵌入模型         │
echo └─────────────────────────────────────────┘
echo.

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 开始下载 all-MiniLM-L6-v2...
echo     模型大小: ~90MB
echo     目标路径: models\embeddings\all-MiniLM-L6-v2
echo.
echo     正在下载,请耐心等待...
echo     (首次下载需要从HuggingFace获取模型)
echo.

python -c "import sys; sys.stdout.write('下载进度: '); from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('models/embeddings/all-MiniLM-L6-v2'); print('完成')"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo     [✗] 嵌入模型下载失败
    echo.
    echo     可能的原因:
    echo       1. 网络连接问题
    echo       2. 未安装 sentence-transformers
    echo.
    echo     解决方法:
    echo       pip install sentence-transformers
    echo       或使用国内镜像:
    echo       pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers
    echo.
    pause
    exit /b 1
)

echo.
echo     [✓] 嵌入模型下载完成
echo     保存位置: models\embeddings\all-MiniLM-L6-v2
echo.

REM ============================================
REM 步骤3: 下载重排序模型
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !CURRENT_STEP!/!TOTAL_STEPS!] 下载重排序模型       │
echo └─────────────────────────────────────────┘
echo.

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 开始下载 ms-marco-MiniLM-L-6-v2...
echo     模型大小: ~80MB
echo     目标路径: models\rerankers\ms-marco-MiniLM-L-6-v2
echo.
echo     正在下载,请耐心等待...
echo.

python -c "import sys; sys.stdout.write('下载进度: '); from sentence_transformers import CrossEncoder; model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); model.save('models/rerankers/ms-marco-MiniLM-L-6-v2'); print('完成')"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo     [✗] 重排序模型下载失败
    echo.
    echo     解决方法同上
    echo.
    pause
    exit /b 1
)

echo.
echo     [✓] 重排序模型下载完成
echo     保存位置: models\rerankers\ms-marco-MiniLM-L-6-v2
echo.

REM ============================================
REM 完成
REM ============================================
echo ╔════════════════════════════════════════╗
echo ║        模型下载完成!                   ║
echo ╚════════════════════════════════════════╝
echo.
echo [完成时间: %date% %time%]
echo.

echo ┌─────────────────────────────────────────┐
echo │ 已下载模型:                             │
echo └─────────────────────────────────────────┘
echo.
echo   [✓] 嵌入模型: all-MiniLM-L6-v2
echo       用于: 文本向量化,RAG检索
echo       大小: ~90MB
echo.
echo   [✓] 重排序模型: ms-marco-MiniLM-L-6-v2
echo       用于: 检索结果重排序
echo       大小: ~80MB
echo.

echo ┌─────────────────────────────────────────┐
echo │ 待手动下载: LLM模型                     │
echo └─────────────────────────────────────────┘
echo.
echo   推荐模型:
echo.
echo   1. Qwen2.5-7B-Instruct (推荐)
echo      大小: ~14GB
echo      质量: ⭐⭐⭐⭐⭐
echo      适合: 16GB+ 内存
echo.
echo   2. Mistral-7B-Instruct-v0.3
echo      大小: ~14GB
echo      质量: ⭐⭐⭐⭐⭐
echo      适合: 16GB+ 内存
echo.
echo   3. Qwen2.5-3B-Instruct
echo      大小: ~6GB
echo      质量: ⭐⭐⭐⭐
echo      适合: 8GB+ 内存
echo.
echo   4. Phi-3-mini-4k-instruct
echo      大小: ~2.3GB
echo      质量: ⭐⭐⭐⭐
echo      适合: 4GB+ 内存
echo.

echo ┌─────────────────────────────────────────┐
echo │ 下载方法:                               │
echo └─────────────────────────────────────────┘
echo.
echo   方法1: 使用HuggingFace CLI
echo      pip install huggingface-hub
echo      huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir models\llm\Qwen2.5-7B-Instruct
echo.
echo   方法2: 使用Python
echo      python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-7B-Instruct', local_dir='models/llm/Qwen2.5-7B-Instruct')"
echo.
echo   详细说明请查看: models\README.md
echo.

pause
