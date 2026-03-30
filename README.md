# 手势控制PPT翻页程序

通过手势识别控制PowerPoint演示文稿翻页的Python程序，支持可视化界面和实时状态显示。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## 功能特性

- 🖐️ **手势控制** - 通过摄像头识别手势动作
- ⬅️ **手向左移动** → PPT上一页
- ➡️ **手向右移动** → PPT下一页
- 🖥️ **可视化界面** - 显示摄像头画面和实时状态
- 📊 **状态监控** - FPS、速度、方向、动作实时显示
- 🎛️ **可配置参数** - 灵敏度、冷却时间等可自定义
- 📦 **一键打包** - 支持打包成独立EXE文件分发

## 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11
- 摄像头

### 安装依赖

```bash
pip install -r requirements.txt
```

### 下载模型文件

从Google MediaPipe下载手势识别模型：

```bash
# 下载 hand_landmarker.task (约7.8MB)
# https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

或使用以下命令：

```bash
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

### 运行程序

```bash
python gesture_ppt_control.py
```

## 使用方法

| 操作 | 效果 |
|------|------|
| 手向左挥动 | PPT 上一页 |
| 手向右挥动 | PPT 下一页 |
| 点击"退出"按钮 | 关闭程序 |
| 按 Q 键 | 关闭程序 |

## 配置说明

编辑 `config.json` 可调整参数：

```json
{
  "camera": {
    "index": 1,          // 摄像头索引（0为默认摄像头）
    "width": 640,        // 画面宽度
    "height": 480,       // 画面高度
    "fps": 30            // 帧率
  },
  "detection": {
    "speed_threshold": 0.03,        // 速度阈值（越小越灵敏）
    "direction_lock_time": 0.8,     // 方向锁定时间（秒）
    "cooldown_time": 0.8            // 触发后冷却时间（秒）
  },
  "confidence": {
    "hand_detection": 0.4,          // 手部检测置信度
    "hand_presence": 0.4,           // 手部存在置信度
    "tracking": 0.4                 // 追踪置信度
  }
}
```

## 打包成EXE

### 方法一：使用批处理脚本（推荐）

```bash
build.bat
```

### 方法二：使用Python脚本

```bash
python build.py
```

打包完成后，可执行文件位于：`dist/GesturePPTControl.exe`

## 项目结构

```
gesture-ppt-control/
├── gesture_ppt_control.py    # 主程序
├── config.json               # 配置文件
├── requirements.txt          # Python依赖
├── build.py                  # 打包脚本（Python）
├── build.bat                 # 打包脚本（Windows）
├── hand_landmarker.task      # 手势识别模型（需下载）
└── README.md                 # 项目说明
```

## 技术栈

- **Python 3.8+** - 开发语言
- **OpenCV** - 摄像头图像处理
- **MediaPipe** - 手势识别
- **Tkinter** - GUI界面
- **PIL** - 图像处理
- **pynput** - 键盘控制
- **PyInstaller** - 打包工具

## 常见问题

### Q: 找不到摄像头
**A:** 确保没有其他程序占用摄像头，可以尝试修改 `config.json` 中的摄像头索引（0 或 1）

### Q: 手势识别不准确
**A:** 
- 确保光线充足
- 调整 `config.json` 中的 `speed_threshold` 参数
- 手势动作幅度可以大一些

### Q: PPT没有反应
**A:** 
- 确保 PPT 窗口是活动状态
- 检查程序窗口是否显示"检测到手"
- 尝试更大幅度的手势动作

### Q: 打包后的EXE无法运行
**A:** 
- 右键选择"以管理员身份运行"
- 确保杀毒软件没有拦截
- 首次运行可能需要几秒钟初始化

## 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **存储**: 至少 200MB 可用空间
- **硬件**: 摄像头

## 开发计划

- [ ] 支持自定义手势动作
- [ ] 添加声音提示
- [ ] 支持其他演示软件（Keynote、Google Slides）
- [ ] 多语言支持
- [ ] 手势训练功能

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [MediaPipe](https://mediapipe.dev/) - Google 开源的手势识别框架
- [OpenCV](https://opencv.org/) - 计算机视觉库

---

**版本**: 2.0.0  
**作者**: [Your Name]  
**更新日期**: 2025-02-20