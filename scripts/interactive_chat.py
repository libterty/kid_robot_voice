#!/usr/bin/env python3
"""
互動式一問一答
支援文字輸入或語音輸入
"""

import sys
import os

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.voice import ChatBot, TextToSpeech
from dotenv import load_dotenv

load_dotenv()


class InteractiveChat:
    """互動式對話系統"""
    
    def __init__(self, use_voice: bool = False):
        """
        初始化互動式對話
        
        Args:
            use_voice: 是否使用語音輸出（TTS）
        """
        self.bot = ChatBot()
        self.use_voice = use_voice
        
        if self.use_voice:
            self.tts = TextToSpeech()
            print("🔊 語音輸出已啟用")
        else:
            self.tts = None
            print("💬 純文字模式")
    
    def greet(self):
        """打招呼"""
        greeting = "你好！我是陪讀小助手，有什麼問題想問我嗎？"
        print(f"\n🤖 小助手: {greeting}\n")
        
        if self.use_voice:
            self.tts.speak(greeting)
    
    def ask(self, question: str) -> str:
        """
        提問並獲得回答
        
        Args:
            question: 問題內容
            
        Returns:
            AI 的回答
        """
        print(f"👦 你: {question}")
        
        # 取得 AI 回答
        response = self.bot.chat(question)
        print(f"🤖 小助手: {response}\n")
        
        # 語音輸出
        if self.use_voice:
            self.tts.speak(response)
        
        return response
    
    def run(self):
        """執行互動式對話"""
        print("\n" + "=" * 60)
        print("💬 互動式對話模式")
        print("=" * 60)
        
        # 顯示使用說明
        print("\n📖 使用說明:")
        print("  • 輸入問題後按 Enter")
        print("  • 輸入 'quit' 或 'exit' 或 '退出' 結束對話")
        print("  • 輸入 'reset' 或 '重置' 清除對話歷史")
        print("  • 輸入 'voice on' 開啟語音")
        print("  • 輸入 'voice off' 關閉語音")
        print("=" * 60)
        
        # 打招呼
        self.greet()
        
        # 主對話循環
        while True:
            try:
                # 讀取使用者輸入
                question = input("👦 你: ").strip()
                
                # 檢查結束指令
                if question.lower() in ['quit', 'exit', '退出', '結束', 'q']:
                    farewell = "再見！期待下次再聊！"
                    print(f"\n🤖 小助手: {farewell}")
                    if self.use_voice:
                        self.tts.speak(farewell)
                    break
                
                # 檢查重置指令
                if question.lower() in ['reset', '重置', 'clear']:
                    self.bot.reset_conversation()
                    print("🔄 對話已重置，我們重新開始吧！\n")
                    continue
                
                # 檢查語音控制
                if question.lower() == 'voice on':
                    if not self.tts:
                        self.tts = TextToSpeech()
                    self.use_voice = True
                    print("🔊 語音輸出已開啟\n")
                    continue
                
                if question.lower() == 'voice off':
                    self.use_voice = False
                    print("🔇 語音輸出已關閉\n")
                    continue
                
                # 空輸入
                if not question:
                    continue
                
                # 對話
                self.ask(question)
                
            except KeyboardInterrupt:
                print("\n\n👋 掰掰！")
                break
            except Exception as e:
                print(f"\n❌ 發生錯誤: {e}")


def main():
    """主函數"""
    
    print("\n🤖 家庭陪讀機器人 - 互動式對話")
    
    # 選擇模式
    print("\n請選擇模式:")
    print("1. 純文字對話（推薦，快速）")
    print("2. 文字 + 語音輸出（會朗讀回答）")
    
    try:
        choice = input("\n選擇 (1/2): ").strip()
        
        use_voice = (choice == '2')
        
        # 啟動互動式對話
        chat = InteractiveChat(use_voice=use_voice)
        chat.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 掰掰！")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
