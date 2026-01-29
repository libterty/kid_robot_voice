#!/usr/bin/env python3
"""
完整互動示範
結合語音和視覺，模擬真實的陪讀場景
"""

import sys
import os
import time

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.voice import ChatBot, TextToSpeech
from dotenv import load_dotenv

load_dotenv()


class ReadingCompanion:
    """陪讀小助手完整示範"""
    
    def __init__(self):
        self.bot = ChatBot()
        self.tts = TextToSpeech()
        
    def greet(self):
        """打招呼"""
        greeting = "你好！我是陪讀小助手，我可以回答你的問題，陪你一起學習！"
        print(f"\n🤖: {greeting}")
        self.tts.speak(greeting)
        return greeting
    
    def answer_question(self, question: str):
        """回答問題並生成語音"""
        print(f"\n👦: {question}")
        
        # 取得 AI 回答
        response = self.bot.chat(question)
        print(f"🤖: {response}")
        
        # 生成語音
        self.tts.speak(response)
        
        return response
    
    def run_demo(self):
        """執行互動示範"""
        print("\n" + "=" * 60)
        print("🎬 陪讀小助手互動示範")
        print("=" * 60)
        
        # 打招呼
        self.greet()
        time.sleep(1)
        
        # 模擬問答場景
        demo_questions = [
            {
                "scenario": "📖 場景一：閱讀自然科學書籍",
                "question": "為什麼恐龍會滅絕？"
            },
            {
                "scenario": "📖 場景二：數學作業時間",
                "question": "什麼是乘法？"
            },
            {
                "scenario": "📖 場景三：好奇心時刻",
                "question": "為什麼月亮會跟著我走？"
            }
        ]
        
        for i, scenario in enumerate(demo_questions, 1):
            print(f"\n{'='*60}")
            print(f"{scenario['scenario']}")
            print(f"{'='*60}")
            
            self.answer_question(scenario['question'])
            
            if i < len(demo_questions):
                print("\n⏳ 等待 2 秒後繼續...")
                time.sleep(2)
        
        # 結束
        print("\n" + "=" * 60)
        print("✨ 示範完成！")
        print("=" * 60)
        print(f"\n📁 對話記錄已儲存至: {self.bot.log_dir}")
        print(f"📁 語音檔案已儲存至: {self.tts.audio_dir}")


def interactive_mode():
    """互動模式：讓使用者自己輸入問題"""
    print("\n" + "=" * 60)
    print("💬 互動模式")
    print("=" * 60)
    print("💡 提示: 輸入 'quit' 或 'exit' 離開\n")
    
    companion = ReadingCompanion()
    companion.greet()
    
    while True:
        try:
            question = input("\n👦 你的問題: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出', '結束']:
                farewell = "再見！期待下次再聊！"
                print(f"\n🤖: {farewell}")
                companion.tts.speak(farewell)
                break
            
            if not question:
                continue
            
            companion.answer_question(question)
            
        except KeyboardInterrupt:
            print("\n\n👋 掰掰！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")


def main():
    """主函數"""
    # 檢查 API Key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ 錯誤: 請先設定 GEMINI_API_KEY 環境變數")
        print("💡 提示: 複製 .env.example 為 .env 並填入你的 API Key")
        return
    
    print("\n🤖 家庭陪讀機器人 - 完整示範")
    print("\n請選擇模式:")
    print("1. 自動示範（播放預設場景）")
    print("2. 互動模式（自己輸入問題）")
    
    try:
        choice = input("\n選擇 (1/2): ").strip()
        
        if choice == '1':
            companion = ReadingCompanion()
            companion.run_demo()
        elif choice == '2':
            interactive_mode()
        else:
            print("❌ 無效的選擇")
            
    except KeyboardInterrupt:
        print("\n\n👋 掰掰！")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
