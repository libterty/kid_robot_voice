#!/usr/bin/env python3
"""
語音對話模式
使用麥克風輸入 + 喇叭輸出
真正的語音對話體驗！
"""

import sys
import os
import time

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.voice import ChatBot, TextToSpeech, SpeechToText
from dotenv import load_dotenv

load_dotenv()


class VoiceChat:
    """語音對話系統"""
    
    def __init__(self):
        """初始化語音對話系統"""
        print("\n🔧 正在初始化系統...")
        
        # 初始化各個模組
        self.bot = ChatBot()
        self.tts = TextToSpeech()
        self.stt = SpeechToText()
        
        print("✅ 系統初始化完成！\n")
    
    def speak(self, text: str):
        """
        說話（TTS + 播放）
        
        Args:
            text: 要說的文字
        """
        print(f"🤖 小助手: {text}")
        
        # 生成並播放語音
        audio_file = self.tts.speak(text, play=True)
    
    def listen(self, timeout: int = 10) -> str:
        """
        聆聽（STT）
        
        Args:
            timeout: 超時時間（秒）
            
        Returns:
            識別出的文字
        """
        # 從麥克風錄音並轉文字
        text = self.stt.listen_from_microphone(
            timeout=timeout,
            phrase_time_limit=15
        )
        
        if text:
            print(f"👦 你說: {text}")
        
        return text
    
    def greet(self):
        """打招呼"""
        greeting = "你好！我是陪讀小助手。你可以直接用說的問我問題喔！"
        self.speak(greeting)
    
    def run(self):
        """執行語音對話主循環"""
        print("=" * 70)
        print("🎤 語音對話模式")
        print("=" * 70)
        
        # 顯示使用說明
        print("\n📖 使用說明:")
        print("  • 聽到「請說話」後開始提問")
        print("  • 說完後會自動識別並回答")
        print("  • 按 Ctrl+C 可以隨時結束")
        print("  • 說「退出」或「結束」可以結束對話")
        print("  • 說「重置」可以清除對話歷史")
        print("=" * 70)
        print()
        
        # 打招呼
        self.greet()
        
        # 主對話循環
        conversation_count = 0
        
        while True:
            try:
                print("\n" + "-" * 70)
                
                # 聆聽使用者輸入
                user_input = self.listen(timeout=30)
                
                # 檢查是否有輸入
                if not user_input:
                    print("⏱️  沒有聽到聲音，請再試一次")
                    time.sleep(1)
                    continue
                
                # 檢查結束指令
                if any(word in user_input for word in ['退出', '結束', '再見', 'bye', 'quit', 'exit']):
                    farewell = "再見！期待下次再聊！"
                    self.speak(farewell)
                    break
                
                # 檢查重置指令
                if '重置' in user_input or 'reset' in user_input.lower():
                    self.bot.reset_conversation()
                    response = "好的，我們重新開始吧！"
                    self.speak(response)
                    continue
                
                # 對話
                print("🤔 正在思考...")
                response = self.bot.chat(user_input)
                
                print()
                self.speak(response)
                
                conversation_count += 1
                
                # 每5輪對話提示一次
                if conversation_count % 5 == 0:
                    print(f"\n💡 提示: 已經聊了 {conversation_count} 輪了！隨時可以說「退出」結束對話")
                
            except KeyboardInterrupt:
                print("\n\n⏸️  對話中斷")
                farewell = "掰掰！"
                self.speak(farewell)
                break
            
            except Exception as e:
                print(f"\n❌ 發生錯誤: {e}")
                print("💡 請再試一次...")
                time.sleep(1)
        
        # 顯示統計
        print(f"\n📊 本次對話統計:")
        print(f"  • 對話輪數: {conversation_count}")
        print(f"  • 使用後端: {self.bot.backend}")
        print(f"  • 使用模型: {self.bot.model_name}")


def test_audio_devices():
    """測試音訊裝置"""
    print("\n🔍 檢測音訊裝置...")
    
    try:
        stt = SpeechToText()
        return stt.test_microphone()
    except Exception as e:
        print(f"❌ 音訊裝置檢測失敗: {e}")
        return False


def main():
    """主函數"""
    
    print("\n" + "=" * 70)
    print("🎤 家庭陪讀機器人 - 語音對話模式")
    print("=" * 70)
    
    # 檢查是否要測試音訊
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_audio_devices()
        return
    
    print("\n⚠️  注意事項:")
    print("  1. 請確保麥克風和喇叭都正常工作")
    print("  2. 請在安靜的環境中使用")
    print("  3. 說話要清晰，不要太快")
    print("  4. Mac 可能會詢問麥克風權限，請允許")
    
    print("\n是否要先測試音訊裝置？")
    choice = input("輸入 'y' 測試，按 Enter 直接開始: ").strip().lower()
    
    if choice == 'y':
        if not test_audio_devices():
            print("\n❌ 音訊測試失敗，請檢查設備")
            print("💡 提示:")
            print("  • 確認麥克風已連接")
            print("  • 檢查系統偏好設定 > 隱私權 > 麥克風")
            print("  • 確認 Terminal 有麥克風權限")
            return
        
        print("\n✅ 音訊測試通過！")
        input("按 Enter 開始語音對話...")
    
    try:
        # 啟動語音對話
        chat = VoiceChat()
        chat.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 掰掰！")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        print("\n💡 可能的原因:")
        print("  1. 麥克風權限未授予")
        print("  2. PyAudio 未正確安裝")
        print("  3. 音訊裝置不可用")
        print("\n解決方法:")
        print("  brew install portaudio")
        print("  pip install pyaudio")
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
