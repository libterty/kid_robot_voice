#!/bin/bash

# 🤖 家庭陪讀機器人 - 快速設定腳本

echo "🤖 家庭陪讀機器人 - 環境設定"
echo "================================"

# 檢查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 找不到 Python 3"
    echo "請先安裝 Python 3.11 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "✅ 找到 Python $PYTHON_VERSION"

# 建立虛擬環境
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 正在建立虛擬環境..."
    python3 -m venv venv
    echo "✅ 虛擬環境已建立"
else
    echo "✅ 虛擬環境已存在"
fi

# 啟動虛擬環境
echo ""
echo "🔄 啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo ""
echo "📦 正在安裝依賴套件..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ 依賴安裝完成！"

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  警告: 找不到 .env 檔案"
    echo "正在從 .env.example 建立..."
    cp .env.example .env
    echo "✅ .env 已建立"
    echo ""
    echo "🔑 請編輯 .env 檔案並填入你的 OPENAI_API_KEY"
    echo "   nano .env  (或用任何文字編輯器)"
else
    echo ""
    echo "✅ .env 檔案已存在"
fi

# 建立必要目錄
mkdir -p data/{logs,audio,config}
echo "✅ 資料目錄已建立"

echo ""
echo "================================"
echo "✨ 設定完成！"
echo "================================"
echo ""
echo "🚀 快速開始:"
echo "  1. 啟動虛擬環境:  source venv/bin/activate"
echo "  2. 測試語音功能:  python scripts/test_voice.py"
echo "  3. 測試視覺功能:  python scripts/test_vision.py"
echo "  4. 完整示範:      python scripts/demo_chat.py"
echo ""
echo "📚 更多資訊請參考 README.md"
echo ""
