"""
輕量級人臉偵測模組 (MediaPipe 0.10.32 tasks API 版本)
使用 MediaPipe Tasks 進行人臉偵測與簡單辨識
不依賴 face_recognition 套件
"""

import os
import cv2
import numpy as np
import pickle
from pathlib import Path
from dotenv import load_dotenv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

load_dotenv()


class LightweightFaceDetector:
    """輕量級人臉偵測與辨識器（使用 MediaPipe Tasks API）"""
    
    def __init__(self, camera_id: int = None, database_path: str = "face_database"):
        """
        初始化人臉偵測器
        
        Args:
            camera_id: 攝像頭 ID
            database_path: 人臉資料庫儲存路徑
        """
        self.camera_id = camera_id if camera_id is not None else \
                         int(os.getenv('CAMERA_ID', '0'))
        
        # 初始化 MediaPipe Face Detector（使用 tasks API）
        base_options = python.BaseOptions(
            model_asset_path=self._download_face_detector_model()
        )
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=0.5
        )
        self.face_detector = vision.FaceDetector.create_from_options(options)
        
        # 初始化 Face Landmarker（用於特徵提取）
        landmarker_options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=self._download_face_landmarker_model()
            ),
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(landmarker_options)
        
        # 人臉資料庫
        self.database_path = Path(database_path)
        self.database_path.mkdir(exist_ok=True)
        self.known_faces = {}
        self.load_database()
        
        # 攝像頭
        self.cap = None
        
        # 追蹤狀態
        self.target_name = None
        self.last_seen_position = None
        
        print("✅ 使用輕量級人臉偵測器（MediaPipe 0.10.32 Tasks API）")
    
    def _download_face_detector_model(self):
        """下載 Face Detector 模型"""
        model_path = Path("models/face_detector.tflite")
        model_path.parent.mkdir(exist_ok=True)
        
        if not model_path.exists():
            print("📥 下載 Face Detector 模型...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
            urllib.request.urlretrieve(url, model_path)
            print("✅ 模型下載完成")
        
        return str(model_path)
    
    def _download_face_landmarker_model(self):
        """下載 Face Landmarker 模型"""
        model_path = Path("models/face_landmarker.task")
        model_path.parent.mkdir(exist_ok=True)
        
        if not model_path.exists():
            print("📥 下載 Face Landmarker 模型...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            print("✅ 模型下載完成")
        
        return str(model_path)
    
    def load_database(self):
        """載入已註冊的人臉資料"""
        db_file = self.database_path / "faces_tasks.pkl"
        if db_file.exists():
            with open(db_file, 'rb') as f:
                self.known_faces = pickle.load(f)
            print(f"✅ 已載入 {len(self.known_faces)} 個人臉資料")
        else:
            print("ℹ️ 人臉資料庫為空，請先註冊人臉")
    
    def save_database(self):
        """儲存人臉資料庫"""
        db_file = self.database_path / "faces_tasks.pkl"
        with open(db_file, 'wb') as f:
            pickle.dump(self.known_faces, f)
        print(f"✅ 人臉資料庫已儲存（共 {len(self.known_faces)} 人）")
    
    def start_camera(self):
        """啟動攝像頭"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception(f"❌ 無法開啟攝像頭 {self.camera_id}")
        print(f"✅ 攝像頭 {self.camera_id} 已啟動")
    
    def detect_faces(self, frame):
        """
        使用 MediaPipe Tasks 偵測人臉位置
        
        Args:
            frame: OpenCV 影像幀
            
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
        """
        # 轉換為 MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # 執行偵測
        detection_result = self.face_detector.detect(mp_image)
        
        faces = []
        if detection_result.detections:
            h, w, _ = frame.shape
            for detection in detection_result.detections:
                bbox = detection.bounding_box
                x = int(bbox.origin_x)
                y = int(bbox.origin_y)
                width = int(bbox.width)
                height = int(bbox.height)
                
                # 確保座標在有效範圍內
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                faces.append((x, y, width, height))
        
        return faces
    
    def extract_face_features(self, frame, bbox):
        """
        提取人臉特徵向量（使用 Face Landmarker）
        
        Args:
            frame: 原始影像
            bbox: (x, y, w, h) 人臉邊界框
            
        Returns:
            特徵向量 (numpy array) 或 None
        """
        x, y, w, h = bbox
        
        # 擴展邊界框
        padding = int(w * 0.2)
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(frame.shape[1], x + w + padding)
        y2 = min(frame.shape[0], y + h + padding)
        
        # 裁切人臉區域
        face_roi = frame[y1:y2, x1:x2]
        
        if face_roi.size == 0:
            return None
        
        # 轉換為 MediaPipe Image
        rgb_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_face)
        
        # 使用 Face Landmarker 提取特徵點
        landmarker_result = self.face_landmarker.detect(mp_image)
        
        if landmarker_result.face_landmarks:
            # 取第一個臉部的特徵點
            face_landmarks = landmarker_result.face_landmarks[0]
            
            # 提取關鍵特徵點座標（眼睛、鼻子、嘴巴）
            key_indices = [
                # 左眼
                33, 133, 160, 159, 158, 157, 173,
                # 右眼
                263, 362, 387, 386, 385, 384, 398,
                # 鼻子
                1, 2, 98, 327,
                # 嘴巴
                61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
                # 臉部輪廓
                10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
                234, 127, 162, 21, 54, 103, 67, 109
            ]
            
            features = []
            for idx in key_indices:
                if idx < len(face_landmarks):
                    landmark = face_landmarks[idx]
                    features.extend([landmark.x, landmark.y, landmark.z])
            
            return np.array(features)
        
        # 如果 Face Landmarker 失敗，使用顏色直方圖
        return self._extract_color_histogram(face_roi)
    
    def _extract_color_histogram(self, face_roi):
        """提取顏色直方圖作為後備特徵"""
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        
        hist_h = cv2.calcHist([hsv], [0], None, [50], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [60], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [60], [0, 256])
        
        cv2.normalize(hist_h, hist_h)
        cv2.normalize(hist_s, hist_s)
        cv2.normalize(hist_v, hist_v)
        
        features = np.concatenate([hist_h.flatten(), hist_s.flatten(), hist_v.flatten()])
        return features
    
    def compare_faces(self, feature1, feature2):
        """
        比較兩個特徵向量的相似度
        
        Returns:
            相似度分數 (0-100, 越高越相似)
        """
        if feature1 is None or feature2 is None:
            return 0
        
        if len(feature1) != len(feature2):
            return 0
        
        # 使用餘弦相似度
        dot_product = np.dot(feature1, feature2)
        norm1 = np.linalg.norm(feature1)
        norm2 = np.linalg.norm(feature2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        similarity = dot_product / (norm1 * norm2)
        return max(0, min(100, (similarity + 1) * 50))
    
    def recognize_face(self, frame, face_location):
        """
        辨識人臉
        
        Args:
            frame: OpenCV 影像幀
            face_location: (x, y, w, h) 人臉位置
            
        Returns:
            (name, confidence) 或 (None, 0)
        """
        if len(self.known_faces) == 0:
            return None, 0
        
        current_features = self.extract_face_features(frame, face_location)
        
        if current_features is None:
            return None, 0
        
        best_match_name = None
        best_similarity = 0
        
        for name, data in self.known_faces.items():
            for stored_features in data['features']:
                similarity = self.compare_faces(current_features, stored_features)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_name = name
        
        threshold = 70
        
        if best_similarity >= threshold:
            return best_match_name, best_similarity
        
        return None, 0
    
    def register_face(self, name: str, num_samples: int = 5):
        """註冊新人臉"""
        if self.cap is None:
            self.start_camera()
        
        print(f"\n📸 開始註冊 '{name}' 的人臉")
        print(f"請保持正面對鏡頭，將拍攝 {num_samples} 張照片")
        print("按 SPACE 拍照，按 ESC 取消\n")
        
        features_list = []
        images_list = []
        captured = 0
        
        while captured < num_samples:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            faces = self.detect_faces(frame)
            
            display_frame = frame.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.putText(
                display_frame,
                f"Captured: {captured}/{num_samples} - Press SPACE",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            cv2.imshow('Register Face', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and len(faces) > 0:
                bbox = faces[0]
                features = self.extract_face_features(frame, bbox)
                
                if features is not None:
                    features_list.append(features)
                    x, y, w, h = bbox
                    face_img = frame[y:y+h, x:x+w]
                    images_list.append(face_img)
                    captured += 1
                    print(f"✅ 已拍攝 {captured}/{num_samples}")
                else:
                    print("⚠️ 特徵提取失敗，請重試")
            
            elif key == 27:
                print("❌ 註冊已取消")
                cv2.destroyWindow('Register Face')
                return
        
        self.known_faces[name] = {
            'features': features_list,
            'images': images_list
        }
        self.save_database()
        
        print(f"\n🎉 '{name}' 註冊成功！")
        cv2.destroyWindow('Register Face')
    
    def set_target(self, name: str):
        """設定要追蹤的目標"""
        if name in self.known_faces:
            self.target_name = name
            print(f"🎯 追蹤目標設定為: {name}")
        else:
            print(f"❌ 找不到 '{name}'，請先註冊人臉")
    
    def detect_and_recognize(self, frame):
        """
        偵測並辨識畫面中的所有人臉
        
        Returns:
            (annotated_frame, detections)
        """
        faces = self.detect_faces(frame)
        
        detections = []
        annotated_frame = frame.copy()
        
        for face_location in faces:
            x, y, w, h = face_location
            
            name, confidence = self.recognize_face(frame, face_location)
            
            if name == self.target_name:
                color = (0, 255, 0)
                label = f"{name} ({confidence:.1f}%) [TARGET]"
                self.last_seen_position = (x + w//2, y + h//2)
            elif name:
                color = (255, 0, 0)
                label = f"{name} ({confidence:.1f}%)"
            else:
                color = (0, 0, 255)
                label = "Unknown"
            
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(
                annotated_frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
            
            detections.append((name, confidence, face_location))
        
        return annotated_frame, detections
    
    def run_live_recognition(self):
        """執行即時人臉辨識"""
        if self.cap is None:
            self.start_camera()
        
        print("\n🎥 即時人臉辨識啟動！")
        print("按鍵說明：")
        print("  'q' - 退出")
        print("  'r' - 註冊新人臉")
        print("  't' - 設定追蹤目標")
        if self.target_name:
            print(f"\n🎯 當前追蹤目標: {self.target_name}\n")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ 無法讀取影像")
                break
            
            annotated_frame, detections = self.detect_and_recognize(frame)
            
            cv2.imshow('Kid Robot - Face Recognition (Tasks API)', annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                name = input("\n請輸入要註冊的名字: ")
                if name:
                    self.register_face(name)
            elif key == ord('t'):
                print(f"\n已註冊的人臉: {list(self.known_faces.keys())}")
                target = input("請輸入要追蹤的名字: ")
                if target:
                    self.set_target(target)
        
        self.stop_camera()
    
    def stop_camera(self):
        """停止攝像頭"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ 攝像頭已關閉")
    
    def get_target_position(self):
        """取得追蹤目標的位置"""
        return self.last_seen_position


if __name__ == "__main__":
    print("\n" + "="*60)
    print("家庭陪讀機器人 - 人臉辨識系統 (Tasks API)")
    print("="*60)
    
    detector = LightweightFaceDetector()
    detector.run_live_recognition()