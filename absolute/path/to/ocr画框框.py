import cv2
import subprocess
import numpy as np
from paddleocr import PaddleOCR

# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16416"  # 指定目标设备
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接！请确认设备 {device_serial} 已开启USB调试模式")

# -------------------- 2. ADB截图函数 --------------------
def adb_screenshot(save_path="screen.png"):
    """截取模拟器屏幕并返回OpenCV图像"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16416"  # 指定目标设备
    subprocess.run(f"{adb_path} -s {device_serial} shell screencap -p /sdcard/screen.png", shell=True, check=True)
    subprocess.run(f"{adb_path} -s {device_serial} pull /sdcard/screen.png {save_path}", shell=True, check=True)
    
    # 改进图像预处理
    img = cv2.imread(save_path)
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 应用自适应阈值化，提高文字对比度
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # 可选：进行形态学操作，增强文字
    kernel = np.ones((1, 1), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    cv2.imwrite(save_path, thresh)
    return save_path  # 返回图像路径

# -------------------- 3. 主程序 --------------------
if __name__ == "__main__":
    # 初始化OCR，优化配置以提高英文和数字识别率
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",  # 使用英文模型
        det_db_thresh=0.3,  # 降低文本检测阈值
        det_db_box_thresh=0.3,  # 降低文本框阈值
        det_db_unclip_ratio=2.0,  # 调整文本框扩张比例
        rec_thresh=0.5  # 降低识别阈值
    )
    
    # 检查ADB连接
    check_adb_connection()
    
    # 截取屏幕
    screen = adb_screenshot()
    
    # OCR识别
    result = ocr.ocr(screen)
    
    # 提取并打印所有识别结果
    if result is not None and len(result) > 0:
        for line in result:
            if line:
                for detection in line:
                    # detection格式通常是[[坐标], (文本, 置信度)]
                    if isinstance(detection, list) and len(detection) > 1:
                        text, confidence = detection[1]
                        print(f"识别文本: '{text}', 置信度: {confidence:.4f}")
                    else:
                        print(f"line: {detection}")
    else:
        print("未识别到任何内容")
    
    # 可视化识别结果
    img = cv2.imread(screen)
    if result is not None and len(result) > 0:
        for line in result:
            if line:
                for detection in line:
                    if isinstance(detection, list) and len(detection) > 1:
                        box = np.array(detection[0], dtype=np.int32)
                        text, confidence = detection[1]
                        
                        # 绘制文本框
                        cv2.polylines(img, [box], isClosed=True, color=(0, 255, 0), thickness=2)
                        
                        # 在文本框上方显示识别的文本和置信度
                        x, y = box[0][0], box[0][1] - 10
                        if y < 10: y = 30
                        cv2.putText(img, f"{text} ({confidence:.2f})", 
                                   (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # 显示带有识别框的图像
    cv2.imshow("OCR识别结果", img)
    cv2.imwrite("ocr_result.png", img)  # 保存结果图像
    cv2.waitKey(0)
    cv2.destroyAllWindows()