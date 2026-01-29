# 🔧 Gemini API 故障排除指南

## 常見錯誤與解決方法

### 錯誤 1: 模型不存在（404 Not Found）

**錯誤訊息：**
```
404 models/gemini-2.0-flash-exp is not found for API version v1beta
```

**原因：**
- 模型名稱錯誤
- 模型在你的地區還未開放
- 使用了實驗版模型但帳號沒有權限

**解決方法：**

#### 方法 1: 使用檢查工具（推薦）
```bash
# 查看你的帳號可以使用哪些模型
python scripts/check_gemini_models.py
```

#### 方法 2: 改用穩定版模型
編輯 `.env` 檔案：
```bash
# 改成穩定版
GEMINI_MODEL=gemini-1.5-flash

# 或使用 Pro 版（更強但較慢）
GEMINI_MODEL=gemini-1.5-pro
```

#### 方法 3: 測試特定模型
```bash
# 測試 gemini-1.5-flash
python scripts/check_gemini_models.py gemini-1.5-flash

# 測試 gemini-1.5-pro
python scripts/check_gemini_models.py gemini-1.5-pro
```

---

### 錯誤 2: API Key 無效

**錯誤訊息：**
```
401 API key not valid
```

**解決方法：**

1. 確認 API Key 已正確複製到 `.env`
2. 檢查 API Key 格式（應該是一串英數字）
3. 重新產生 API Key：https://aistudio.google.com/apikey

---

### 錯誤 3: 超過免費額度

**錯誤訊息：**
```
429 Resource exhausted
```

**原因：**
- 超過每分鐘 15 次的請求限制

**解決方法：**
- 等待 1 分鐘後再試
- 在程式中加入延遲（`time.sleep(5)`）

---

### 錯誤 4: 網路連線問題

**錯誤訊息：**
```
Failed to connect to generativelanguage.googleapis.com
```

**解決方法：**
1. 檢查網路連線
2. 檢查防火牆設定
3. 如果在中國大陸，可能需要 VPN

---

## 推薦的模型設定

### 場景 1: 日常測試（推薦）
```bash
GEMINI_MODEL=gemini-1.5-flash
```
- ⚡ 速度快
- 💰 免費額度高
- ✅ 適合頻繁測試

### 場景 2: 複雜對話
```bash
GEMINI_MODEL=gemini-1.5-pro
```
- 🎯 更聰明
- 📚 更好的理解力
- ⚠️ 較慢，免費額度較少

### 場景 3: 嘗試最新功能
```bash
GEMINI_MODEL=gemini-2.0-flash-exp
```
- 🚀 最新功能
- ⚠️ 可能不穩定
- ⚠️ 可能不是所有地區都支援

---

## 快速診斷流程

```bash
# 1. 檢查環境變數
cat .env | grep GEMINI

# 2. 查看可用模型
python scripts/check_gemini_models.py

# 3. 測試語音功能
python scripts/test_voice.py

# 4. 如果還是有問題，檢查詳細錯誤
python scripts/test_voice.py 2>&1 | tee error.log
```

---

## 如果還是無法解決

1. 查看完整錯誤訊息
2. 前往 [Gemini API 文件](https://ai.google.dev/docs)
3. 檢查 [API 狀態頁面](https://status.cloud.google.com/)

---

## 其他資源

- 📚 [Gemini API 官方文件](https://ai.google.dev/tutorials/python_quickstart)
- 💬 [Google AI Discord 社群](https://discord.gg/google-ai-dev)
- 🐛 [回報問題](https://github.com/google/generative-ai-python/issues)
