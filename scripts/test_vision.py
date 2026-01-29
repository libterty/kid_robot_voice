#!/usr/bin/env python3
"""
測試視覺偵測功能
測試攝像頭和人體骨架偵測
"""

import sys
import os

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vision import PersonDetector
from dotenv import load_dotenv

load_dotenv()


def main():
    """主測試函數"""
    print("\n🤖 家庭陪讀機器人 - 視覺偵測測試")
    print("=" * 50)
    print("📷 準備啟動攝像頭...")
    print("💡 提示: 按 'q' 可以退出")
    print("=" * 50)
    
    try:
        # 建立偵測器
        detector = PersonDetector()
        
        # 執行即時偵測
        detector.run_live_detection()
        
        print("\n✅ 測試完成！")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        
        if "Permission denied" in str(e) or "無法開啟攝像頭" in str(e):
            print("\n💡 可能的解決方法:")
            print("1. 檢查系統偏好設定 > 隱私權與安全性 > 相機")
            print("2. 確認 Terminal 或 Python 有攝像頭權限")
            print("3. 確認沒有其他程式正在使用攝像頭")
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
