# 🚀 5 分鐘快速開始指南（Gemini 版）

## 第一步：設定環境 (2 分鐘)

```bash
# 1. 進入專案目錄
cd kid_robot_project

# 2. 執行自動設定腳本
./setup.sh
```

這會自動完成：
- ✅ 建立 Python 虛擬環境
- ✅ 安裝所有依賴套件
- ✅ 建立資料目錄
- ✅ 複製環境變數範本

---

## 第二步：設定 Gemini API Key (1 分鐘)

### 取得 Google Gemini API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登入你的 Google 帳號
3. 點選「Get API Key」→「Create API key」
4. 複製你的 API Key

**完全免費！不需要綁信用卡！** 🎉

### 填入 .env 檔案

```bash
# 用任何編輯器開啟 .env
nano .env
# 或
code .env
# 或
open -e .env
```

修改這一行：
```
GEMINI_API_KEY=你的實際金鑰
```

儲存並關閉。

---

## 第三步：測試功能 (2 分鐘)

### 測試 1: 語音互動

```bash
# 啟動虛擬環境（如果還沒啟動）
source venv/bin/activate

# 執行語音測試
python scripts/test_voice.py
```

**會發生什麼：**
- 🧠 測試 Gemini AI 對話（問 3 個問題）
- 🔊 生成語音檔案（存在 `data/audio/`）
- ✅ 顯示完整流程結果

### 測試 2: 視覺辨識

```bash
python scripts/test_vision.py
```

**會發生什麼：**
- 📷 開啟你的 Mac 攝像頭
- 👁️ 即時顯示人體骨架
- 📏 估算你與攝像頭的距離
- 按 `q` 退出

### 測試 3: 完整互動

```bash
python scripts/demo_chat.py
```

選擇模式：
- **選項 1**：自動播放預設場景（3 個示範問題）
- **選項 2**：互動模式（自己輸入問題）

---

## 💰 成本說明

### Gemini 免費額度

| 功能 | 免費額度 | 足夠用嗎？ |
|------|----------|-----------|
| Gemini 2.0 Flash | 每分鐘 15 次請求 | ✅ 測試綽綽有餘 |
| gTTS 語音合成 | 無限制 | ✅ 完全免費 |
| Google Speech Recognition | 每月 60 分鐘 | ✅ 測試足夠 |

**對於開發測試來說，完全免費！** 🎉

---

## 常見問題排解

### ❌ 找不到 Gemini API Key

**錯誤訊息：**
```
❌ 錯誤: 請先設定 GEMINI_API_KEY 環境變數
```

**解決方法：**
1. 確認 `.env` 檔案存在
2. 確認 API Key 已正確填入
3. 重新執行測試腳本

---

### ❌ Gemini API 錯誤

**錯誤訊息：**
```
❌ Gemini API 錯誤: 429 Resource exhausted
```

**解決方法：**
這表示超過每分鐘 15 次的免費限制，等一分鐘再試即可。

---

### ❌ 攝像頭無法開啟

**錯誤訊息：**
```
❌ 無法開啟攝像頭 0
```

**解決方法：**
1. **系統偏好設定** → **隱私權與安全性** → **相機**
2. 勾選 **Terminal** 或 **iTerm**
3. 重新執行 `python scripts/test_vision.py`

---

### ❌ gTTS 套件錯誤

**錯誤訊息：**
```
ImportError: No module named 'gtts'
```

**解決方法：**
```bash
pip install gtts
```

---

## 🎨 客製化設定

### 更換語音語言

編輯 `.env`，修改 `TTS_LANGUAGE`：

```
TTS_LANGUAGE=zh-CN  # 簡體中文
TTS_LANGUAGE=en     # 英語
TTS_LANGUAGE=ja     # 日語
```

### 調整 AI 個性

編輯 `src/voice/llm.py`，找到 `system_prompt`：

```python
self.system_prompt = """你是一個溫柔、有耐心的陪讀小助手。
# 這裡改成你想要的個性！
"""
```

### 使用不同的 Gemini 模型

編輯 `.env`：

```
GEMINI_MODEL=gemini-2.0-flash-exp     # 最新實驗版（推薦）
GEMINI_MODEL=gemini-1.5-flash         # 穩定版
GEMINI_MODEL=gemini-1.5-pro           # 更強但較慢
```

---

## 🆚 Gemini vs OpenAI 比較

| 項目 | Google Gemini | OpenAI |
|------|---------------|--------|
| **對話 API** | 免費（有限制） | 付費 $0.15/1M tokens |
| **語音合成** | gTTS 免費 | $15/1M 字元 |
| **語音辨識** | 免費 60 分鐘/月 | $0.006/分鐘 |
| **速度** | ⚡⚡⚡ 很快 | ⚡⚡ 快 |
| **繁中支援** | ✅ 優秀 | ✅ 優秀 |
| **需要信用卡** | ❌ 不需要 | ✅ 需要 |

---

## 🎉 完成！

現在你有一個使用 **Google Gemini** 的 AI 小助手了！

**接下來可以：**
- 📝 客製化對話邏輯
- 🎯 加入更多功能
- 🤖 準備硬體整合
- 💰 **完全不花錢測試！**

**有問題隨時問！** 💪
