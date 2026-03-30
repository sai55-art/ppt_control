@echo off
chcp 65001 > nul
echo ========================================
echo   手势控制PPT - 打包脚本
echo ========================================
echo.

REM 检查是否安装PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/2] 未安装PyInstaller，正在安装...
    pip install pyinstaller -q
    if %errorlevel% neq 0 (
        echo [错误] PyInstaller安装失败！
        pause
        exit /b 1
    )
) else (
    echo [1/2] PyInstaller已安装
)

REM 检查主程序文件
if not exist gesture_ppt_control.py (
    echo [错误] 找不到 gesture_ppt_control.py！
    pause
    exit /b 1
)

REM 检查模型文件
if not exist hand_landmarker.task (
    echo [错误] 找不到 hand_landmarker.task！
    pause
    exit /b 1
)

echo [2/2] 开始打包...
echo.

REM 清理旧的打包输出目录
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM 执行打包 - GUI模式
pyinstaller --onefile ^
    --noconsole ^
    --name "GesturePPTControl" ^
    --icon=NONE ^
    --add-data "hand_landmarker.task;." ^
    --add-data "config.json;." ^
    --hidden-import "mediapipe.tasks.c" ^
    --hidden-import "mediapipe.tasks.python" ^
    --hidden-import "mediapipe.tasks.python.vision" ^
    --hidden-import "mediapipe.tasks.python.vision.core" ^
    gesture_ppt_control.py

if %errorlevel% neq 0 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo   可执行文件位置: dist\GesturePPTControl.exe
echo.
echo.
echo 使用说明:
echo   1. 双击 GesturePPTControl.exe 运行
echo   2. 程序会显示窗口，显示摄像头画面和状态
echo   3. 点击窗口底部的"退出"按钮关闭程序
echo   4. 手向左移动 = 上一页
echo   5. 手向右移动 = 下一页
echo.
echo ========================================

pause
