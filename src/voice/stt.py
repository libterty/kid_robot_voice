"""
語音轉文字 (Speech-to-Text) 模組
使用 SpeechRecognition + Google Speech API（免費）
支援即時麥克風錄音
"""

import os
from pathlib import Path
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()


class SpeechToText:
    """語音轉文字處理器"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language = os.getenv('STT_LANGUAGE', 'zh-TW')
        
        # 調整識別靈敏度
        self.recognizer.energy_threshold = 4000  # 提高門檻，減少背景噪音
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # 停頓 1 秒視為結束
        
    def transcribe(self, audio_file_path: str) -> str:
        """
        將音訊檔案轉換為文字
        
        Args:
            audio_file_path: 音訊檔案路徑 (支援 wav, aiff, flac)
            
        Returns:
            辨識出的文字內容
        """
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                
            # 使用 Google Speech Recognition（免費）
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
            
        except sr.UnknownValueError:
            print("❌ 無法辨識音訊內容")
            return ""
        except sr.RequestError as e:
            print(f"❌ Google Speech API 錯誤: {e}")
            return ""
        except Exception as e:
            print(f"❌ STT 錯誤: {e}")
            return ""
    
    def listen_from_microphone(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """
        從麥克風即時錄音並轉文字
        
        Args:
            timeout: 等待開始說話的超時時間（秒）
            phrase_time_limit: 單次錄音最長時間（秒）
            
        Returns:
            辨識出的文字內容
        """
        try:
            with sr.Microphone() as source:
                print("🎤 請說話...")
                
                # 調整環境噪音
                # print("🔇 正在調整環境噪音...")
                # self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # 開始錄音
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    print("⏱️  沒有聽到聲音，超時了")
                    return ""
                
            print("🔄 正在辨識...")
            
            # 識別語音
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
            
        except sr.UnknownValueError:
            print("❌ 無法辨識，請說清楚一點")
            return ""
        except sr.RequestError as e:
            print(f"❌ Google Speech API 錯誤: {e}")
            return ""
        except Exception as e:
            print(f"❌ STT 錯誤: {e}")
            return ""
    
    def test_microphone(self):
        """測試麥克風是否正常"""
        try:
            print("\n🎤 測試麥克風...")
            print("📋 可用的麥克風:")
            
            mic_list = sr.Microphone.list_microphone_names()
            for i, name in enumerate(mic_list):
                print(f"  {i}: {name}")
            
            print(f"\n✅ 找到 {len(mic_list)} 個音訊裝置")
            
            # 測試錄音
            print("\n🧪 測試錄音 (請說「測試」)...")
            result = self.listen_from_microphone(timeout=5, phrase_time_limit=3)
            
            if result:
                print(f"✅ 識別成功: {result}")
                return True
            else:
                print("❌ 識別失敗")
                return False
                
        except Exception as e:
            print(f"❌ 麥克風測試失敗: {e}")
            return False


if __name__ == "__main__":
    # 測試範例
    stt = SpeechToText()
    print("✅ STT 模組初始化成功")
    print(f"語言設定: {stt.language}")
    
    # 測試麥克風
    stt.test_microphone()

