#!/usr/bin/env python3
"""
macOS 人臉辨識能力測試
快速驗證系統是否正常運作
"""

import sys
import os
import cv2

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vision import KidTrackerLite
from dotenv import load_dotenv

load_dotenv()

def test_face_recognition():
    """測試人臉辨識功能"""
    print("\n" + "="*70)
    print("🎯 人臉辨識能力測試")
    print("="*70)
    
    print("\n📋 測試項目：")
    print("  1. 攝像頭啟動測試")
    print("  2. 人臉偵測測試")
    print("  3. 人臉註冊測試")
    print("  4. 人臉辨識測試")
    print("  5. 辨識準確度評估")
    
    # 建立追蹤器
    print("\n正在初始化追蹤器...")
    tracker = KidTrackerLite()
    
    try:
        # 測試 1: 啟動攝像頭
        print("\n[測試 1/5] 攝像頭啟動測試...")
        tracker.start_camera()
        
        ret, frame = tracker.cap.read()
        if ret:
            h, w, _ = frame.shape
            print(f"✅ 攝像頭正常運作 (解析度: {w}x{h})")
        else:
            print("❌ 無法讀取影像")
            return False
        
        # 測試 2: 人臉偵測
        print("\n[測試 2/5] 人臉偵測測試...")
        print("請對著鏡頭，按 ENTER 開始偵測...")
        input()
        
        detection_count = 0
        for i in range(10):
            ret, frame = tracker.cap.read()
            if not ret:
                continue
            
            faces = tracker.face_detector.detect_faces(frame)
            if len(faces) > 0:
                detection_count += 1
            
            # 顯示偵測結果
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.putText(frame, f"Test {i+1}/10 - Faces: {len(faces)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Face Detection Test', frame)
            cv2.waitKey(100)
        
        cv2.destroyWindow('Face Detection Test')
        
        detection_rate = (detection_count / 10) * 100
        print(f"✅ 偵測成功率: {detection_rate:.0f}% ({detection_count}/10)")
        
        if detection_rate < 50:
            print("⚠️ 偵測率較低，請確保：")
            print("   - 光線充足")
            print("   - 正面對鏡頭")
            print("   - 距離適中（50-200cm）")
        
        # 測試 3: 人臉註冊
        print("\n[測試 3/5] 人臉註冊測試...")
        print("即將註冊測試用戶...")
        
        register = input("是否要註冊新人臉？(y/n): ").strip().lower()
        if register == 'y':
            name = input("請輸入名字（按 Enter 使用 '測試用戶'）: ").strip()
            if not name:
                name = "測試用戶"
            
            print(f"\n開始註冊 '{name}'")
            print("提示：按 SPACE 拍照，拍攝 5 張不同角度的照片")
            
            tracker.face_detector.register_face(name, num_samples=5)
            print(f"✅ '{name}' 註冊完成")
        else:
            print("⏭️ 跳過註冊測試")
            name = None
        
        # 測試 4 & 5: 人臉辨識和準確度
        if name:
            print("\n[測試 4/5] 人臉辨識測試...")
            print(f"設定追蹤目標為 '{name}'")
            tracker.face_detector.set_target(name)
            
            print("\n[測試 5/5] 辨識準確度評估...")
            print("請對著鏡頭保持不同姿勢，測試 30 幀...")
            print("按 ENTER 開始測試...")
            input()
            
            recognized_count = 0
            confidence_sum = 0
            total_frames = 30
            
            for i in range(total_frames):
                ret, frame = tracker.cap.read()
                if not ret:
                    continue
                
                annotated_frame, detections = tracker.face_detector.detect_and_recognize(frame)
                
                # 檢查是否辨識到目標
                for detected_name, confidence, bbox in detections:
                    if detected_name == name:
                        recognized_count += 1
                        confidence_sum += confidence
                
                # 顯示進度
                cv2.putText(annotated_frame, f"Recognition Test: {i+1}/{total_frames}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Recognition Accuracy Test', annotated_frame)
                cv2.waitKey(100)
            
            cv2.destroyWindow('Recognition Accuracy Test')
            
            recognition_rate = (recognized_count / total_frames) * 100
            avg_confidence = confidence_sum / recognized_count if recognized_count > 0 else 0
            
            print(f"\n📊 測試結果：")
            print(f"  辨識成功率: {recognition_rate:.1f}% ({recognized_count}/{total_frames})")
            print(f"  平均信心度: {avg_confidence:.1f}%")
            
            # 評估等級
            if recognition_rate >= 80 and avg_confidence >= 75:
                grade = "🟢 優秀"
            elif recognition_rate >= 60 and avg_confidence >= 65:
                grade = "🟡 良好"
            else:
                grade = "🔴 需改進"
            
            print(f"  綜合評估: {grade}")
            
            if recognition_rate < 60:
                print("\n💡 改進建議：")
                print("  - 增加註冊照片數量（10-15 張）")
                print("  - 確保光線充足且穩定")
                print("  - 多角度拍攝（正面、左側、右側）")
                print("  - 保持適當距離（80-150cm）")
        else:
            print("\n⏭️ 未註冊人臉，跳過辨識測試")
        
        print("\n" + "="*70)
        print("✅ 人臉辨識能力測試完成！")
        print("="*70)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n❌ 測試已中斷")
        return False
    except Exception as e:
        print(f"\n❌ 測試發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        tracker.stop_camera()


if __name__ == "__main__":
    print("\n🤖 家庭陪讀機器人 - macOS 測試程式")
    print("Python 3.13 輕量版")
    
    success = test_face_recognition()
    
    if success:
        print("\n✨ 系統運作正常，可以進行下一步測試！")
    else:
        print("\n⚠️ 測試未完成，請檢查錯誤訊息")
    
    sys.exit(0 if success else 1)