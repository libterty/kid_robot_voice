"""
語音轉文字 (Speech-to-Text) 模組 - 改進版
使用 SpeechRecognition + Google Speech API（免費）
支援即時麥克風錄音

改進項目：
1. 增加停頓容忍度，避免中途斷句
2. 優化環境噪音處理
3. 支援更長的語音輸入
4. 所有參數可通過環境變數調整
"""

import os
from pathlib import Path
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()


class SpeechToText:
    """語音轉文字處理器 - 改進版"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language = os.getenv('STT_LANGUAGE', 'zh-TW')
        
        # === 核心參數（可通過環境變數調整）===
        
        # 能量門檻：降低以提高靈敏度，減少漏聽
        self.recognizer.energy_threshold = int(os.getenv('STT_ENERGY_THRESHOLD', '2500'))
        
        # 動態能量調整：開啟以自動適應環境噪音
        self.recognizer.dynamic_energy_threshold = os.getenv('STT_DYNAMIC_ENERGY', 'true').lower() == 'true'
        
        # 停頓容忍度：2.5秒 -> 允許思考停頓而不中斷
        self.recognizer.pause_threshold = float(os.getenv('STT_PAUSE_THRESHOLD', '2.5'))
        
        # 非語音持續時間：降低以更快響應說話開始
        self.recognizer.non_speaking_duration = float(os.getenv('STT_NON_SPEAKING_DURATION', '0.3'))
        
        # 動態能量調整參數（微調）
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        
        # 顯示當前配置
        self._log_config()
    
    def _log_config(self):
        """顯示當前 STT 配置"""
        if os.getenv('STT_SHOW_CONFIG', 'false').lower() == 'true':
            print("\n📊 STT 配置:")
            print(f"  • 能量門檻: {self.recognizer.energy_threshold}")
            print(f"  • 停頓容忍: {self.recognizer.pause_threshold} 秒")
            print(f"  • 非語音時長: {self.recognizer.non_speaking_duration} 秒")
            print(f"  • 動態調整: {self.recognizer.dynamic_energy_threshold}")
            print()
    
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
                
                # 環境噪音自動調整（縮短時間以減少等待）
                if os.getenv('STT_ADJUST_AMBIENT', 'true').lower() == 'true':
                    # print("🔇 正在調整環境噪音...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
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
    
    def listen_from_microphone_extended(self, timeout: int = 10, phrase_time_limit: int = 30) -> str:
        """
        從麥克風即時錄音並轉文字（長句模式）
        
        專門用於處理複雜、較長的問題描述
        
        Args:
            timeout: 等待開始說話的超時時間（秒）- 預設 10 秒
            phrase_time_limit: 單次錄音最長時間（秒）- 預設 30 秒
            
        Returns:
            辨識出的文字內容
        """
        try:
            with sr.Microphone() as source:
                print("🎤 請說話（長句模式）...")
                print("💡 可以慢慢說，中間可以停頓思考")
                
                # 環境噪音自動調整
                if os.getenv('STT_ADJUST_AMBIENT', 'true').lower() == 'true':
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                
                # 開始錄音（使用更長的時限）
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    print("⏱️  沒有聽到聲音，超時了")
                    return ""
                
            print("🔄 正在辨識（這可能需要一點時間）...")
            
            # 識別語音（使用 show_all 獲取更多候選）
            try:
                # 嘗試獲取最佳結果
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.language,
                    show_all=False  # 只返回最可能的結果
                )
                return text
            except sr.UnknownValueError:
                # 如果無法識別，嘗試獲取所有候選
                try:
                    results = self.recognizer.recognize_google(
                        audio, 
                        language=self.language,
                        show_all=True
                    )
                    if results and 'alternative' in results:
                        # 返回第一個候選
                        return results['alternative'][0]['transcript']
                except:
                    pass
                
                print("❌ 無法辨識，請重新說一遍")
                return ""
            
        except sr.RequestError as e:
            print(f"❌ Google Speech API 錯誤: {e}")
            return ""
        except Exception as e:
            print(f"❌ STT 錯誤: {e}")
            import traceback
            traceback.print_exc()
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
    
    def test_long_sentence(self):
        """測試長句識別能力"""
        print("\n🧪 長句識別測試")
        print("💡 請用一句話描述你的問題，可以停頓思考，最多 30 秒")
        
        result = self.listen_from_microphone_extended(timeout=10, phrase_time_limit=30)
        
        if result:
            print(f"\n✅ 識別結果:")
            print(f"   {result}")
            print(f"\n📏 長度: {len(result)} 字元")
            return True
        else:
            print("❌ 識別失敗")
            return False


if __name__ == "__main__":
    # 測試範例
    print("=" * 70)
    print("🎤 STT 模組測試（改進版）")
    print("=" * 70)
    
    stt = SpeechToText()
    print(f"\n✅ STT 模組初始化成功")
    print(f"語言設定: {stt.language}")
    
    # 選單
    print("\n請選擇測試項目:")
    print("  1. 測試麥克風")
    print("  2. 測試長句識別")
    print("  3. 兩個都測試")
    
    choice = input("\n請輸入選項 (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        stt.test_microphone()
    
    if choice in ['2', '3']:
        stt.test_long_sentence()