# 📦 套件升級指南

## ⚠️ 重要通知

Google 已棄用 `google-generativeai` 套件，請升級到新的 `google-genai` 套件。

## 🔄 如何升級

### 步驟 1: 移除舊套件

```bash
pip uninstall google-generativeai -y
```

### 步驟 2: 安裝新套件

```bash
pip install --upgrade google-genai
```

### 步驟 3: 重新安裝所有依賴

```bash
pip install -r requirements.txt
```

### 步驟 4: 測試

```bash
python scripts/check_gemini_models.py
python scripts/test_voice.py
```

## ✅ 已更新的檔案

專案已經更新為使用新的 SDK：
- ✅ `requirements.txt` - 改用 `google-genai`
- ✅ `src/voice/llm.py` - 使用新的 API
- ✅ `scripts/check_gemini_models.py` - 使用新的 SDK

## 🆕 新 SDK 的改進

1. **更穩定** - 官方正式支援的套件
2. **更清晰** - API 設計更直覺
3. **更完整** - 更好的錯誤處理

## 💡 如果遇到問題

### 錯誤: ModuleNotFoundError: No module named 'google.generativeai'

**解決方法：**
```bash
pip uninstall google-generativeai -y
pip install google-genai
```

### 錯誤: ImportError: cannot import name 'genai'

**解決方法：**
```bash
pip install --upgrade google-genai
```

### 完全重新安裝

```bash
# 移除虛擬環境
rm -rf venv

# 重新建立
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

## 📚 新 SDK 文件

- [官方文件](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- [GitHub](https://github.com/googleapis/python-genai)
