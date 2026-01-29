"""
文字轉語音 (Text-to-Speech) 模組
使用 gTTS (Google Text-to-Speech) - 完全免費
支援自動播放
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()


class TextToSpeech:
    """文字轉語音處理器"""
    
    def __init__(self):
        self.language = os.getenv('TTS_LANGUAGE', 'zh-TW')
        self.slow = os.getenv('TTS_SLOW', 'false').lower() == 'true'
        
        # 音訊檔案存放目錄
        self.audio_dir = Path(os.getenv('DATA_DIR', './data')) / 'audio'
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
    def speak(self, text: str, output_file: str = None, play: bool = False) -> str:
        """
        將文字轉換為語音
        
        Args:
            text: 要轉換的文字
            output_file: 輸出檔案路徑（可選，預設自動生成）
            play: 是否立即播放音訊
            
        Returns:
            生成的音訊檔案路徑
        """
        try:
            # 如果沒指定檔名，自動生成
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.audio_dir / f"tts_{timestamp}.mp3"
            else:
                output_file = Path(output_file)
            
            # 使用 gTTS 生成語音
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(str(output_file))
            
            # 播放音訊
            if play:
                self.play_audio(str(output_file))
            
            return str(output_file)
            
        except Exception as e:
            print(f"❌ TTS 錯誤: {e}")
            return ""
    
    def play_audio(self, audio_file: str):
        """
        播放音訊檔案
        
        Args:
            audio_file: 音訊檔案路徑
        """
        try:
            # Mac 使用 afplay 命令播放（內建）
            subprocess.run(['afplay', audio_file], check=True)
        except FileNotFoundError:
            print("⚠️  找不到 afplay 命令，嘗試其他播放器...")
            try:
                # 備用：使用 open 命令
                subprocess.run(['open', audio_file], check=True)
            except Exception as e:
                print(f"❌ 播放失敗: {e}")
        except Exception as e:
            print(f"❌ 播放錯誤: {e}")
    
    def get_available_languages(self) -> dict:
        """取得可用的語言選項"""
        return {
            'zh-TW': '繁體中文（台灣）',
            'zh-CN': '簡體中文',
            'en': '英語',
            'ja': '日語',
            'ko': '韓語'
        }


if __name__ == "__main__":
    # 測試範例
    tts = TextToSpeech()
    print(f"當前使用語言: {tts.language}")
    print(f"可用語言: {tts.get_available_languages()}")
    
    # 測試生成並播放語音
    print("\n測試語音播放...")
    audio_file = tts.speak("你好！我是陪讀小助手，很高興認識你！", play=True)
    print(f"測試音訊檔案: {audio_file}")

