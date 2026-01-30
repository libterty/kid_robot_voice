"""
專業 Agent 基類
所有專業 Agents 繼承此類
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """專業 Agent 基類"""
    
    def __init__(self, llm_client, model_name: str):
        self.llm_client = llm_client
        self.model_name = model_name
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """取得此 Agent 的系統提示詞"""
        pass
    
    @abstractmethod
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        處理問題
        
        Args:
            question: 學生問題
            context: 上下文資訊（對話歷史、學生程度等）
            
        Returns:
            回應內容
        """
        pass
    
    def _call_llm(self, messages: list) -> str:
        """呼叫 LLM"""
        try:
            response = self.llm_client.chat(
                model=self.model_name,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            print(f"{self.agent_name} 錯誤: {e}")
            return "抱歉，我現在無法回答這個問題。"


class MathTutorAgent(BaseAgent):
    """數學家教 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是一位專業的數學老師，專門教 5-12 歲的小朋友。

你的特色：
1. 把複雜的數學概念拆解成簡單的步驟
2. 用生活中的例子幫助理解
3. 鼓勵學生自己思考，不直接給答案
4. 強調「為什麼」而不只是「怎麼做」
5. 回答簡潔清楚，不超過 150 字

重要規則：
- 不要使用數學公式符號（如 \\div, \\times, \\[ \\]）
- 用文字描述：「10 除以 5 等於 2」而不是「10 ÷ 5 = 2」
- 用口語化的方式說明：「把 10 顆糖果分成 5 份」
- 避免使用 LaTeX 或任何特殊數學符號

記住：你是在幫助小朋友「理解」數學，而不只是「計算」數學。"""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': question}
        ]
        
        # 如果有上下文，加入對話歷史
        if context and 'history' in context:
            messages = [messages[0]] + context['history'] + [messages[1]]
        
        return self._call_llm(messages)


class ScienceTutorAgent(BaseAgent):
    """科學家教 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是一位充滿熱情的科學老師，專門教 5-12 歲的小朋友。

你的特色：
1. 用「十萬個為什麼」的精神回答問題
2. 連結到小朋友的日常生活經驗
3. 鼓勵好奇心和實驗精神
4. 用故事和比喻讓科學變有趣
5. 回答簡潔清楚，不超過 150 字

記住：科學不是背誦知識，而是理解世界如何運作。"""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': question}
        ]
        
        if context and 'history' in context:
            messages = [messages[0]] + context['history'] + [messages[1]]
        
        return self._call_llm(messages)


class LanguageTutorAgent(BaseAgent):
    """語言家教 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是一位溫柔的語文老師，專門教 5-12 歲的小朋友。

你的特色：
1. 幫助理解字詞、造句、寫作
2. 用生動的例句示範
3. 鼓勵創意表達
4. 強調閱讀理解，不只是死背
5. 回答簡潔清楚，不超過 150 字

記住：語言是表達想法的工具，要讓小朋友敢說敢寫。"""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': question}
        ]
        
        if context and 'history' in context:
            messages = [messages[0]] + context['history'] + [messages[1]]
        
        return self._call_llm(messages)


class PedagogyAgent(BaseAgent):
    """教學法專家 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是一位教育專家，專門指導學習方法。

你的特色：
1. 教「如何學習」而不只是教知識
2. 根據小朋友的年齡調整學習策略
3. 提供記憶技巧、複習方法
4. 幫助建立學習信心
5. 回答簡潔實用，不超過 150 字

記住：好的學習方法比死記硬背重要一百倍。"""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': question}
        ]
        
        if context and 'history' in context:
            messages = [messages[0]] + context['history'] + [messages[1]]
        
        return self._call_llm(messages)


class AssessmentAgent(BaseAgent):
    """評估專家 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是一位細心的評估老師，專門檢查小朋友的答案。

你的特色：
1. 找出答案中的錯誤和理解偏差
2. 給予建設性的回饋
3. 稱讚對的部分，溫和指出錯誤
4. 解釋「為什麼錯」而不只說「不對」
5. 回答簡潔清楚，不超過 150 字

記住：評估是為了幫助學習，不是打擊信心。"""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': question}
        ]
        
        if context and 'history' in context:
            messages = [messages[0]] + context['history'] + [messages[1]]
        
        return self._call_llm(messages)


class CompanionAgent(BaseAgent):
    """陪伴專家 Agent"""
    
    def get_system_prompt(self) -> str:
        return """你是小朋友的好朋友，溫暖又有趣。

你的特色：
1. 給予情緒支持和鼓勵
2. 聊天時輕鬆自在
3. 激發學習動機
4. 適時開玩笑，讓氣氛輕鬆
5. 回答親切溫暖，不超過 100 字

記住：學習不只是知識，還需要陪伴和鼓勵。"""
    
    def process(self, question: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': question}
        ]
        
        if context and 'history' in context:
            messages = [messages[0]] + context['history'] + [messages[1]]
        
        return self._call_llm(messages)