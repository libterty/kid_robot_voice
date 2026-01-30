#!/usr/bin/env python3
"""
語音對話模式
使用麥克風輸入 + 喇叭輸出
真正的語音對話體驗！
支援按空白鍵跳過、串流播放
"""

import sys
import os
import time
import threading
import subprocess
import select

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
        
        # 控制標記
        self.skip_requested = False
        self.is_speaking = False
        self.audio_process = None
        
        print("✅ 系統初始化完成！\n")
    
    def check_skip_key(self):
        """檢查是否按下空白鍵（非阻塞）"""
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == ' ':
                return True
        return False
    
    def speak_streaming(self, text: str):
        """
        串流模式說話（邊顯示邊播放）
        
        Args:
            text: 要說的文字
        """
        print("🤖 小助手: ", end='', flush=True)
        
        # 將文字分句
        sentences = self._split_into_sentences(text)
        
        # 重置跳過標記
        self.skip_requested = False
        self.is_speaking = True
        
        # 啟動背景語音監聽
        self.listen_for_skip_command()
        
        for i, sentence in enumerate(sentences):
            if self.skip_requested:
                print("\n⏭️  已跳過")
                break
            
            # 顯示文字
            print(sentence, end='', flush=True)
            
            # 同時生成並播放語音
            audio_file = self.tts.speak(sentence, play=False)
            
            if audio_file and not self.skip_requested:
                self._play_audio_with_skip(audio_file)
            
            # 短暫停頓
            if i < len(sentences) - 1 and not self.skip_requested:
                time.sleep(0.3)
        
        print()  # 換行
        self.is_speaking = False
    
    def _split_into_sentences(self, text: str) -> list:
        """將文字分割成句子"""
        import re
        
        # 按句號、問號、驚嘆號分割
        sentences = re.split(r'([。！？!?.]+)', text)
        
        # 重新組合（標點符號和前面的句子合併）
        result = []
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                result.append(sentences[i] + sentences[i+1])
            else:
                result.append(sentences[i])
        
        # 處理剩餘內容
        if len(sentences) % 2 == 1 and sentences[-1]:
            result.append(sentences[-1])
        
        return [s.strip() for s in result if s.strip()]
    
    def listen_for_skip_command(self):
        """在背景監聽「跳過」或「下一個」指令"""
        import threading
        
        def background_listen():
            while self.is_speaking:
                try:
                    # 短時間錄音檢測
                    text = self.stt.listen_from_microphone(timeout=1, phrase_time_limit=2)
                    
                    if text and any(word in text for word in ['跳過', '下一個', 'skip', 'next']):
                        print(f"\n🎤 聽到指令: {text}")
                        self.skip_requested = True
                        break
                except:
                    pass
        
        # 在背景線程中監聽
        listener_thread = threading.Thread(target=background_listen, daemon=True)
        listener_thread.start()
    
    def _play_audio_with_skip(self, audio_file: str):
        """播放音訊（可被跳過 - 支援空白鍵和語音指令）"""
        try:
            self.audio_process = subprocess.Popen(
                ['afplay', audio_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待播放完成或被跳過
            while self.audio_process.poll() is None:
                if self.skip_requested:
                    self.audio_process.terminate()
                    self.audio_process.wait()
                    break
                
                # 檢查空白鍵
                if self.check_skip_key():
                    print("\n⌨️  空白鍵")
                    self.skip_requested = True
                    self.audio_process.terminate()
                    self.audio_process.wait()
                    break
                
                time.sleep(0.05)
            
        except Exception as e:
            print(f"播放錯誤: {e}")
        finally:
            self.audio_process = None
    
    def speak(self, text: str):
        """
        普通模式說話（一次性顯示和播放）
        
        Args:
            text: 要說的文字
        """
        print(f"🤖 小助手: {text}")
        
        # 重置跳過標記
        self.skip_requested = False
        self.is_speaking = True
        
        # 生成語音
        audio_file = self.tts.speak(text, play=False)
        
        if audio_file:
            print("💡 按空白鍵可跳過")
            self._play_audio_with_skip(audio_file)
        
        self.is_speaking = False
    
    def listen(self, timeout: int = 10) -> str:
        """
        聆聽（STT）
        
        Args:
            timeout: 超時時間（秒）
            
        Returns:
            識別出的文字
        """
        # 重置跳過標記
        self.skip_requested = False
        
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
        print("🎤 語音對話模式（串流版）")
        print("=" * 70)
        
        # 顯示使用說明
        print("\n📖 使用說明:")
        print("  • 聽到「請說話」後開始提問")
        print("  • 說完後會自動識別並回答")
        print("  • 按【空白鍵】或說「跳過」「下一個」可跳過回答")
        print("  • 說「退出」或「結束」可以結束對話")
        print("  • 說「重置」可以清除對話歷史")
        print("=" * 70)
        print()
        
        # 打招呼
        self.greet()
        
        # 主對話循環
        conversation_count = 0
        
        # 設定終端為非阻塞模式（Mac/Linux）
        try:
            import termios
            import tty
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except:
            old_settings = None
        
        try:
            while True:
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
                
                # 使用串流模式播放（邊顯示邊播放）
                self.speak_streaming(response)
                
                conversation_count += 1
                
                # 每5輪對話提示一次
                if conversation_count % 5 == 0:
                    print(f"\n💡 提示: 已經聊了 {conversation_count} 輪了！")
                
        except KeyboardInterrupt:
            print("\n\n⏸️  對話中斷")
            farewell = "掰掰！"
            self.speak(farewell)
        
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 恢復終端設定
            if old_settings:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except:
                    pass
        
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
    print("🎤 家庭陪讀機器人 - 語音對話模式（串流版）")
    print("=" * 70)
    
    # 檢查是否要測試音訊
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_audio_devices()
        return
    
    print("\n⚠️  注意事項:")
    print("  1. 請確保麥克風和喇叭都正常工作")
    print("  2. 請在安靜的環境中使用")
    print("  3. 說話要清晰，不要太快")
    print("  4. 播放時可以按【空白鍵】或說「跳過」「下一個」")
    
    print("\n是否要先測試音訊裝置？")
    choice = input("輸入 'y' 測試，按 Enter 直接開始: ").strip().lower()
    
    if choice == 'y':
        if not test_audio_devices():
            print("\n❌ 音訊測試失敗，請檢查設備")
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
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()