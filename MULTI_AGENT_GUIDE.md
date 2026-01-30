# 🤖 Multi-Agent 系統使用指南

## 什麼是 Multi-Agent？

Multi-Agent 系統使用多個專業 AI Agent 協作，每個 Agent 專精不同領域，提供更專業、更精準的回答。

## 🏗️ 系統架構

```
學生提問
    ↓
Gateway Agent (主控)
    ├→ 分析問題類型
    ├→ 選擇專業 Agent
    └→ 整合回應
    ↓
專業 Agents
    ├─ Math Tutor (數學專家)
    ├─ Science Tutor (科學專家)
    ├─ Language Tutor (語文專家)
    ├─ Pedagogy (教學法專家)
    ├─ Assessment (評估專家)
    └─ Companion (陪伴專家)
    ↓
最終回答
```

## 🎯 六大專業 Agents

### 1. Math Tutor Agent 📐
**專長：** 數學問題
- 計算題（加減乘除、分數、小數）
- 幾何問題
- 代數方程
- 數學概念解釋

**範例：**
```
問：3 + 5 等於多少？
→ 路由到: Math Tutor
答：我們來一起算算看！3 加 5...
```

### 2. Science Tutor Agent 🔬
**專長：** 科學問題
- 物理現象（光、聲音、力）
- 化學反應
- 生物知識
- 地球科學

**範例：**
```
問：為什麼天空是藍色的？
→ 路由到: Science Tutor
答：這是因為光的散射...
```

### 3. Language Tutor Agent 📚
**專長：** 語言學習
- 寫作指導
- 造句練習
- 閱讀理解
- 語詞解釋

**範例：**
```
問：怎麼寫好作文？
→ 路由到: Language Tutor
答：寫作文有幾個小秘訣...
```

### 4. Pedagogy Agent 🎓
**專長：** 學習方法
- 學習技巧
- 記憶方法
- 時間管理
- 解題策略

**範例：**
```
問：怎麼快速記住單字？
→ 路由到: Pedagogy
答：我教你幾個記憶技巧...
```

### 5. Assessment Agent ✅
**專長：** 答案評估
- 檢查答案正確性
- 分析錯誤原因
- 追蹤學習進度
- 識別知識盲點

**範例：**
```
問：我的答案是 8，對不對？
→ 路由到: Assessment
答：讓我檢查一下...
```

### 6. Companion Agent 💝
**專長：** 情緒支持
- 鼓勵和安慰
- 學習動機激發
- 閒聊互動
- 情緒疏導

**範例：**
```
問：我覺得學習好難啊
→ 路由到: Companion
答：沒關係，每個人都有覺得困難的時候...
```

## ⚙️ 啟用/關閉 Multi-Agent

### 方法 1: 環境變數設定

編輯 `.env`:
```bash
# 啟用 Multi-Agent 模式
USE_MULTI_AGENT=true

# 關閉 Multi-Agent 模式（使用單一 Agent）
USE_MULTI_AGENT=false
```

### 方法 2: 程式碼設定

```python
# 啟用 Multi-Agent
bot = ChatBot(use_multi_agent=True)

# 關閉 Multi-Agent
bot = ChatBot(use_multi_agent=False)
```

## 🚀 使用範例

### 完整測試

```bash
cd kid_robot_project
source venv/bin/activate

# 測試 Multi-Agent 系統
python src/voice/llm.py
```

### 在語音對話中使用

```bash
# 確認 .env 中 USE_MULTI_AGENT=true
python scripts/voice_chat.py
```

對話時會自動路由到專業 Agent：

```
問：3 + 5 等於多少？
🎯 路由到: math_tutor
答：[數學專家的回答]

問：為什麼會下雨？
🎯 路由到: science_tutor
答：[科學專家的回答]
```

## 📊 Multi-Agent vs 單一 Agent

| 特性 | Multi-Agent | 單一 Agent |
|------|-------------|-----------|
| **專業度** | ✅ 每個領域都有專家 | ⚠️ 通才但不專精 |
| **回答品質** | ✅ 更精準、更專業 | ⚠️ 一般品質 |
| **速度** | ⚠️ 稍慢（需路由） | ✅ 較快 |
| **資源消耗** | ⚠️ 較高 | ✅ 較低 |
| **適用場景** | 正式教學、作業輔導 | 休閒聊天、快速問答 |

## 💡 使用建議

### 什麼時候用 Multi-Agent？

✅ **推薦使用：**
- 正式的學習輔導
- 作業題目解答
- 需要深入解釋的問題
- 需要評估學習成效時

❌ **不建議使用：**
- 快速閒聊
- 簡單問候
- 網路不穩定時
- 電腦效能較低時

### 優化建議

1. **使用較大的模型**
   ```bash
   # .env
   OLLAMA_MODEL=qwen2.5:7b  # 繁中更好
   # 或
   OLLAMA_MODEL=llama3.1:8b  # 能力更強
   ```

2. **確保 Ollama 穩定運行**
   ```bash
   ollama serve  # 保持運行
   ```

3. **定期清除對話記錄**
   ```
   說「重置」清除記憶
   ```

## 🔍 進階功能

### 查看路由決策

修改 `scripts/voice_chat.py`，在對話時顯示路由資訊：

```python
# 在 VoiceChat.run() 中
response = self.bot.chat(user_input)

# 顯示使用的 Agent
if hasattr(self.bot, 'orchestrator') and self.bot.orchestrator:
    last_agent = self.bot.orchestrator.context.get('last_agent')
    print(f"[使用 Agent: {last_agent}]")
```

### 自訂 Agent

可以在 `src/agents/specialist_agents.py` 中新增自己的專業 Agent：

```python
class HistoryTutorAgent(BaseAgent):
    """歷史家教 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是歷史老師..."""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        # 處理歷史問題
        pass
```

然後在 `orchestrator.py` 中註冊：

```python
self.agents['history_tutor'] = HistoryTutorAgent(llm_client, self.model_name)
```

## 🐛 故障排除

### 問題 1: Multi-Agent 無法啟動

**錯誤訊息：**
```
⚠️  無法載入 Multi-Agent 系統
💡 將使用單一 Agent 模式
```

**解決方法：**
1. 確認 `src/agents/` 目錄存在
2. 確認所有 Agent 檔案都已創建
3. 檢查 Python 路徑

### 問題 2: 路由不準確

**現象：** 數學問題被路由到科學 Agent

**解決方法：**
1. 使用更大的模型（提高路由準確度）
2. 在問題中加入明確關鍵字
3. 調整 `gateway_agent.py` 中的關鍵字列表

### 問題 3: 回答太慢

**解決方法：**
1. 關閉 Multi-Agent：`USE_MULTI_AGENT=false`
2. 使用更小的模型：`OLLAMA_MODEL=llama3.2:3b`
3. 確保 Ollama 正常運行

## 📈 效能測試

```bash
# 測試不同模式的回答品質
python << 'EOF'
from src.voice import ChatBot

# Multi-Agent 模式
bot_multi = ChatBot(use_multi_agent=True)
response_multi = bot_multi.chat("3 + 5 等於多少？")

# 單一 Agent 模式
bot_single = ChatBot(use_multi_agent=False)
response_single = bot_single.chat("3 + 5 等於多少？")

print(f"Multi-Agent: {response_multi}")
print(f"Single-Agent: {response_single}")
EOF
```

---

**Multi-Agent 系統讓陪讀機器人更專業！** 🤖✨