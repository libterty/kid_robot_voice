"""
LLM 對話引擎模組
支援 Ollama (本地) 和 Gemini (雲端)
支援 Multi-Agent 模式
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ChatBot:
    """陪讀小助手對話引擎"""
    
    def __init__(self, save_conversation: bool = None, use_multi_agent: bool = None):
        self.backend = os.getenv('AI_BACKEND', 'ollama').lower()
        self.save_conversation = save_conversation if save_conversation is not None else \
                                 os.getenv('SAVE_CONVERSATION', 'true').lower() == 'true'
        
        # Multi-Agent 模式
        self.use_multi_agent = use_multi_agent if use_multi_agent is not None else \
                               os.getenv('USE_MULTI_AGENT', 'true').lower() == 'true'
        
        # 系統提示詞：定義機器人的角色（單一 Agent 模式）
        self.system_instruction = """你是一個溫柔、有耐心的陪讀小助手。
你的任務是陪伴 5-12 歲的小朋友閱讀和學習。

回答原則：
1. 用淺顯易懂的語言,避免過於艱深的詞彙
2. 多用比喻和生活化的例子
3. 鼓勵小朋友思考,不直接給答案
4. 保持正向、鼓勵的態度
5. 回答簡潔,每次不超過 100 字
6. 如果是危險或不適當的問題,溫和地引導到正確方向

重要：數學公式符號（如 \\div, \\times, \\[ \\] 等）要改成用文字描述：「10 除以 5 等於 2」而不是「10 ÷ 5 = 2」"""
        
        # 對話歷史
        self.chat_history = []
        
        # 日誌目錄
        self.log_dir = Path(os.getenv('DATA_DIR', './data')) / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化對應的後端
        if self.backend == 'ollama':
            self._init_ollama()
        elif self.backend == 'gemini':
            self._init_gemini()
        else:
            raise ValueError(f"不支援的 AI 後端: {self.backend}")
        
        # 初始化 Multi-Agent 系統（如果啟用）
        if self.use_multi_agent:
            self._init_multi_agent()
    
    def _init_ollama(self):
        """初始化 Ollama 後端"""
        try:
            import ollama
            self.client = ollama.Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
            self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
            
            # 測試連線
            try:
                self.client.list()
                print(f"✅ 使用 Ollama 本地模型: {self.model_name}")
            except Exception as e:
                print(f"⚠️  無法連線到 Ollama: {e}")
                print("💡 請確認 Ollama 已啟動: ollama serve")
                raise
                
        except ImportError:
            print("❌ 請先安裝 ollama: pip install ollama")
            raise
    
    def _init_gemini(self):
        """初始化 Gemini 後端"""
        try:
            from google import genai
            from google.genai import types
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("請設定 GEMINI_API_KEY 環境變數")
            
            self.client = genai.Client(api_key=api_key)
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            self.types = types
            
            print(f"✅ 使用 Gemini 雲端模型: {self.model_name}")
            
        except ImportError:
            print("❌ 請先安裝 google-genai: pip install google-genai")
            raise
    
    def _init_multi_agent(self):
        """初始化 Multi-Agent 系統"""
        try:
            # 將 src 目錄加入 Python 路徑
            src_dir = Path(__file__).parent.parent
            if str(src_dir) not in sys.path:
                sys.path.insert(0, str(src_dir))
            
            from agents import MultiAgentOrchestrator
            
            self.orchestrator = MultiAgentOrchestrator(self.client)
            print("✅ Multi-Agent 模式已啟用")
            
        except Exception as e:
            print(f"⚠️  無法載入 Multi-Agent 系統: {e}")
            print("💡 將使用單一 Agent 模式")
            self.use_multi_agent = False
            self.orchestrator = None
    
    def chat(self, user_message: str, verbose: bool = False) -> str:
        """
        與 AI 對話
        
        Args:
            user_message: 使用者輸入的訊息
            verbose: 是否顯示詳細日誌
            
        Returns:
            AI 的回應
        """
        try:
            # 使用 Multi-Agent 模式
            if self.use_multi_agent and self.orchestrator:
                # 顯示路由過程
                if verbose or os.getenv('SHOW_ROUTING', 'false').lower() == 'true':
                    print(f"\n{'='*60}")
                    print(f"🔍 [路由分析] 問題: {user_message}")
                
                response = self.orchestrator.process_question(user_message, verbose=verbose)
                
                # 顯示使用的 Agent
                if verbose or os.getenv('SHOW_ROUTING', 'false').lower() == 'true':
                    last_agent = self.orchestrator.context.get('last_agent')
                    print(f"✅ [使用 Agent] {last_agent}")
                    print(f"{'='*60}\n")
                
                # 儲存對話記錄
                if self.save_conversation:
                    self._save_log(user_message, response, agent='multi-agent')
                
                return response
            
            # 使用單一 Agent 模式
            if self.backend == 'ollama':
                return self._chat_ollama(user_message)
            elif self.backend == 'gemini':
                return self._chat_gemini(user_message)
                
        except Exception as e:
            print(f"❌ AI 對話錯誤: {e}")
            import traceback
            traceback.print_exc()
            return "抱歉，我現在有點累了，等一下再聊好嗎？"
    
    def _chat_ollama(self, user_message: str) -> str:
        """使用 Ollama 對話（單一 Agent）"""
        # 建立完整的對話訊息
        messages = []
        
        # 加入系統指示（只在第一次）
        if not self.chat_history:
            messages.append({
                'role': 'system',
                'content': self.system_instruction
            })
        
        # 加入歷史對話
        messages.extend(self.chat_history)
        
        # 加入當前訊息
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        # 呼叫 Ollama API
        response = self.client.chat(
            model=self.model_name,
            messages=messages
        )
        
        ai_response = response['message']['content']
        
        # 更新對話歷史
        self.chat_history.append({
            'role': 'user',
            'content': user_message
        })
        self.chat_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # 儲存對話記錄
        if self.save_conversation:
            self._save_log(user_message, ai_response)
        
        return ai_response
    
    def _chat_gemini(self, user_message: str) -> str:
        """使用 Gemini 對話（單一 Agent）"""
        # 建立完整的對話內容
        contents = []
        
        # 加入系統指示（作為第一條訊息）
        if not self.chat_history:
            contents.append(self.types.Content(
                role='user',
                parts=[self.types.Part(text=self.system_instruction)]
            ))
            contents.append(self.types.Content(
                role='model',
                parts=[self.types.Part(text='好的，我明白了！我會用淺顯易懂的方式陪伴小朋友學習。')]
            ))
        
        # 加入歷史對話
        for msg in self.chat_history:
            contents.append(self.types.Content(
                role=msg['role'] if msg['role'] != 'assistant' else 'model',
                parts=[self.types.Part(text=msg['content'])]
            ))
        
        # 加入當前訊息
        contents.append(self.types.Content(
            role='user',
            parts=[self.types.Part(text=user_message)]
        ))
        
        # 呼叫 Gemini API
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents
        )
        
        ai_response = response.text
        
        # 更新對話歷史
        self.chat_history.append({
            'role': 'user',
            'content': user_message
        })
        self.chat_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # 儲存對話記錄
        if self.save_conversation:
            self._save_log(user_message, ai_response)
        
        return ai_response
    
    def _save_log(self, user_msg: str, ai_msg: str, agent: str = 'single'):
        """儲存對話記錄到日誌檔案"""
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"conversation_{timestamp}.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "assistant": ai_msg,
            "backend": self.backend,
            "model": self.model_name,
            "mode": "multi-agent" if self.use_multi_agent else "single-agent",
            "agent_used": agent
        }
        
        if self.use_multi_agent and self.orchestrator:
            log_entry['last_agent'] = self.orchestrator.context.get('last_agent')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def reset_conversation(self):
        """重置對話歷史"""
        self.chat_history = []
        
        if self.use_multi_agent and self.orchestrator:
            self.orchestrator.reset_context()
        
        print("✅ 對話歷史已清除")
