"""
輕量級整合追蹤器 (MediaPipe 0.10.32 Tasks API 版本)
使用輕量級人臉偵測器 + MediaPipe Pose Landmarker
"""

import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from dotenv import load_dotenv
from .face_detector_lite import LightweightFaceDetector
from pathlib import Path

load_dotenv()


class KidTrackerLite:
    """輕量級整合追蹤器（使用 MediaPipe Tasks API）"""
    
    def __init__(self, camera_id: int = None):
        """初始化追蹤器"""
        self.camera_id = camera_id if camera_id is not None else \
                         int(os.getenv('CAMERA_ID', '0'))
        
        # 初始化輕量級人臉偵測器
        self.face_detector = LightweightFaceDetector(camera_id=self.camera_id)
        
        # 初始化 MediaPipe Pose Landmarker（使用 tasks API）
        model_path = self._download_pose_model()
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5
        )
        self.pose_landmarker = vision.PoseLandmarker.create_from_options(options)
        
        # 追蹤狀態
        self.tracking_mode = "fusion"
        self.target_info = {
            'face_position': None,
            'body_position': None,
            'final_position': None,
            'distance': None,
            'confidence': 0,
            'name': None,
            'is_detected': False
        }
        
        self.cap = None
        
        print("✅ 使用輕量級追蹤器（MediaPipe 0.10.32 Tasks API）")
    
    def _download_pose_model(self):
        """下載 Pose Landmarker 模型"""
        model_path = Path("models/pose_landmarker.task")
        model_path.parent.mkdir(exist_ok=True)
        
        if not model_path.exists():
            print("📥 下載 Pose Landmarker 模型...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
            urllib.request.urlretrieve(url, model_path)
            print("✅ 模型下載完成")
        
        return str(model_path)
    
    def start_camera(self):
        """啟動攝像頭"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception(f"❌ 無法開啟攝像頭 {self.camera_id}")
        
        self.face_detector.cap = self.cap
        print(f"✅ 攝像頭 {self.camera_id} 已啟動")
    
    def detect_body(self, frame):
        """偵測人體骨架（使用 Pose Landmarker）"""
        # 轉換為 MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # 執行偵測
        detection_result = self.pose_landmarker.detect(mp_image)
        
        body_center = None
        distance_estimate = None
        pose_landmarks = None
        
        if detection_result.pose_landmarks:
            # 取第一個人的骨架
            landmarks = detection_result.pose_landmarks[0]
            pose_landmarks = landmarks
            
            h, w, _ = frame.shape
            
            # 計算身體中心
            # Pose landmarks 索引：0=鼻子, 23=左髖, 24=右髖
            nose = landmarks[0]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            center_x = int((nose.x + (left_hip.x + right_hip.x) / 2) / 2 * w)
            center_y = int((nose.y + (left_hip.y + right_hip.y) / 2) / 2 * h)
            body_center = (center_x, center_y)
            
            # 距離估算（基於肩寬）
            # 11=左肩, 12=右肩
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            shoulder_width_px = abs(left_shoulder.x - right_shoulder.x) * w
            
            if shoulder_width_px > 0:
                distance_estimate = (40 * 600) / shoulder_width_px
        
        return body_center, distance_estimate, pose_landmarks
    
    def fuse_positions(self, face_pos, body_pos):
        """融合人臉和身體位置"""
        if face_pos and body_pos:
            x = int(face_pos[0] * 0.7 + body_pos[0] * 0.3)
            y = int(face_pos[1] * 0.7 + body_pos[1] * 0.3)
            return (x, y)
        elif face_pos:
            return face_pos
        elif body_pos:
            return body_pos
        return None
    
    def track_target(self, frame):
        """執行完整的目標追蹤"""
        annotated_frame = frame.copy()
        h, w, _ = frame.shape
        
        # 1. 人臉辨識
        face_frame, face_detections = self.face_detector.detect_and_recognize(frame)
        
        # 2. 身體偵測
        body_center, distance, pose_landmarks = self.detect_body(frame)
        
        # 3. 找出目標
        target_face_pos = None
        target_name = None
        target_confidence = 0
        
        if self.face_detector.target_name:
            for name, confidence, (x, y, w, h) in face_detections:
                if name == self.face_detector.target_name:
                    target_face_pos = (x + w//2, y + h//2)
                    target_name = name
                    target_confidence = confidence
                    break
        
        # 4. 融合位置
        final_position = self.fuse_positions(target_face_pos, body_center)
        
        # 5. 更新狀態
        self.target_info = {
            'face_position': target_face_pos,
            'body_position': body_center,
            'final_position': final_position,
            'distance': distance,
            'confidence': target_confidence,
            'name': target_name,
            'is_detected': final_position is not None
        }
        
        # 6. 視覺化
        annotated_frame = face_frame.copy()
        
        # 繪製骨架
        if pose_landmarks:
            self._draw_pose_landmarks(annotated_frame, pose_landmarks, w, h)
        
        # 繪製身體中心
        if body_center:
            cv2.circle(annotated_frame, body_center, 8, (255, 0, 255), -1)
            cv2.putText(annotated_frame, "Body", 
                       (body_center[0] - 25, body_center[1] - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        # 繪製最終追蹤點
        if final_position:
            cv2.circle(annotated_frame, final_position, 15, (0, 255, 0), 3)
            cv2.circle(annotated_frame, final_position, 5, (0, 255, 0), -1)
            
            # 十字準星
            cv2.line(annotated_frame, 
                    (final_position[0] - 20, final_position[1]),
                    (final_position[0] + 20, final_position[1]),
                    (0, 255, 0), 2)
            cv2.line(annotated_frame, 
                    (final_position[0], final_position[1] - 20),
                    (final_position[0], final_position[1] + 20),
                    (0, 255, 0), 2)
        
        # 資訊面板
        self._draw_info_panel(annotated_frame, w, h)
        
        return annotated_frame, self.target_info
    
    def _draw_pose_landmarks(self, frame, landmarks, width, height):
        """繪製人體骨架"""
        # Pose 連接定義
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 7),  # 頭部
            (0, 4), (4, 5), (5, 6), (6, 8),  # 頭部
            (9, 10),  # 嘴巴
            (11, 12),  # 肩膀
            (11, 13), (13, 15),  # 左手臂
            (12, 14), (14, 16),  # 右手臂
            (11, 23), (12, 24),  # 軀幹
            (23, 24),  # 髖部
            (23, 25), (25, 27),  # 左腿
            (24, 26), (26, 28),  # 右腿
        ]
        
        # 繪製連線
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                
                start_point = (int(start.x * width), int(start.y * height))
                end_point = (int(end.x * width), int(end.y * height))
                
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)
        
        # 繪製關鍵點
        for landmark in landmarks:
            point = (int(landmark.x * width), int(landmark.y * height))
            cv2.circle(frame, point, 3, (0, 255, 255), -1)
    
    def _draw_info_panel(self, frame, width, height):
        """繪製資訊面板"""
        cv2.rectangle(frame, (10, 10), (400, 180), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (400, 180), (0, 255, 0), 2)
        
        y_offset = 35
        line_height = 25
        
        cv2.putText(frame, "Kid Robot Tracker (Tasks API)", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += line_height
        
        if self.target_info['is_detected']:
            status = f"Status: TRACKING ({self.tracking_mode.upper()})"
            color = (0, 255, 0)
        else:
            status = "Status: SEARCHING..."
            color = (0, 165, 255)
        
        cv2.putText(frame, status, (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        y_offset += line_height
        
        if self.target_info['name']:
            cv2.putText(frame, f"Target: {self.target_info['name']}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            target_name = self.face_detector.target_name or "None"
            cv2.putText(frame, f"Target: {target_name}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        y_offset += line_height
        
        if self.target_info['confidence'] > 0:
            cv2.putText(frame, f"Confidence: {self.target_info['confidence']:.1f}%", 
                       (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += line_height
        
        if self.target_info['distance']:
            cv2.putText(frame, f"Distance: {self.target_info['distance']:.0f} cm", 
                       (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += line_height
        
        if self.target_info['final_position']:
            pos = self.target_info['final_position']
            cv2.putText(frame, f"Position: ({pos[0]}, {pos[1]})", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def set_tracking_mode(self, mode: str):
        """設定追蹤模式"""
        if mode in ["face", "body", "fusion"]:
            self.tracking_mode = mode
            print(f"🎯 追蹤模式已設定為: {mode}")
        else:
            print(f"❌ 無效的追蹤模式: {mode}")
    
    def run_tracking(self):
        """執行即時追蹤"""
        if self.cap is None:
            self.start_camera()
        
        print("\n" + "="*60)
        print("家庭陪讀機器人 - 追蹤系統 (Tasks API)")
        print("="*60)
        print("\n按鍵說明：")
        print("  'q' - 退出")
        print("  'r' - 註冊新人臉")
        print("  't' - 設定追蹤目標")
        print("  '1' - 人臉追蹤模式")
        print("  '2' - 身體追蹤模式")
        print("  '3' - 融合追蹤模式（推薦）")
        print("  's' - 顯示狀態")
        print()
        
        if self.face_detector.target_name:
            print(f"🎯 當前追蹤目標: {self.face_detector.target_name}")
        else:
            print("⚠️ 尚未設定追蹤目標，請按 't' 設定")
        
        print(f"📊 追蹤模式: {self.tracking_mode}\n")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ 無法讀取影像")
                break
            
            tracked_frame, target_info = self.track_target(frame)
            cv2.imshow('Kid Robot - Tracker (Tasks API)', tracked_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                name = input("\n請輸入要註冊的名字: ")
                if name:
                    self.face_detector.register_face(name)
            elif key == ord('t'):
                print(f"\n已註冊的人臉: {list(self.face_detector.known_faces.keys())}")
                target = input("請輸入要追蹤的名字: ")
                if target:
                    self.face_detector.set_target(target)
            elif key == ord('1'):
                self.set_tracking_mode("face")
            elif key == ord('2'):
                self.set_tracking_mode("body")
            elif key == ord('3'):
                self.set_tracking_mode("fusion")
            elif key == ord('s'):
                self._print_status()
        
        self.stop_camera()
    
    def _print_status(self):
        """印出狀態"""
        print("\n" + "="*60)
        print("當前追蹤狀態")
        print("="*60)
        print(f"追蹤模式: {self.tracking_mode}")
        print(f"目標名稱: {self.target_info['name'] or '無'}")
        print(f"偵測狀態: {'✅ 已偵測' if self.target_info['is_detected'] else '❌ 未偵測'}")
        print(f"信心度: {self.target_info['confidence']:.1f}%")
        print(f"距離: {self.target_info['distance']:.0f} cm" if self.target_info['distance'] else "距離: N/A")
        print(f"最終位置: {self.target_info['final_position']}")
        print("="*60 + "\n")
    
    def stop_camera(self):
        """停止攝像頭"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ 攝像頭已關閉")
    
    def get_tracking_info(self):
        """取得追蹤資訊"""
        return self.target_info


if __name__ == "__main__":
    tracker = KidTrackerLite()
    tracker.run_tracking()