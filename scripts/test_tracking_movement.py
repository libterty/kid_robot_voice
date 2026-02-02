#!/usr/bin/env python3
"""
macOS 追蹤移動能力測試
測試系統追蹤人臉移動的能力
"""

import cv2
import sys
import time
import os

# 將 src 目錄加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vision import KidTrackerLite
from dotenv import load_dotenv


def test_tracking_ability():
    """測試追蹤移動能力"""
    print("\n" + "="*70)
    print("🎯 追蹤移動能力測試")
    print("="*70)
    
    print("\n📋 測試項目：")
    print("  1. 靜態追蹤測試（不移動）")
    print("  2. 水平移動追蹤測試（左右移動）")
    print("  3. 垂直移動追蹤測試（上下移動）")
    print("  4. 距離變化追蹤測試（前後移動）")
    print("  5. 綜合移動追蹤測試")
    
    # 建立追蹤器
    print("\n正在初始化追蹤器...")
    tracker = KidTrackerLite()
    
    try:
        tracker.start_camera()
        
        # 檢查是否有註冊的人臉
        if len(tracker.face_detector.known_faces) == 0:
            print("\n⚠️ 尚未註冊任何人臉")
            register = input("是否要現在註冊？(y/n): ").strip().lower()
            
            if register == 'y':
                name = input("請輸入名字: ").strip()
                if not name:
                    name = "測試用戶"
                tracker.face_detector.register_face(name, num_samples=5)
                tracker.face_detector.set_target(name)
            else:
                print("❌ 需要先註冊人臉才能進行追蹤測試")
                return False
        else:
            print(f"\n已註冊的人臉: {list(tracker.face_detector.known_faces.keys())}")
            target = input("請選擇要追蹤的目標: ").strip()
            
            if target in tracker.face_detector.known_faces:
                tracker.face_detector.set_target(target)
            else:
                print("❌ 找不到該用戶")
                return False
        
        # 設定融合追蹤模式
        tracker.set_tracking_mode("fusion")
        
        # 測試 1: 靜態追蹤
        print("\n[測試 1/5] 靜態追蹤測試")
        print("請保持不動，面對鏡頭 5 秒...")
        input("按 ENTER 開始...")
        
        static_results = run_tracking_test(
            tracker, 
            duration=5, 
            test_name="Static",
            instruction="保持不動"
        )
        
        # 測試 2: 水平移動
        print("\n[測試 2/5] 水平移動追蹤測試")
        print("請緩慢左右移動頭部 10 秒...")
        input("按 ENTER 開始...")
        
        horizontal_results = run_tracking_test(
            tracker,
            duration=10,
            test_name="Horizontal",
            instruction="左右移動"
        )
        
        # 測試 3: 垂直移動
        print("\n[測試 3/5] 垂直移動追蹤測試")
        print("請緩慢上下移動頭部 10 秒...")
        input("按 ENTER 開始...")
        
        vertical_results = run_tracking_test(
            tracker,
            duration=10,
            test_name="Vertical",
            instruction="上下移動"
        )
        
        # 測試 4: 距離變化
        print("\n[測試 4/5] 距離變化追蹤測試")
        print("請緩慢前後移動 10 秒...")
        input("按 ENTER 開始...")
        
        distance_results = run_tracking_test(
            tracker,
            duration=10,
            test_name="Distance",
            instruction="前後移動"
        )
        
        # 測試 5: 綜合移動
        print("\n[測試 5/5] 綜合移動追蹤測試")
        print("請自由移動（左右、上下、前後）15 秒...")
        input("按 ENTER 開始...")
        
        combined_results = run_tracking_test(
            tracker,
            duration=15,
            test_name="Combined",
            instruction="自由移動"
        )
        
        # 統計結果
        print("\n" + "="*70)
        print("📊 測試結果總覽")
        print("="*70)
        
        all_results = [
            ("靜態追蹤", static_results),
            ("水平移動", horizontal_results),
            ("垂直移動", vertical_results),
            ("距離變化", distance_results),
            ("綜合移動", combined_results)
        ]
        
        for test_name, results in all_results:
            print(f"\n{test_name}:")
            print(f"  追蹤成功率: {results['success_rate']:.1f}%")
            print(f"  平均信心度: {results['avg_confidence']:.1f}%")
            print(f"  平均 FPS: {results['avg_fps']:.1f}")
            print(f"  評估: {results['grade']}")
        
        # 計算總體評估
        overall_success_rate = sum(r['success_rate'] for _, r in all_results) / len(all_results)
        overall_confidence = sum(r['avg_confidence'] for _, r in all_results) / len(all_results)
        
        print(f"\n" + "="*70)
        print("🎯 總體評估")
        print("="*70)
        print(f"整體追蹤成功率: {overall_success_rate:.1f}%")
        print(f"整體平均信心度: {overall_confidence:.1f}%")
        
        if overall_success_rate >= 75 and overall_confidence >= 70:
            final_grade = "🟢 優秀 - 系統追蹤能力良好"
        elif overall_success_rate >= 60 and overall_confidence >= 60:
            final_grade = "🟡 良好 - 基本滿足需求"
        else:
            final_grade = "🔴 需改進 - 建議優化"
        
        print(f"最終評級: {final_grade}")
        
        # 給出建議
        print(f"\n💡 使用建議：")
        if overall_success_rate >= 75:
            print("  ✅ 系統運作良好，可以進行實際應用測試")
            print("  ✅ 建議在光線充足的環境下使用")
        else:
            print("  ⚠️ 建議改進：")
            print("    - 增加註冊照片數量")
            print("    - 確保環境光線充足穩定")
            print("    - 降低移動速度")
            print("    - 保持在攝像頭視野範圍內")
        
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


def run_tracking_test(tracker, duration, test_name, instruction):
    """執行單個追蹤測試"""
    print(f"\n開始 {test_name} 測試...")
    print(f"指示: {instruction}")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("開始！\n")
    
    start_time = time.time()
    frame_count = 0
    tracked_count = 0
    confidence_sum = 0
    positions = []
    
    while time.time() - start_time < duration:
        ret, frame = tracker.cap.read()
        if not ret:
            continue
        
        frame_count += 1
        
        # 執行追蹤
        tracked_frame, target_info = tracker.track_target(frame)
        
        # 記錄結果
        if target_info['is_detected']:
            tracked_count += 1
            confidence_sum += target_info['confidence']
            positions.append(target_info['final_position'])
        
        # 顯示剩餘時間
        remaining = int(duration - (time.time() - start_time))
        cv2.putText(
            tracked_frame,
            f"{test_name} Test - {remaining}s remaining",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # 顯示當前狀態
        status = "TRACKING" if target_info['is_detected'] else "LOST"
        color = (0, 255, 0) if target_info['is_detected'] else (0, 0, 255)
        cv2.putText(
            tracked_frame,
            f"Status: {status}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )
        
        cv2.imshow(f'{test_name} Tracking Test', tracked_frame)
        cv2.waitKey(1)
    
    cv2.destroyWindow(f'{test_name} Tracking Test')
    
    # 計算結果
    elapsed_time = time.time() - start_time
    success_rate = (tracked_count / frame_count * 100) if frame_count > 0 else 0
    avg_confidence = (confidence_sum / tracked_count) if tracked_count > 0 else 0
    avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
    
    # 計算移動距離（如果有追蹤到）
    movement = 0
    if len(positions) > 1:
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            movement += (dx**2 + dy**2) ** 0.5
    
    # 評級
    if success_rate >= 80 and avg_confidence >= 70:
        grade = "🟢 優秀"
    elif success_rate >= 60 and avg_confidence >= 60:
        grade = "🟡 良好"
    else:
        grade = "🔴 需改進"
    
    results = {
        'success_rate': success_rate,
        'avg_confidence': avg_confidence,
        'avg_fps': avg_fps,
        'total_frames': frame_count,
        'tracked_frames': tracked_count,
        'movement': movement,
        'grade': grade
    }
    
    # 即時顯示結果
    print(f"✅ {test_name} 測試完成")
    print(f"   追蹤成功率: {success_rate:.1f}%")
    print(f"   平均信心度: {avg_confidence:.1f}%")
    print(f"   總移動距離: {movement:.0f} 像素")
    
    return results


if __name__ == "__main__":
    print("\n🤖 家庭陪讀機器人 - 追蹤移動能力測試")
    print("Python 3.13 輕量版")
    
    success = test_tracking_ability()
    
    if success:
        print("\n✨ 追蹤測試完成！")
    else:
        print("\n⚠️ 測試未完成")
    
    sys.exit(0 if success else 1)