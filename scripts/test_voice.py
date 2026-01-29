#!/usr/bin/env python3
"""
測試語音互動功能
測試 LLM 對話和 TTS 語音合成
"""

import sys
import os

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.voice import ChatBot, TextToSpeech
from dotenv import load_dotenv

load_dotenv()


def test_llm():
    """測試 LLM 對話功能"""
    print("=" * 50)
    print("🧠 測試 LLM 對話功能")
    print("=" * 50)
    
    bot = ChatBot(save_conversation=False)  # 測試時不儲存記錄
    
    test_questions = [
        "為什麼天空是藍色的？",
        "恐龍為什麼會滅絕？",
        "我可以吃一整天的糖果嗎？"
    ]
    
    for question in test_questions:
        print(f"\n👦 小孩: {question}")
        response = bot.chat(question)
        print(f"🤖 小助手: {response}")
    
    print("\n✅ LLM 測試完成！")


def test_tts():
    """測試 TTS 語音合成"""
    print("\n" + "=" * 50)
    print("🔊 測試 TTS 語音合成（使用 gTTS）")
    print("=" * 50)
    
    tts = TextToSpeech()
    
    test_texts = [
        "你好！我是陪讀小助手",
        "讓我來幫你解答這個問題",
        "太棒了！你答對了！"
    ]
    
    print(f"\n當前使用語言: {tts.language}")
    print(f"可用語言: {tts.get_available_languages()}\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"[{i}/{len(test_texts)}] 正在合成: {text}")
        audio_file = tts.speak(text)
        if audio_file:
            print(f"✅ 已儲存: {audio_file}")
    
    print("\n✅ TTS 測試完成！")
    print(f"📁 音訊檔案存放在: {tts.audio_dir}")


def test_conversation_flow():
    """測試完整對話流程"""
    print("\n" + "=" * 50)
    print("💬 測試完整對話流程（LLM + TTS）")
    print("=" * 50)
    
    bot = ChatBot(save_conversation=False)
    tts = TextToSpeech()
    
    question = "什麼是光合作用？"
    
    print(f"\n👦 小孩問: {question}")
    
    # LLM 生成回答
    response = bot.chat(question)
    print(f"🤖 小助手回答: {response}")
    
    # 將回答轉成語音
    print("\n🔊 正在生成語音...")
    audio_file = tts.speak(response)
    
    if audio_file:
        print(f"✅ 完整流程測試成功！")
        print(f"📁 語音檔案: {audio_file}")
    
    print("\n💡 提示: 你可以用 QuickTime Player 或其他播放器播放音訊")


def main():
    """主測試函數"""
    print("\n🤖 家庭陪讀機器人 - 語音互動測試")
    print("=" * 50)
    
    # 檢查 API Key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ 錯誤: 請先設定 GEMINI_API_KEY 環境變數")
        print("💡 提示: 複製 .env.example 為 .env 並填入你的 API Key")
        return
    
    try:
        # 測試 1: LLM 對話
        test_llm()
        
        # 測試 2: TTS 語音合成
        test_tts()
        
        # 測試 3: 完整流程
        test_conversation_flow()
        
        print("\n" + "=" * 50)
        print("✨ 所有測試完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
