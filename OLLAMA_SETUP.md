# 🦙 Ollama 本地 AI 設定指南

## 為什麼選擇 Ollama？

✅ **完全免費** - 不需要 API Key，不需要網路
✅ **隱私保護** - 所有對話都在本地處理
✅ **速度快** - M3 Max 可以跑得很快
✅ **多模型** - 可以輕鬆切換不同的 AI 模型

---

## 📦 安裝 Ollama

### Mac 安裝（推薦）

```bash
# 方法 1: 使用 Homebrew
brew install ollama

# 方法 2: 下載安裝包
# 前往 https://ollama.com/download 下載 Mac 版本
```

### 啟動 Ollama

```bash
# 啟動 Ollama 服務
ollama serve
```

保持這個終端視窗開啟！Ollama 會在背景運行。

---

## 🤖 下載 AI 模型

### 推薦模型（按效能排序）

#### 1. Llama 3.2 3B（推薦入門）
```bash
ollama pull llama3.2:3b
```
- **大小**: ~2GB
- **速度**: ⚡⚡⚡ 很快
- **能力**: 🎯🎯 適合日常對話
- **繁中支援**: ✅ 良好

#### 2. Llama 3.1 8B（推薦平衡）
```bash
ollama pull llama3.1:8b
```
- **大小**: ~4.7GB
- **速度**: ⚡⚡ 快
- **能力**: 🎯🎯🎯 很聰明
- **繁中支援**: ✅ 優秀

#### 3. Qwen 2.5 7B（繁中專用）
```bash
ollama pull qwen2.5:7b
```
- **大小**: ~4.4GB
- **速度**: ⚡⚡ 快
- **能力**: 🎯🎯🎯 很聰明
- **繁中支援**: ✅✅ 最佳（阿里巴巴出品）

#### 4. Gemma 2 9B（Google 出品）
```bash
ollama pull gemma2:9b
```
- **大小**: ~5.4GB
- **速度**: ⚡⚡ 快
- **能力**: 🎯🎯🎯 很聰明
- **繁中支援**: ✅ 優秀

### 查看已安裝的模型

```bash
ollama list
```

---

## ⚙️ 設定專案使用 Ollama

### 步驟 1: 編輯 .env

```bash
nano .env
```

修改以下內容：

```bash
# 使用 Ollama 作為 AI 後端
AI_BACKEND=ollama

# Ollama 設定
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b  # 或改成你下載的模型
```

### 步驟 2: 安裝 Python 套件

```bash
source venv/bin/activate
pip install ollama
```

### 步驟 3: 測試

```bash
# 測試 Ollama 是否正常運作
python scripts/test_voice.py

# 或直接開始對話
python scripts/interactive_chat.py
```

---

## 💬 互動式對話

### 啟動一問一答模式

```bash
python scripts/interactive_chat.py
```

### 功能說明

1. **選擇模式**
   - 純文字對話（推薦）
   - 文字 + 語音輸出

2. **指令**
   - 輸入問題 → AI 回答
   - `quit` / `exit` / `退出` → 結束對話
   - `reset` / `重置` → 清除對話歷史
   - `voice on` → 開啟語音朗讀
   - `voice off` → 關閉語音朗讀

### 使用範例

```
👦 你: 為什麼天空是藍色的？
🤖 小助手: 因為太陽光中的藍色光線比較容易被空氣中的小分子散射...

👦 你: 恐龍為什麼會滅絕？
🤖 小助手: 科學家認為是因為一顆巨大的隕石撞擊地球...

👦 你: reset
🔄 對話已重置，我們重新開始吧！

👦 你: quit
🤖 小助手: 再見！期待下次再聊！
```

---

## 🔄 切換不同模型

### 在 .env 中修改

```bash
# 使用 Llama 3.2 3B（快速）
OLLAMA_MODEL=llama3.2:3b

# 使用 Llama 3.1 8B（平衡）
OLLAMA_MODEL=llama3.1:8b

# 使用 Qwen 2.5 7B（繁中最佳）
OLLAMA_MODEL=qwen2.5:7b
```

### 或在程式中測試

```python
from src.voice import ChatBot
import os

# 暫時修改模型
os.environ['OLLAMA_MODEL'] = 'qwen2.5:7b'

bot = ChatBot()
response = bot.chat("你好！")
print(response)
```

---

## 🆚 Ollama vs Gemini 比較

| 項目 | Ollama (本地) | Gemini (雲端) |
|------|---------------|---------------|
| **成本** | 完全免費 | 有免費額度 |
| **隱私** | ✅ 完全本地 | ⚠️ 需上傳雲端 |
| **速度** | ⚡⚡⚡ M3 Max 很快 | ⚡⚡ 受網路影響 |
| **離線使用** | ✅ 可以 | ❌ 不行 |
| **需要網路** | ❌ 不需要 | ✅ 需要 |
| **模型選擇** | 多種開源模型 | Google 模型 |
| **繁中能力** | ✅ 看模型 | ✅ 優秀 |

---

## 🐛 常見問題

### Q: Ollama 服務啟動失敗？

**檢查是否已安裝：**
```bash
ollama --version
```

**重新安裝：**
```bash
brew uninstall ollama
brew install ollama
```

### Q: 連線錯誤 "Connection refused"？

**確認 Ollama 正在運行：**
```bash
# 開啟新終端
ollama serve
```

### Q: 模型下載很慢？

**使用國內鏡像（中國）：**
```bash
export OLLAMA_HOST=https://ollama.example.com
ollama pull llama3.2:3b
```

### Q: 記憶體不足？

**使用較小的模型：**
```bash
# 改用 1B 模型（最小）
ollama pull qwen2.5:1.5b
```

然後在 `.env` 設定：
```
OLLAMA_MODEL=qwen2.5:1.5b
```

### Q: M3 Max 跑得不夠快？

**確認使用 Metal 加速：**
Ollama 會自動使用 Mac 的 GPU 加速，不需要額外設定。

### Q: 想切換回 Gemini？

編輯 `.env`:
```bash
AI_BACKEND=gemini
GEMINI_API_KEY=你的金鑰
```

---

## 📚 更多資源

- [Ollama 官網](https://ollama.com)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [可用模型列表](https://ollama.com/library)
- [Llama 3 介紹](https://ai.meta.com/blog/meta-llama-3/)

---

## 🎉 開始使用

```bash
# 1. 啟動 Ollama
ollama serve  # 保持運行

# 2. 開啟新終端，下載模型
ollama pull llama3.2:3b

# 3. 進入專案目錄
cd kid_robot_project
source venv/bin/activate

# 4. 確認 .env 設定
cat .env | grep AI_BACKEND
# 應該顯示: AI_BACKEND=ollama

# 5. 開始對話！
python scripts/interactive_chat.py
```

享受本地 AI 的樂趣！🚀
