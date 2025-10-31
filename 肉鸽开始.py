
import subprocess
import time
import os

import cv2
import numpy as np

adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"
SCREENSHOT_MAIN = r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\screenshot1.png"
device_serial = "127.0.0.1:16384" 
device_serialb = "127.0.0.1:16416" 


def adb_screenshot(save_path=SCREENSHOT_MAIN):
    """截取模拟器屏幕并保存为文件"""
    """通过 ADB 直接获取截图二进制流，避免文件传输损坏"""
    
    command = f'"{adb_path}" -s {device_serial} exec-out screencap -p'

    try:
        # 直接捕获二进制数据
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        # 将二进制数据写入文件
        with open(save_path, "wb") as f:
            f.write(result.stdout)
        print(f"截图保存成功: {save_path}")
        return save_path
    except subprocess.CalledProcessError as e:
        print(f"截图失败: {e.stderr.decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"截图异常: {str(e)}")
        return False

def adb_screenshotb(save_path=SCREENSHOT_MAIN):
    """截取模拟器屏幕并保存为文件"""
    """通过 ADB 直接获取截图二进制流，避免文件传输损坏"""
    
    command = f'"{adb_path}" -s {device_serialb} exec-out screencap -p'

    try:
        # 直接捕获二进制数据
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        # 将二进制数据写入文件
        with open(save_path, "wb") as f:
            f.write(result.stdout)
        print(f"截图保存成功: {save_path}")
        return save_path
    except subprocess.CalledProcessError as e:
        print(f"截图失败: {e.stderr.decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"截图异常: {str(e)}")
        return False

def cv_imread(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在！")
        return None
    try:
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

def get_xy(img_model_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值，默认为0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果没有匹配则返回None
    """
    screenshot_dir = "./Pictures/Screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    adb_screenshot(SCREENSHOT_MAIN)
    img = cv_imread(SCREENSHOT_MAIN)
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)
    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

def get_xyb(img_model_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值，默认为0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果没有匹配则返回None
    """
    screenshot_dir = "./Pictures/Screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    adb_screenshotb(SCREENSHOT_MAIN)
    img = cv_imread(SCREENSHOT_MAIN)
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)
    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None



def adb_tap(x, y):
    """
    使用ADB命令模拟点击屏幕坐标 (x, y)
    """  # ADB 的完整路径
    x = int(x)
    y = int(y)
    command = f'"{adb_path}" -s {device_serial} shell input tap {x} {y}'
    print(f"执行的命令: {command}")
    os.system(command)

def adb_tapb(x, y):
    """
    使用ADB命令模拟点击屏幕坐标 (x, y)
    """  # ADB 的完整路径
    x = int(x)
    y = int(y)
    command = f'"{adb_path}" -s {device_serialb} shell input tap {x} {y}'
    print(f"执行的命令: {command}")
    os.system(command)


def routine(img_model_path, name, timeout=None):

    avg = get_xy(img_model_path, SCREENSHOT_MAIN, threshold=0.6)
    if avg:
        print(f'正在点击 {name}')
        adb_tap(avg[0], avg[1])
        return True
    time.sleep(4)


def routineb(img_model_path, name, threshold=0.6):

    avg = get_xyb(img_model_path, SCREENSHOT_MAIN, threshold=threshold)
    if avg:
        print(f'正在点击 {name}')
        adb_tapb(1280-avg[0], 720-avg[1])
        return True

    
while True:


    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\1bs.png",'一倍速')
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\ks.png",'开始')
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\djqx.png",'点击取消')
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\djqx3.png",'一倍速')
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\ct.png",'撤退')
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\djqx2.png",'撤退')
   
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\bx.png",'不行')
    routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\sq.png",'收起')
    time.sleep(12)
    #routineb(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\ks.png",'开始',)

