import time
import cv2
import subprocess
import numpy as np
from paddleocr import PaddleOCR
import os
import traceback

# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16416"  # 指定目标设备
    
    try:
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
        if device_serial not in result.stdout:
            print(f"设备 {device_serial} 未连接，尝试连接...")
            subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
            result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
            if device_serial not in result.stdout:
                raise ConnectionError(f"ADB设备未连接！请确认设备 {device_serial} 已开启USB调试模式")
        print(f"设备 {device_serial} 连接成功")
    except Exception as e:
        print(f"检查ADB连接时出错: {e}")
        raise

# -------------------- 2. ADB截图函数 --------------------
def adb_screenshot(save_path="screen.png"):
    """截取模拟器屏幕并返回图像路径"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16416"  # 指定目标设备
    
    try:
        # 执行截图命令
        subprocess.run(f"{adb_path} -s {device_serial} shell screencap -p /sdcard/screen.png", 
                      shell=True, check=True, capture_output=True, text=True)
        # 拉取截图文件
        subprocess.run(f"{adb_path} -s {device_serial} pull /sdcard/screen.png {save_path}", 
                      shell=True, check=True, capture_output=True, text=True)
        
        # 检查文件是否成功保存
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"截图文件 {save_path} 未成功保存")
        
        # 检查文件大小是否合理
        if os.path.getsize(save_path) < 1024:  # 如果文件太小，可能是空文件
            raise ValueError(f"截图文件 {save_path} 可能为空，文件大小: {os.path.getsize(save_path)} 字节")
        
        print(f"截图已保存至 {save_path}")
        return save_path
    except subprocess.CalledProcessError as e:
        print(f"ADB命令执行失败: {e}")
        print(f"命令输出: {e.stdout}")
        print(f"错误输出: {e.stderr}")
        raise
    except Exception as e:
        print(f"ADB截图过程中出错: {e}")
        raise

# -------------------- 3. 主程序 --------------------
if __name__ == "__main__":
    try:
        print("=== OCR识别程序开始 ===")
        
        # 初始化OCR，使用支持的参数配置（更新为新版本参数）
        print("初始化OCR引擎...")
        ocr = PaddleOCR(
            use_textline_orientation=True,  # 替代 use_angle_cls
            lang="en",  # 使用英文模型
            text_det_thresh=0.1,  # 替代 det_db_thresh
            text_det_box_thresh=0.1,  # 替代 det_db_box_thresh
            text_det_unclip_ratio=2.0  # 替代 det_db_unclip_ratio
        )
        print("OCR引擎初始化完成")
        
        # 检查ADB连接
        print("检查ADB连接...")
        check_adb_connection()
        
        # 截取屏幕
        print("截取屏幕...")
        time.sleep(5)
        screen = adb_screenshot()
        
        # OCR识别 - 使用predict方法
        print("执行OCR识别...")
        result = ocr.predict(screen)
        
        # 提取并打印所有识别结果
        print("识别结果解析...")
        # 确保result不为None
        if result is not None:
            found_text = False
            # 根据PaddleOCR最新版返回格式解析结果
            if isinstance(result, dict):
                # 检查是否有识别到的文本
                if 'rec_texts' in result and result['rec_texts']:
                    found_text = True
                    for i, text in enumerate(result['rec_texts']):
                        # 获取对应的置信度
                        confidence = result['rec_scores'][i] if 'rec_scores' in result and i < len(result['rec_scores']) else 0
                        print(f"识别文本: '{text}', 置信度: {confidence:.4f}")
                else:
                    print("未识别到任何文本")
            elif isinstance(result, list):
                # 兼容旧版本格式
                for line in result:
                    if line:
                        for detection in line:
                            # detection格式通常是[[坐标], (文本, 置信度)]
                            if isinstance(detection, list) and len(detection) > 1:
                                text, confidence = detection[1]
                                print(f"识别文本: '{text}', 置信度: {confidence:.4f}")
                                found_text = True
                            elif isinstance(detection, tuple) and len(detection) > 1:
                                # 检查是否是(文本, 置信度)格式
                                if isinstance(detection[0], str):
                                    text, confidence = detection
                                    print(f"识别文本: '{text}', 置信度: {confidence:.4f}")
                                    found_text = True
            if not found_text:
                print("未识别到可解析的文本")
        else:
            print("OCR识别结果为空")
        
        print("=== OCR识别程序完成 ===")
    except Exception as e:
        print(f"程序执行出错: {e}")
        print("详细错误信息:")
        traceback.print_exc()