"""
Gateway Agent - 主控代理
負責路由請求到專業 Agents
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class GatewayAgent:
    """主控代理 - 負責問題分類和路由"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        # 路由決策提示詞
        self.routing_prompt = """你是一個智能路由系統。分析學生的問題，判斷應該路由到哪個專業 Agent。

可用的 Agents:
1. math_tutor - 數學相關問題（計算、幾何、代數、分數、小數等）
2. science_tutor - 科學相關問題（物理、化學、生物、地球科學、天文、自然現象等）
3. language_tutor - 語言相關問題（國語、英語、寫作、閱讀理解、造句等）
4. pedagogy - 學習方法、解題技巧、如何記憶、學習策略等
5. assessment - 檢查答案、評估理解程度、判斷對錯
6. companion - 情緒支持、鼓勵、閒聊、非學習相關問題

重要規則：
- 如果問題包含「加減乘除、分數、小數、計算、等於」→ math_tutor
- 如果問題問「為什麼會XX現象」（如天空、下雨、光）→ science_tutor
- 如果問題關於「寫作、造句、閱讀理解、成語」→ language_tutor
- 如果問「如何提升閱讀/寫作」→ language_tutor（不是 pedagogy）
- 如果問「什麼是分數/小數」→ math_tutor（不是 language_tutor）
- 如果問「怎麼學習/記憶方法」→ pedagogy
- 如果問「我的答案對嗎」→ assessment
- 如果是打招呼或情緒問題 → companion

請只回答 Agent 名稱和信心度，格式: agent_name|confidence
例如: math_tutor|0.9

學生問題: {question}"""
    
    def route_question(self, question: str, verbose: bool = False) -> Dict[str, Any]:
        """
        路由問題到合適的 Agent
        
        Args:
            question: 學生的問題
            verbose: 是否顯示詳細過程
            
        Returns:
            路由結果 {agent: str, confidence: float, reasoning: str}
        """
        if verbose:
            print(f"\n🔍 [Gateway] 分析問題...")
        
        # 先嘗試關鍵字匹配
        fallback_agent = self._fallback_routing(question)
        matched_keywords = self._get_matched_keywords(question)
        
        if verbose and matched_keywords:
            print(f"   匹配關鍵字: {', '.join(matched_keywords)}")
            print(f"   關鍵字建議: {fallback_agent}")
        
        # 呼叫 LLM 進行路由決策
        messages = [
            {
                'role': 'system',
                'content': 'You are a smart question classifier.'
            },
            {
                'role': 'user',
                'content': self.routing_prompt.format(question=question)
            }
        ]
        
        try:
            response = self.llm_client.chat(
                model=self.model_name,
                messages=messages
            )
            
            result = response['message']['content'].strip()
            
            if verbose:
                print(f"   LLM 原始回應: {result}")
            
            # 解析結果
            if '|' in result:
                agent, confidence = result.split('|')
                agent = agent.strip()
                confidence = float(confidence)
            else:
                # 使用關鍵字匹配作為後備
                agent = fallback_agent
                confidence = 0.6
                if verbose:
                    print(f"   ⚠️  LLM 回應格式錯誤，使用關鍵字匹配")
            
            # 驗證 Agent 是否有效
            valid_agents = ['math_tutor', 'science_tutor', 'language_tutor', 
                          'pedagogy', 'assessment', 'companion']
            if agent not in valid_agents:
                if verbose:
                    print(f"   ⚠️  無效 Agent: {agent}，使用: {fallback_agent}")
                agent = fallback_agent
                confidence = 0.5
            
            reasoning = f"LLM 分析 + 關鍵字匹配"
            
            return {
                'agent': agent,
                'confidence': confidence,
                'reasoning': reasoning,
                'matched_keywords': matched_keywords,
                'fallback_suggestion': fallback_agent
            }
            
        except Exception as e:
            if verbose:
                print(f"   ❌ 路由錯誤: {e}")
            # 使用後備路由
            return {
                'agent': fallback_agent,
                'confidence': 0.5,
                'reasoning': '後備路由（關鍵字匹配）',
                'matched_keywords': matched_keywords,
                'error': str(e)
            }
    
    def _get_matched_keywords(self, question: str) -> List[str]:
        """取得匹配的關鍵字"""
        matched = []
        
        # 數學關鍵字（擴充）
        math_keywords = [
            '數學', '計算', '加', '減', '乘', '除', '幾何', '代數', 
            '方程', '分數', '小數', '等於', '多少', '幾個', '數字', 
            '算', '通分', '平分', '糖果', '元', '錢'
        ]
        if any(kw in question for kw in math_keywords):
            matched.extend([kw for kw in math_keywords if kw in question])
        
        # 科學關鍵字（擴充）
        science_keywords = [
            '科學', '物理', '化學', '生物', '實驗', '為什麼', '怎麼', 
            '原理', '現象', '光', '聲音', '能量', '力', '天空', '藍色', 
            '月亮', '太陽', '下雨', '雲', '風', '水', '植物', '動物', 
            '細胞', '光合作用', '呼吸', '消化', '恐龍', '隕石', '滅絕',
            '氧氣', '二氧化碳', '空氣', '雪', '冬天'
        ]
        if any(kw in question for kw in science_keywords):
            matched.extend([kw for kw in science_keywords if kw in question])
        
        # 語文關鍵字（擴充）
        language_keywords = [
            '寫作', '造句', '語詞', '成語', '作文', '閱讀', '字', '詞',
            '句', '段落', '文章', '理解', '文法', '標點', '修辭',
            '描寫', '故事', '比喻', '擬人', '生動'
        ]
        if any(kw in question for kw in language_keywords):
            matched.extend([kw for kw in language_keywords if kw in question])
        
        # 學習方法關鍵字（擴充）
        pedagogy_keywords = [
            '怎麼學', '如何學', '學習方法', '記憶', '技巧', '不會', 
            '專注', '複習', '準備', '筆記', '緊張', '考試', '背', 
            '時間', '安排', '讀書'
        ]
        if any(kw in question for kw in pedagogy_keywords):
            matched.extend([kw for kw in pedagogy_keywords if kw in question])
        
        # 評估關鍵字（擴充）
        assessment_keywords = [
            '對不對', '答案', '檢查', '對嗎', '正確', '錯', '評分',
            '誰是對的', '幫我看看', '有問題'
        ]
        if any(kw in question for kw in assessment_keywords):
            matched.extend([kw for kw in assessment_keywords if kw in question])
        
        # 情緒關鍵字（擴充）
        companion_keywords = [
            '心情', '難過', '開心', '謝謝', '你好', '再見', '累', 
            '困', '好笨', '不想', '罵我', '難過', '厲害', '休息'
        ]
        if any(kw in question for kw in companion_keywords):
            matched.extend([kw for kw in companion_keywords if kw in question])
        
        return list(set(matched))  # 去重
    
    def _fallback_routing(self, question: str) -> str:
        """後備路由邏輯（基於關鍵字）"""
        question_lower = question.lower()
        
        # 計分系統
        scores = {
            'math_tutor': 0,
            'science_tutor': 0,
            'language_tutor': 0,
            'pedagogy': 0,
            'assessment': 0,
            'companion': 0
        }
        
        # 數學關鍵字（權重更高）
        math_keywords = {
            '數學': 3, '計算': 3, '加': 2, '減': 2, '乘': 2, '除': 2,
            '幾何': 3, '代數': 3, '方程': 3, '分數': 3, '小數': 3,  # 分數權重提高
            '等於': 2, '多少': 1, '幾個': 1, '數字': 2, '算': 2
        }
        for keyword, weight in math_keywords.items():
            if keyword in question:
                scores['math_tutor'] += weight
        
        # 科學關鍵字（增加更多物理現象詞）
        science_keywords = {
            '科學': 3, '物理': 3, '化學': 3, '生物': 3, '實驗': 3,
            '為什麼': 2, '怎麼': 2, '原理': 3, '現象': 3,
            '光': 2, '聲音': 2, '能量': 2, '力': 2,
            '天空': 3, '藍色': 2, '月亮': 2, '太陽': 2,  # 天文現象
            '下雨': 3, '雲': 2, '風': 2, '水': 1,  # 氣象現象
            '植物': 2, '動物': 2, '細胞': 3,  # 生物
            '光合作用': 3, '呼吸': 2, '消化': 2  # 生物過程
        }
        for keyword, weight in science_keywords.items():
            if keyword in question:
                scores['science_tutor'] += weight
        
        # 語文關鍵字（強調語言本身）
        language_keywords = {
            '寫作': 3, '造句': 3, '語詞': 3, '成語': 3, 
            '作文': 3, '閱讀': 3, '字': 2, '詞': 2,
            '句': 2, '段落': 3, '文章': 3, '理解': 2,  # 閱讀理解相關
            '文法': 3, '標點': 3, '修辭': 3
        }
        for keyword, weight in language_keywords.items():
            if keyword in question:
                scores['language_tutor'] += weight
        
        # 學習方法關鍵字（需同時有方法詞）
        pedagogy_keywords = {
            '怎麼學': 3, '如何學': 3, '學習方法': 3, '記憶': 3,
            '技巧': 2, '不會': 2, '專注': 2, '複習': 2,
            '準備': 2, '筆記': 3
        }
        for keyword, weight in pedagogy_keywords.items():
            if keyword in question:
                scores['pedagogy'] += weight
        
        # 如果是"如何提升XX"的問題，優先考慮該領域
        if '提升' in question or '提高' in question or '改善' in question:
            if '閱讀' in question or '寫作' in question:
                scores['language_tutor'] += 2  # 語文學習
            elif '數學' in question or '計算' in question:
                scores['math_tutor'] += 2  # 數學學習
            else:
                scores['pedagogy'] += 1  # 一般學習方法
        
        # 評估關鍵字
        assessment_keywords = {
            '對不對': 3, '答案': 3, '檢查': 3, '對嗎': 3,
            '正確': 2, '錯': 2, '評分': 3
        }
        for keyword, weight in assessment_keywords.items():
            if keyword in question:
                scores['assessment'] += weight
        
        # 情緒/閒聊關鍵字
        companion_keywords = {
            '心情': 3, '難過': 3, '開心': 3, '謝謝': 3,
            '你好': 3, '再見': 3, '累': 2, '困': 2
        }
        for keyword, weight in companion_keywords.items():
            if keyword in question:
                scores['companion'] += weight
        
        # 特殊規則：單純的"為什麼"問題且有科學詞彙
        if '為什麼' in question and len(question) < 15:
            # 短問題如"為什麼天空是藍色"應該是科學
            if any(kw in question for kw in ['天空', '月亮', '太陽', '星星', '雨', '雪', '雲']):
                scores['science_tutor'] += 3
        
        # 返回得分最高的 Agent
        max_score = max(scores.values())
        if max_score == 0:
            return 'companion'  # 預設
        
        # 找出得分最高的 Agent
        for agent, score in scores.items():
            if score == max_score:
                return agent
        
        return 'companion'
    
    def synthesize_response(self, question: str, agent_responses: List[Dict[str, Any]]) -> str:
        """
        整合多個 Agent 的回應
        
        Args:
            question: 原始問題
            agent_responses: Agent 回應列表
            
        Returns:
            整合後的最終回應
        """
        if len(agent_responses) == 1:
            return agent_responses[0]['response']
        
        # 多個回應需要整合
        synthesis_prompt = f"""整合以下專家的回答，給學生一個清楚、完整的答案。

學生問題: {question}

專家回答:
"""
        for resp in agent_responses:
            synthesis_prompt += f"\n【{resp['agent']}】: {resp['response']}\n"
        
        synthesis_prompt += "\n請整合以上回答，用適合 5-12 歲小朋友的語言回答:"
        
        messages = [
            {
                'role': 'user',
                'content': synthesis_prompt
            }
        ]
        
        try:
            response = self.llm_client.chat(
                model=self.model_name,
                messages=messages
            )
            
            return response['message']['content']
            
        except Exception as e:
            print(f"整合錯誤: {e}")
            # 後備：直接返回第一個回應
            return agent_responses[0]['response']
