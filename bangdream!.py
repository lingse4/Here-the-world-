import os
import subprocess
import cv2
import numpy as np
import pyautogui
import time
import pyautogui as p
from mini_record import mini_record

commands = [
    "adb connect emulator-5554",
    "adb -s emulator-5554 shell am start-foreground-service --user 0 -a jp.co.cyberagent.stf.ACTION_START -n jp.co.cyberagent.stf/.Service && adb -s emulator-5554 forward tcp:1102 localabstract:stfservice",
    "adb -s emulator-5554 forward tcp:1092 localabstract:stfagent && adb -s emulator-5554 shell pm path jp.co.cyberagent.stf && adb -s emulator-5554 shell export CLASSPATH=\"package:/data/app/jp.co.cyberagent.stf-k4TOFwRWHHDXNz0Jq6FzVA==/base.apk\";exec app_process /system/bin jp.co.cyberagent.stf.Agent",
    "adb -s emulator-5554 shell /data/local/tmp/minitouch",
    "adb -s emulator-5554 forward tcp:1092 localabstract:minitouch"
]

# Define the CREATE_NO_WINDOW flag
CREATE_NO_WINDOW = 0x08000000

for i, command in enumerate(commands):
    subprocess.Popen(command, creationflags=CREATE_NO_WINDOW, shell=True)
    # 第一个命令（连接）执行后等待1秒
    if i == 0:
        time.sleep(1)


# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "emulator-5554"  # 指定目标设备
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接！请确认设备 {device_serial} 已开启USB调试模式")

# -------------------- 2. ADB截图函数 --------------------
def adb_screenshot(save_path="screen.png"):
    """截取模拟器屏幕并保存为文件"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "emulator-5554"  # 指定目标设备
    subprocess.run(f"{adb_path} -s {device_serial} shell screencap -p /sdcard/screen.png", shell=True, check=True)
    subprocess.run(f"{adb_path} -s {device_serial} pull /sdcard/screen.png {save_path}", shell=True, check=True)
    return save_path  # 返回图像路径

# -------------------- 5. ADB点击函数 --------------------
def adb_tap(x, y):
    """使用ADB命令在指定坐标点击"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "emulator-5554"  # 指定目标设备
    subprocess.run(f"{adb_path} -s {device_serial} shell input tap {x} {y}", shell=True, check=True)

def cv_imread(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在！")
        return None
    try:
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None


def get_xy0(img_model_path, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param threshold: 匹配阈值，默认为 0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果未匹配则返回 None
    """
    # 将屏幕截图保存
    pyautogui.screenshot("./Pictures/Screenshots/screenshot.png")
    # 载入截图
    img = cv_imread("./Pictures/Screenshots/screenshot.png")
    # 载入模板
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        print("无法加载截图或模板图片")
        return None

    # 获取模板的宽度和高度
    height, width, channel = img_terminal.shape
        # 转换为灰度图（如果原图像是彩色）
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if len(img_terminal.shape) == 3:
        img_terminal = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)

    # 确保深度一致（转换为8位无符号）
    img = img.astype(np.uint8)
    img_terminal = img_terminal.astype(np.uint8)
    # 进行模板匹配
    result = cv2.matchTemplate(img, img_terminal, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 检查匹配值是否达到阈值
    if max_val >= threshold:
        # 解析出匹配区域的左上角坐标
        upper_left = max_loc
        # 计算匹配区域右下角的坐标
        lower_right = (upper_left[0] + width, upper_left[1] + height)
        # 计算中心区域的坐标并且返回
        avg = (int((upper_left[0] + lower_right[0]) / 2), int((upper_left[1] + lower_right[1]) / 2))
        return avg
    else:
        print(f"匹配值 {max_val} 未达到阈值 {threshold}")
        return None


def get_xy(img_model_path, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param threshold: 匹配阈值，默认为 0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果未匹配则返回 None
    """
    # 将屏幕截图保存
    adb_screenshot("./Pictures/Screenshots/screenshot.png")
    # 载入截图
    img = cv_imread("./Pictures/Screenshots/screenshot.png")
    # 载入模板
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        print("无法加载截图或模板图片")
        return None

    # 获取模板的宽度和高度
    height, width, channel = img_terminal.shape
    # 进行模板匹配
    result = cv2.matchTemplate(img, img_terminal, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 检查匹配值是否达到阈值
    if max_val >= threshold:
        # 解析出匹配区域的左上角坐标
        upper_left = max_loc
        # 计算匹配区域右下角的坐标
        lower_right = (upper_left[0] + width, upper_left[1] + height)
        # 计算中心区域的坐标并且返回
        avg = (int((upper_left[0] + lower_right[0]) / 2), int((upper_left[1] + lower_right[1]) / 2))
        return avg
    else:
        print(f"匹配值 {max_val} 未达到阈值 {threshold}")
        return None

def auto_click(var_avg):
    """
    接受一个元组参数，自动点击
    :param var_avg: 坐标范围
    :return: None
    """
    if var_avg:
        adb_tap(var_avg[0], var_avg[1], button='left')
        time.sleep(2)
    else:
        print("未检测到目标，无法点击")

def routine0(img_model_path, name, threshold=0.8):
    while True:
        avg = get_xy0(img_model_path, threshold)
        if avg:
            print(f'正在点击 {name}，坐标：{avg}')
            pyautogui.click(avg[0], avg[1])
            return avg
        else:
            print(f"未检测到 {name}，继续检测...")

def routine(img_model_path, name, threshold=0.8):
    while True:
        avg = get_xy(img_model_path, threshold)
        if avg:
            print(f'正在点击 {name}，坐标：{avg}')
            adb_tap(avg[0], avg[1])
            return avg
        else:
            print(f"未检测到 {name}，继续检测...")

def blue_rule(x, y):
    """蓝色规则：G通道<50时点按（检测模拟器画面）"""
    # 确保截图保存目录存在
    save_dir = "./Pictures/Screenshots"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "blue_rule_screenshot.png")
    
    while True:        
        try:
            # 1. 截取模拟器屏幕（替代原屏幕像素检测）
            adb_screenshot(save_path)
            
            # 2. 加载截图并检查有效性
            img = cv_imread(save_path)
            
            # 4. 获取像素BGR值（OpenCV格式），提取G通道
            pixel_bgr = img[y, x]  # 注意：OpenCV坐标为 (y,x)
            g_channel = pixel_bgr[1]  # G通道在BGR格式中为索引1
            
            # 5. 满足条件时执行点击（补充原逻辑缺失的点击动作）
            if g_channel < 100:
                print(f"蓝色规则触发，G通道值: {g_channel}，执行点击")
                adb_tap(x, y)  # 通过ADB点击模拟器坐标
        except Exception as e:
            print(f"蓝色规则检测异常: {e}")
            continue



#adb_tap(1085,500)
avg = routine(r"C:\Users\38384\Pictures\Screenshots\猫猫.png", "猫猫", threshold=0.9)
#print(f"点击完成,坐标：{avg}")
mini_record("C:/Users/38384/Desktop/operation2.mt",1092)

