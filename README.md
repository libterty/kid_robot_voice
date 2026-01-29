# 🤖 家庭陪讀機器人 - 極簡開發版

> 專為 Mac M3 Max 設計的輕量級開發環境  
> **新增：支援本地 Ollama - 完全免費、無需網路、保護隱私！**

## 🎯 專案目標

打造一個能與小孩互動的 AI 陪讀助手：
- 🗣️ **語音互動**：支援 Ollama (本地) 或 Gemini (雲端)
- 🔊 **語音合成**：使用 gTTS（完全免費）
- 👁️ **視覺辨識**：看得到小孩在哪（為之後的跟隨功能做準備）
- 💬 **互動對話**：一問一答模式，即時回應
- 📚 **教育內容**：回答十萬個為什麼

## 🆕 兩種 AI 後端選擇

| 特性 | Ollama (本地) | Gemini (雲端) |
|------|---------------|---------------|
| **成本** | ✅ 完全免費 | 🆓 有免費額度 |
| **隱私** | ✅ 完全本地 | ⚠️ 需上傳雲端 |
| **速度** | ⚡⚡⚡ M3 Max 快 | ⚡⚡ 受網路影響 |
| **離線** | ✅ 可離線使用 | ❌ 需要網路 |
| **設定** | 需安裝 Ollama | 只需 API Key |

**推薦：使用 Ollama！** 完全免費、保護隱私、M3 Max 跑得很快。

## ⚡ 快速開始（Ollama 版）

### 步驟 1: 安裝 Ollama

```bash
# 使用 Homebrew 安裝
brew install ollama

# 啟動 Ollama 服務（保持運行）
ollama serve
```

### 步驟 2: 下載 AI 模型

```bash
# 開啟新終端，下載推薦模型
ollama pull llama3.2:3b  # 2GB，快速
# 或
ollama pull qwen2.5:7b   # 4.4GB，繁中更好
```

### 步驟 3: 設定專案

```bash
# 進入專案目錄
cd kid_robot_project

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# .env 中已預設使用 Ollama，不需要修改！
```

### 步驟 4: 開始對話

```bash
# 互動式一問一答
python scripts/interactive_chat.py
```

**就這麼簡單！** 詳細設定請看 [Ollama 設定指南](OLLAMA_SETUP.md)

---

## 💬 三種對話模式

### 1. 文字對話（最簡單）

```bash
python scripts/interactive_chat.py
```
- ✅ 打字提問，文字回答
- ✅ 可選語音朗讀
- ✅ 適合開發測試

### 2. 語音對話（最自然）⭐ 新功能

```bash
python scripts/voice_chat.py
```
- 🎤 **麥克風說話**提問
- 🔊 **喇叭播放**回答
- ✅ 真正的語音互動
- ✅ 適合實際使用

### 3. 測試模式（驗證功能）

```bash
python scripts/test_voice.py
```
- ✅ 測試 AI 對話
- ✅ 測試語音合成
- ✅ 適合功能驗證

---

## 🎤 語音對話快速開始

### 安裝音訊套件

```bash
# 安裝 PortAudio
brew install portaudio

# 安裝 Python 音訊套件
pip install pyaudio
```

### 授予麥克風權限

1. **系統偏好設定** → **隱私權與安全性** → **麥克風**
2. 勾選 **Terminal** 或 **iTerm**

### 開始語音對話

```bash
python scripts/voice_chat.py
```

**使用方式：**
- 聽到「請說話」後開始提問
- 說完後自動識別並回答
- 說「退出」結束對話
- 說「重置」清除歷史

詳細設定請看 [語音對話設定指南](VOICE_SETUP.md)

---

## 🆓 為什麼選擇 Gemini？

### 成本比較

| 功能 | OpenAI | Google Gemini |
|------|--------|---------------|
| 對話 | GPT-4o-mini<br>$0.15/1M tokens | Gemini 2.0 Flash<br>**完全免費**（有額度限制） |
| TTS | $15/1M 字元 | gTTS **完全免費** |
| STT | $0.006/分鐘 | Google Speech<br>**每月 60 分鐘免費** |

**每日測試成本**: OpenAI ~$1 → Gemini **$0** ✨

### 效能比較

- ⚡ **速度**: Gemini 2.0 Flash 比 GPT-4o-mini 快 2-3 倍
- 🎯 **準確度**: 繁體中文理解能力相當
- 💰 **免費額度**: 每分鐘 15 次請求（對測試綽綽有餘）

## 🔑 取得 Gemini API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登入你的 Google 帳號
3. 點選「Get API Key」
4. 複製你的 API Key
5. 貼到 `.env` 檔案中

**完全免費！不需要綁信用卡！** 🎉

## 📁 專案結構

```
kid_robot_project/
├── README.md                 # 你正在看的檔案
├── requirements.txt          # Python 依賴套件
├── .env.example             # 環境變數範本
├── .env                     # 你的 API Key（不會上傳 git）
├── .gitignore              # Git 忽略清單
│
├── src/                    # 核心程式碼
│   ├── voice/             # 語音模組
│   │   ├── __init__.py
│   │   ├── stt.py        # 語音轉文字（Google Speech）
│   │   ├── llm.py        # AI 對話引擎（Gemini）
│   │   └── tts.py        # 文字轉語音（gTTS）
│   │
│   └── vision/            # 視覺模組
│       ├── __init__.py
│       └── detector.py    # 人體偵測
│
├── scripts/               # 測試腳本
│   ├── test_voice.py     # 測試語音互動
│   ├── test_vision.py    # 測試攝像頭偵測
│   └── demo_chat.py      # 完整對話示範
│
└── data/                  # 資料存放
    ├── logs/             # 對話記錄
    ├── audio/            # 音訊檔案
    └── config/           # 設定檔
```

## 🧪 測試各個模組

### 測試 1: AI 對話能力
```bash
python scripts/test_voice.py
```
會測試：
- ✅ Gemini API 連線
- ✅ 文字對話能力
- ✅ 語音合成功能（gTTS）

### 測試 2: 視覺辨識
```bash
python scripts/test_vision.py
```
會開啟你的 Mac 攝像頭，即時顯示：
- ✅ 人體骨架偵測
- ✅ 距離估算（準備用於跟隨功能）

### 測試 3: 完整互動示範
```bash
python scripts/demo_chat.py
```
模擬小孩提問的完整流程

## 🔧 環境變數說明

編輯 `.env` 檔案：

```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here   # 必填
GEMINI_MODEL=gemini-2.0-flash-exp          # 推薦使用最新版

# 語音設定
TTS_LANGUAGE=zh-TW                         # gTTS 語言
TTS_SLOW=false                             # 是否慢速播放
STT_LANGUAGE=zh-TW                         # 語音辨識語言

# 系統設定
LOG_LEVEL=INFO
SAVE_CONVERSATION=true                     # 是否儲存對話記錄
```

## 💰 成本估算（完全免費！）

使用 Google 免費服務的每日成本：
- **Gemini 2.0 Flash**: 免費（每分鐘 15 次請求）
- **gTTS**: 完全免費
- **Google Speech Recognition**: 每月 60 分鐘免費

**預估一天測試成本**: $0 USD ✨

## 🚀 下一步計畫

- [ ] Week 1-2: 完善語音對話邏輯
- [ ] Week 3: 加入對話記憶功能（記得小孩喜好）
- [ ] Week 4: 整合視覺追蹤（在螢幕上模擬跟隨）
- [ ] Week 5+: 考慮硬體整合（Raspberry Pi / Jetson）

## 🐛 常見問題

**Q: 我沒有 Gemini API Key 怎麼辦？**  
A: 去 https://aistudio.google.com/apikey 申請，完全免費，不需要信用卡！

**Q: 出現模型 404 錯誤怎麼辦？**  
A: 不用擔心！程式已經改成**自動選擇模型**，只要填入 API Key 就會自動找到可用的模型。如果還是有問題，執行 `python scripts/check_gemini_models.py` 查看詳細資訊。

**Q: 我想查看我有哪些可用的模型？**  
A: 執行 `python scripts/check_gemini_models.py`

**Q: gTTS 的語音品質如何？**  
A: 對於陪讀機器人來說足夠清晰，而且是 Google 官方的語音引擎

**Q: 有請求次數限制嗎？**  
A: 免費版每分鐘 15 次請求，對測試來說綽綽有餘

**Q: 攝像頭權限被拒絕？**  
A: 系統偏好設定 > 隱私權與安全性 > 相機 > 勾選 Terminal

**Q: 遇到其他問題？**  
A: 查看 [故障排除指南](TROUBLESHOOTING.md)

## 📝 授權

MIT License - 隨便改隨便用

---

**Made with ❤️ for 未來的陪讀小助手**  
**Powered by Google Gemini 🚀**
