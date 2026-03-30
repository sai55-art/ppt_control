"""
手势控制PPT翻页程序 - PyInstaller 打包脚本
"""
import os
import subprocess
import sys
import shutil

def main():
    print("=" * 60)
    print("手势控制PPT - 开始打包")
    print("=" * 60)
    
    # 检查主程序文件
    if not os.path.exists('gesture_ppt_control.py'):
        print("[错误] 找不到 gesture_ppt_control.py")
        input("按回车退出...")
        return 1
    
    # 检查模型文件
    if not os.path.exists('hand_landmarker.task'):
        print("[错误] 找不到 hand_landmarker.task")
        input("按回车退出...")
        return 1
    
    # 检查配置文件
    if not os.path.exists('config.json'):
        print("[警告] 找不到 config.json，将使用默认配置")
    
    print("\n检查 PyInstaller...")
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("[信息] 正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print("\n开始打包...")
    
    # 清理旧的打包输出目录
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 执行打包命令（GUI模式 - 窗口显示）
    cmd = [
        'pyinstaller',
        '--onefile',
        '--noconsole',
        '--name', 'GesturePPTControl',
        '--add-data', 'hand_landmarker.task;.',
        '--add-data', 'config.json;.',
        '--collect-all', 'mediapipe',
        '--collect-all', 'cv2',
        'gesture_ppt_control.py'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"[错误] 打包失败: {e}")
        input("按回车退出...")
        return 1
    
    print("\n" + "=" * 60)
    print("打包完成！")
    print("=" * 60)
    print(f"\n可执行文件: {os.path.abspath('dist/GesturePPTControl.exe')}")
    print("\n使用说明:")
    print("1. 双击 .exe 文件运行")
    print("2. 程序会显示一个窗口，显示摄像头画面和状态信息")
    print("3. 点击窗口底部的'退出'按钮关闭程序")
    print("4. 手向左移动 = 上一页")
    print("5. 手向右移动 = 下一页")
    print("=" * 60)
    
    input("\n按回车退出...")

if __name__ == "__main__":
    main()
