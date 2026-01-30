"""
文字轉語音 (Text-to-Speech) 模組 - 優化語速版
使用 gTTS 生成語音，並透過 pydub 進行速度處理
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

class TextToSpeech:
    """文字轉語音處理器"""
    
    def __init__(self):
        self.language = os.getenv('TTS_LANGUAGE', 'zh-TW')
        # 語速倍率，1.0 是原速，建議設定為 1.2 或 1.3
        self.speed_factor = float(os.getenv('TTS_SPEED', '1.25'))
        
        self.audio_dir = Path(os.getenv('DATA_DIR', './data')) / 'audio'
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
    def speak(self, text: str, output_file: str = None, play: bool = False) -> str:
        """將文字轉換為語音並調整語速"""
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.audio_dir / f"tts_{timestamp}.mp3"
            else:
                output_file = Path(output_file)
            
            # 1. 先生成原始語音檔
            temp_file = self.audio_dir / "temp_tts_raw.mp3"
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.save(str(temp_file))
            
            # 2. 如果語速不是 1.0，則進行處理
            if self.speed_factor != 1.0:
                audio = AudioSegment.from_file(str(temp_file))
                # 調整速度而不改變音調 (使用 speedup)
                # chunk_size 與 crossfade 能減少加速後的爆音感
                fast_audio = audio.speedup(playback_speed=self.speed_factor, chunk_size=150, crossfade=25)
                fast_audio.export(str(output_file), format="mp3")
                
                if temp_file.exists():
                    temp_file.unlink() # 刪除暫存原速檔
            else:
                os.rename(temp_file, output_file)
            
            if play:
                self.play_audio(str(output_file))
            
            return str(output_file)
            
        except Exception as e:
            print(f"❌ TTS 錯誤: {e}")
            return ""
    
    def play_audio(self, audio_file: str):
        """播放音訊檔案 (Mac)"""
        try:
            # 使用 afplay 播放
            subprocess.run(['afplay', audio_file], check=True)
        except Exception as e:
            print(f"❌ 播放失敗: {e}")

if __name__ == "__main__":
    tts = TextToSpeech()
    print(f"🚀 當前設定語速: {tts.speed_factor}x")
    tts.speak("你好！我是陪讀小助手，現在我的講話速度已經加快了，聽起來應該比較自然一點吧？", play=True)