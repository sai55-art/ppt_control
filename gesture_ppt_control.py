"""
手势控制PPT翻页程序 - 简化版
- 手向左移动 → 上一页 (←)
- 手向右移动 → 下一页 (→)
- 无需手指姿态判断，更简单可靠
"""
import cv2
import mediapipe as mp
import numpy as np
import time
import sys
import os
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard
from collections import deque
import json

from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision import RunningMode as VisionRunningMode


class GesturePPTControl:
    def __init__(self):
        self.config = self.load_config()
        
        model_path = "hand_landmarker.task"
        print("检查模型文件...")
        if not os.path.exists(model_path):
            print(f"错误: 模型文件不存在: {model_path}")
            sys.exit(1)
        
        print("加载手势识别模型...")
        base_options = BaseOptions(model_asset_path=model_path)
        conf = self.config['confidence']
        options = HandLandmarkerOptions(
            base_options=base_options,
            running_mode=VisionRunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=conf['hand_detection'],
            min_hand_presence_confidence=conf['hand_presence'],
            min_tracking_confidence=conf['tracking']
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        print("模型加载成功!")
        
        self.keyboard_controller = keyboard.Controller()
        
        det = self.config['detection']
        self.speed_threshold = det.get('speed_threshold', 0.03)
        self.direction_lock_time = det.get('direction_lock_time', 0.8)
        self.cooldown_time = det.get('cooldown_time', 0.8)
        
        self.hand_detected = False
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        # 手掌位置追踪
        self.hand_positions = deque(maxlen=30)
        self.hand_speed = 0
        self.speed_frames = 0
        
        # 方向锁定和冷却
        self.last_direction = None
        self.direction_locked_until = 0
        self.last_trigger_time = 0
        self.current_direction = None

    def load_config(self):
        config_path = "config.json"
        default_config = {
            "camera": {"index": 1, "width": 640, "height": 480, "fps": 30},
            "detection": {
                "speed_threshold": 0.03,
                "direction_lock_time": 0.8,
                "cooldown_time": 0.8
            },
            "confidence": {
                "hand_detection": 0.4,
                "hand_presence": 0.4,
                "tracking": 0.4
            }
        }
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
                    print(f"配置加载成功: {config_path}")
        except Exception as e:
            print(f"配置加载失败，使用默认配置: {e}")
        return default_config

    def get_hand_center(self, landmarks):
        """
        获取手掌中心位置（使用中指根部landmark 9）
        这是手掌最稳定的点
        """
        # landmark 9 是中指根部，最稳定
        # landmark 0 是手腕，也可以用
        hand_center = np.array([landmarks[9].x, landmarks[9].y])
        return hand_center

    def calculate_speed(self, current_x):
        """计算手掌移动速度"""
        if len(self.hand_positions) < 3:
            return 0
        
        positions = list(self.hand_positions)
        n = min(5, len(positions))
        
        delta = current_x - positions[-n]
        return delta / n

    def detect_direction(self, speed):
        """检测移动方向"""
        if abs(speed) < self.speed_threshold:
            return None
        return 'left' if speed < 0 else 'right'

    def trigger_action(self, direction):
        """触发翻页动作"""
        current_time = time.time()
        
        # 冷却检查
        if current_time - self.last_trigger_time < self.cooldown_time:
            return False
        
        # 方向锁定检查
        if current_time < self.direction_locked_until:
            if self.last_direction != direction:
                return False
        
        action = None
        if direction == 'left':
            try:
                self.keyboard_controller.press(keyboard.Key.left)
                time.sleep(0.05)
                self.keyboard_controller.release(keyboard.Key.left)
                action = "上一页"
                self.last_trigger_time = current_time
                self.last_direction = 'left'
                self.direction_locked_until = current_time + self.direction_lock_time
                print(f"[触发] 上一页 (向左移动, 速度={self.hand_speed:.4f})")
            except Exception as e:
                print(f"[错误] 发送按键失败: {e}")
        elif direction == 'right':
            try:
                self.keyboard_controller.press(keyboard.Key.right)
                time.sleep(0.05)
                self.keyboard_controller.release(keyboard.Key.right)
                action = "下一页"
                self.last_trigger_time = current_time
                self.last_direction = 'right'
                self.direction_locked_until = current_time + self.direction_lock_time
                print(f"[触发] 下一页 (向右移动, 速度={self.hand_speed:.4f})")
            except Exception as e:
                print(f"[错误] 发送按键失败: {e}")
        
        return action

    def draw_hand_landmarks(self, frame, landmarks):
        """绘制手部关键点"""
        h, w = frame.shape[:2]
        
        connections = [
            (0,1),(1,2),(2,3),(3,4),
            (0,5),(5,6),(6,7),(7,8),
            (5,9),(9,10),(10,11),(11,12),
            (9,13),(13,14),(14,15),(15,16),
            (13,17),(17,18),(18,19),(19,20),
            (0,17)
        ]
        
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        
        for s, e in connections:
            cv2.line(frame, points[s], points[e], (0, 255, 0), 2)
        
        # 高亮手掌中心（landmark 9）
        cv2.circle(frame, points[9], 10, (0, 0, 255), -1)
        
        for i, (x, y) in enumerate(points):
            if i != 9:
                cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)
        
        return points

    def draw_direction_arrow(self, frame, direction):
        """绘制方向箭头"""
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        if direction == 'left':
            cv2.putText(frame, "<<<", (center_x - 80, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 5)
        elif direction == 'right':
            cv2.putText(frame, ">>>", (center_x - 40, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 5)

    def run(self):
        print("打开摄像头...")
        camera_cfg = self.config['camera']
        cap = cv2.VideoCapture(camera_cfg['index'], cv2.CAP_ANY)
        
        if not cap.isOpened():
            print("无法打开摄像头!")
            sys.exit(1)
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_cfg['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_cfg['height'])
        
        print(f"摄像头已打开! 索引: {camera_cfg['index']}")
        
        root = tk.Tk()
        root.title("手势控制PPT")
        root.geometry("700x600")
        root.configure(bg='#1a1a1a')
        
        tk.Label(root, text="手势控制PPT翻页", font=("Arial", 18, "bold"), 
                bg='#1a1a1a', fg='white').pack(pady=10)
        
        video_label = tk.Label(root, bg='black')
        video_label.pack(pady=10)
        
        info_frame = tk.Frame(root, bg='#1a1a1a')
        info_frame.pack(pady=10)
        
        fps_label = tk.Label(info_frame, text="FPS: 0", font=("Arial", 12), 
                            bg='#1a1a1a', fg='cyan')
        fps_label.grid(row=0, column=0, padx=20)
        
        status_label = tk.Label(info_frame, text="状态: 等待...", font=("Arial", 12), 
                               bg='#1a1a1a', fg='yellow')
        status_label.grid(row=0, column=1, padx=20)
        
        speed_label = tk.Label(info_frame, text="速度: 0.000", font=("Arial", 14, "bold"), 
                               bg='#1a1a1a', fg='white')
        speed_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        direction_label = tk.Label(info_frame, text="方向: -", font=("Arial", 12), 
                                   bg='#1a1a1a', fg='gray')
        direction_label.grid(row=2, column=0, padx=20)
        
        action_label = tk.Label(info_frame, text="动作: 无", font=("Arial", 12), 
                                bg='#1a1a1a', fg='white')
        action_label.grid(row=2, column=1, padx=20)
        
        help_text = "手向左移动 = 上一页 | 手向右移动 = 下一页"
        tk.Label(root, text=help_text, font=("Arial", 10), 
                bg='#1a1a1a', fg='#888888').pack(side=tk.BOTTOM, pady=10)
        
        def on_closing():
            cap.release()
            self.landmarker.close()
            root.destroy()
        
        def check_key(event):
            if event.char.lower() == 'q':
                on_closing()
        
        exit_btn = tk.Button(root, text="退出", font=("Arial", 12, "bold"),
                           bg='#ff4444', fg='white', width=10, height=2,
                           command=on_closing)
        exit_btn.pack(side=tk.BOTTOM, pady=10)
        
        def update_frame():
            ret, frame = cap.read()
            if not ret:
                root.after(10, update_frame)
                return
            
            frame = cv2.flip(frame, 1)
            
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.fps_start_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.fps_start_time = current_time
                fps_label.config(text=f"FPS: {self.fps}")
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp = int(current_time * 1000)
            result = self.landmarker.detect_for_video(mp_image, timestamp)
            
            self.hand_detected = False
            action = None
            
            if current_time >= self.direction_locked_until:
                self.last_direction = None
            
            if result.hand_landmarks:
                self.hand_detected = True
                status_label.config(text="状态: 检测到手", fg="green")
                
                for landmarks, handedness_list in zip(result.hand_landmarks, result.handedness):
                    if handedness_list:
                        hand_type = handedness_list[0].category_name
                        
                        self.draw_hand_landmarks(frame, landmarks)
                        
                        # 获取手掌中心位置
                        hand_center = self.get_hand_center(landmarks)
                        hand_x = hand_center[0]
                        
                        # 记录位置
                        self.hand_positions.append(hand_x)
                        
                        # 计算速度
                        self.hand_speed = self.calculate_speed(hand_x)
                        
                        # 检测方向
                        direction = self.detect_direction(self.hand_speed)
                        
                        # 更新UI
                        speed_label.config(text=f"速度: {self.hand_speed:.4f}", fg='lime')
                        
                        if direction:
                            self.current_direction = direction
                            direction_text = "向左" if direction == 'left' else "向右"
                            direction_label.config(text=f"方向: {direction_text}", fg='yellow')
                            
                            # 触发动作
                            action = self.trigger_action(direction)
                            if action:
                                self.hand_positions.clear()
                            
                            # 绘制箭头
                            self.draw_direction_arrow(frame, direction)
                        else:
                            direction_label.config(text="方向: -", fg='gray')
                
            else:
                status_label.config(text="状态: 未检测到手", fg="gray")
                speed_label.config(text="速度: 0.000", fg='gray')
                direction_label.config(text="方向: -", fg='gray')
                self.hand_positions.clear()
            
            if action:
                action_label.config(text=f"动作: {action}", fg="yellow")
            
            cooldown = max(0, self.cooldown_time - (current_time - self.last_trigger_time))
            if cooldown > 0:
                action_label.config(text=f"冷却: {cooldown:.1f}s", fg="orange")
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            img_tk = ImageTk.PhotoImage(image=img)
            video_label.img_tk = img_tk
            video_label.configure(image=img_tk)
            
            root.after(10, update_frame)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.bind('<Key>', check_key)
        
        print("=" * 50)
        print("简化版手势控制PPT")
        print("手向左移动 = 上一页")
        print("手向右移动 = 下一页")
        print("按Q退出")
        print("=" * 50)
        update_frame()
        root.mainloop()


if __name__ == "__main__":
    controller = GesturePPTControl()
    controller.run()
