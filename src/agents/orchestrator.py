"""
Multi-Agent 協調器
整合 Gateway 和所有專業 Agents
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from .gateway_agent import GatewayAgent
from .specialist_agents import (
    MathTutorAgent,
    ScienceTutorAgent,
    LanguageTutorAgent,
    PedagogyAgent,
    AssessmentAgent,
    CompanionAgent
)

load_dotenv()


class MultiAgentOrchestrator:
    """Multi-Agent 系統協調器"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        # 初始化 Gateway
        self.gateway = GatewayAgent(llm_client)
        
        # 初始化所有專業 Agents
        self.agents = {
            'math_tutor': MathTutorAgent(llm_client, self.model_name),
            'science_tutor': ScienceTutorAgent(llm_client, self.model_name),
            'language_tutor': LanguageTutorAgent(llm_client, self.model_name),
            'pedagogy': PedagogyAgent(llm_client, self.model_name),
            'assessment': AssessmentAgent(llm_client, self.model_name),
            'companion': CompanionAgent(llm_client, self.model_name)
        }
        
        # 對話上下文
        self.context = {
            'history': [],
            'student_level': 'elementary',  # elementary, intermediate, advanced
            'last_agent': None
        }
        
        print("✅ Multi-Agent 系統已初始化")
        print(f"   可用 Agents: {', '.join(self.agents.keys())}")
    
    def process_question(self, question: str, verbose: bool = False) -> str:
        """
        處理學生問題
        
        Args:
            question: 學生問題
            verbose: 是否顯示詳細過程
            
        Returns:
            最終回應
        """
        # 步驟 1: 路由決策
        routing_result = self.gateway.route_question(question)
        target_agent_name = routing_result['agent']
        confidence = routing_result['confidence']
        
        # 顯示路由資訊
        if verbose:
            print(f"\n🎯 [路由決策]")
            print(f"   問題類型: {self._get_question_type(question)}")
            print(f"   目標 Agent: {target_agent_name}")
            print(f"   信心度: {confidence:.2%}")
            print(f"   推理: {routing_result.get('reasoning', 'N/A')}")
        
        # 步驟 2: 呼叫專業 Agent
        if target_agent_name not in self.agents:
            if verbose:
                print(f"   ⚠️  Agent 不存在，使用後備: companion")
            target_agent_name = 'companion'  # 後備
        
        target_agent = self.agents[target_agent_name]
        
        if verbose:
            print(f"\n🤖 [{target_agent_name}] 正在處理...")
            print(f"   Agent 描述: {self._get_agent_description(target_agent_name)}")
        
        # 呼叫 Agent 處理
        response = target_agent.process(question, self.context)
        
        if verbose:
            print(f"   回應長度: {len(response)} 字")
        
        # 步驟 3: 記錄對話歷史
        self.context['history'].append({
            'role': 'user',
            'content': question
        })
        self.context['history'].append({
            'role': 'assistant',
            'content': response
        })
        
        # 限制歷史長度（保留最近 10 輪對話）
        if len(self.context['history']) > 20:
            self.context['history'] = self.context['history'][-20:]
        
        self.context['last_agent'] = target_agent_name
        
        if verbose:
            print(f"\n✅ 處理完成")
        
        return response
    
    def _get_question_type(self, question: str) -> str:
        """分析問題類型"""
        question_lower = question.lower()
        
        if any(kw in question for kw in ['數學', '計算', '加', '減', '乘', '除', '等於']):
            return '數學問題'
        elif any(kw in question for kw in ['為什麼', '怎麼', '如何', '原理']):
            return '科學/概念問題'
        elif any(kw in question for kw in ['寫', '造句', '作文']):
            return '語文問題'
        elif any(kw in question for kw in ['學習', '記憶', '方法']):
            return '學習方法'
        elif any(kw in question for kw in ['對不對', '答案', '檢查']):
            return '答案評估'
        else:
            return '一般對話'
    
    def _get_agent_description(self, agent_name: str) -> str:
        """取得 Agent 描述"""
        descriptions = {
            'math_tutor': '數學專家 - 處理計算和數學概念',
            'science_tutor': '科學專家 - 解釋自然現象和科學原理',
            'language_tutor': '語文專家 - 指導寫作和語言學習',
            'pedagogy': '教學法專家 - 提供學習方法和技巧',
            'assessment': '評估專家 - 檢查答案和評估理解',
            'companion': '陪伴專家 - 提供情緒支持和鼓勵'
        }
        return descriptions.get(agent_name, '未知 Agent')
    
    def get_agent_info(self, agent_name: str) -> str:
        """取得 Agent 資訊"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            return agent.get_system_prompt()
        return "Agent 不存在"
    
    def reset_context(self):
        """重置對話上下文"""
        self.context = {
            'history': [],
            'student_level': 'elementary',
            'last_agent': None
        }
        print("✅ 對話上下文已清除")
    
    def get_stats(self) -> Dict[str, Any]:
        """取得系統統計"""
        return {
            'total_turns': len(self.context['history']) // 2,
            'last_agent': self.context['last_agent'],
            'available_agents': list(self.agents.keys())
        }
