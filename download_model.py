"""
下载MediaPipe手势识别模型
"""

import urllib.request
import os


def download_model():
    model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    model_path = "hand_landmarker.task"

    if os.path.exists(model_path):
        print(f"模型文件已存在: {model_path}")
        return

    print("正在下载手势识别模型...")
    print(f"URL: {model_url}")
    print(f"保存路径: {model_path}")
    print("文件大小约7.8MB，请稍候...")

    try:
        urllib.request.urlretrieve(model_url, model_path)
        print(f"\n✅ 下载完成！")
        print(f"模型已保存到: {os.path.abspath(model_path)}")
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        print("\n请手动下载模型文件：")
        print(
            "1. 访问: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
        )
        print("2. 将下载的文件保存为 hand_landmarker.task")


if __name__ == "__main__":
    download_model()
