"""
人體偵測模組
使用 MediaPipe 進行即時人體骨架偵測
"""

import os
import cv2
import mediapipe as mp
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class PersonDetector:
    """人體偵測與追蹤器"""
    
    def __init__(self, camera_id: int = None):
        """
        初始化人體偵測器
        
        Args:
            camera_id: 攝像頭 ID（預設從環境變數讀取）
        """
        self.camera_id = camera_id if camera_id is not None else \
                         int(os.getenv('CAMERA_ID', '0'))
        self.confidence = float(os.getenv('DETECTION_CONFIDENCE', '0.5'))
        
        # 初始化 MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=self.confidence,
            min_tracking_confidence=self.confidence
        )
        
        # 攝像頭
        self.cap = None
        
    def start_camera(self):
        """啟動攝像頭"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception(f"❌ 無法開啟攝像頭 {self.camera_id}")
        print(f"✅ 攝像頭 {self.camera_id} 已啟動")
    
    def detect_person(self, frame):
        """
        在單幀影像中偵測人體
        
        Args:
            frame: OpenCV 影像幀
            
        Returns:
            (frame_with_skeleton, person_center, distance_estimate)
            - frame_with_skeleton: 繪製骨架後的影像
            - person_center: 人體中心座標 (x, y) 或 None
            - distance_estimate: 估計距離（基於肩寬）
        """
        # 轉換顏色空間
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        person_center = None
        distance_estimate = None
        
        if results.pose_landmarks:
            # 繪製骨架
            self.mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
            
            # 計算人體中心（使用鼻子和髖部中點）
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape
            
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            center_x = int((nose.x + (left_hip.x + right_hip.x) / 2) / 2 * w)
            center_y = int((nose.y + (left_hip.y + right_hip.y) / 2) / 2 * h)
            person_center = (center_x, center_y)
            
            # 簡易距離估算（基於肩寬）
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            shoulder_width_px = abs(left_shoulder.x - right_shoulder.x) * w
            
            # 假設實際肩寬約 40cm，焦距約 600px
            # 距離 ≈ (實際尺寸 × 焦距) / 像素尺寸
            if shoulder_width_px > 0:
                distance_estimate = (40 * 600) / shoulder_width_px
            
            # 繪製中心點
            cv2.circle(frame, person_center, 10, (0, 255, 0), -1)
            
            # 顯示距離資訊
            if distance_estimate:
                cv2.putText(
                    frame,
                    f"Distance: {distance_estimate:.0f}cm",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
        
        return frame, person_center, distance_estimate
    
    def run_live_detection(self):
        """執行即時偵測（按 'q' 退出）"""
        if self.cap is None:
            self.start_camera()
        
        print("🎥 即時偵測啟動！按 'q' 退出")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ 無法讀取影像")
                break
            
            # 偵測人體
            frame, center, distance = self.detect_person(frame)
            
            # 顯示影像
            cv2.imshow('Kid Robot - Person Detection', frame)
            
            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.stop_camera()
    
    def stop_camera(self):
        """停止攝像頭"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ 攝像頭已關閉")


if __name__ == "__main__":
    # 測試範例
    detector = PersonDetector()
    detector.run_live_detection()
