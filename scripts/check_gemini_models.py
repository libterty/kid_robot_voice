#!/usr/bin/env python3
"""
檢查可用的 Gemini 模型（使用新版 SDK）
"""

import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()


def list_available_models():
    """列出所有可用的 Gemini 模型"""
    
    # 檢查 API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ 錯誤: 請先設定 GEMINI_API_KEY 環境變數")
        print("💡 提示: 編輯 .env 檔案並填入你的 API Key")
        return
    
    try:
        # 初始化客戶端
        client = genai.Client(api_key=api_key)
        
        print("\n🔍 正在查詢你的帳號可用的 Gemini 模型...\n")
        print("=" * 80)
        
        # 列出所有模型
        models = client.models.list()
        
        chat_models = []
        
        for model in models:
            # 只顯示支援對話的模型
            if 'generateContent' in model.supported_generation_methods:
                chat_models.append(model)
        
        if not chat_models:
            print("❌ 找不到任何可用的對話模型")
            print("💡 請檢查你的 API Key 是否正確")
            return
        
        # 顯示支援對話的模型
        print("✅ 你的帳號可用的對話模型:")
        print("=" * 80)
        
        for i, model in enumerate(chat_models, 1):
            # 提取模型名稱（移除 'models/' 前綴）
            model_name = model.name.replace('models/', '')
            
            print(f"\n{i}. {model_name}")
            print(f"   顯示名稱: {model.display_name}")
            
            # 顯示推薦度
            if 'flash' in model_name.lower():
                print(f"   推薦: ⚡ 速度快，適合測試")
            elif 'pro' in model_name.lower():
                print(f"   推薦: 🎯 能力強，適合複雜對話")
            
            if hasattr(model, 'input_token_limit'):
                print(f"   輸入限制: {model.input_token_limit:,} tokens")
        
        print("\n" + "=" * 80)
        print("💡 如何使用:")
        print("=" * 80)
        print("編輯 .env 檔案，設定 GEMINI_MODEL 為上面任一模型名稱")
        if chat_models:
            print(f"例如: GEMINI_MODEL={chat_models[0].name.replace('models/', '')}")
        print("\n或者直接執行測試，程式會自動選擇第一個可用的模型！")
        
        print("\n" + "=" * 80)
        
        return chat_models
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        print("\n💡 可能的原因:")
        print("1. API Key 無效或過期")
        print("2. 網路連線問題")
        print("3. 需要更新套件: pip install --upgrade google-genai")
        
        import traceback
        traceback.print_exc()
        return None


def test_auto_selection():
    """測試自動模型選擇功能"""
    
    print("\n🧪 測試自動模型選擇功能")
    print("=" * 80)
    
    try:
        # 匯入 ChatBot
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from src.voice import ChatBot
        
        print("正在初始化 ChatBot...")
        bot = ChatBot(save_conversation=False)
        
        print(f"\n✅ 自動選擇的模型: {bot.model_name}")
        
        # 測試對話
        print("\n測試對話...")
        response = bot.chat("你好！請用一句話介紹你自己。")
        print(f"🤖: {response}")
        
        print("\n" + "=" * 80)
        print("✨ 自動選擇功能測試成功！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函數"""
    
    print("\n🤖 Gemini 模型檢查工具（新版 SDK）")
    print("=" * 80)
    
    # 列出所有可用模型
    models = list_available_models()
    
    if models:
        # 測試自動選擇
        print("\n")
        test_auto_selection()


if __name__ == "__main__":
    main()
