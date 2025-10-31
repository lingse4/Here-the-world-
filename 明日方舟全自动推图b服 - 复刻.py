from asyncio import Queue
from csv import reader
import ctypes
import os
import re
import socket
import subprocess
import sys
import time
import cv2
import numpy as np
import pyautogui
import threading
from pyminitouch.utils import str2byte
from pynput import keyboard
from paddleocr import PaddleOCR
import pygetwindow as gw
from minitouchdj import send_touch_command as dj
from mini_record import mini_record
from simulator_area_recognition_click import routineo
import subprocess
import os
import time


adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb.exe"
commands = [
    f"{adb_path} connect 127.0.0.1:16416",
    f"{adb_path} -s 127.0.0.1:16416 shell am start-foreground-service --user 0 -a jp.co.cyberagent.stf.ACTION_START -n jp.co.cyberagent.stf/.Service && {adb_path} -s 127.0.0.1:16416 forward tcp:1101 localabstract:stfservice",
    f"{adb_path} -s 127.0.0.1:16416 forward tcp:1091 localabstract:stfagent && {adb_path} -s 127.0.0.1:16416 shell pm path jp.co.cyberagent.stf && {adb_path} -s 127.0.0.1:16416 shell export CLASSPATH=\"package:/data/app/~~56jIni6IM7hPMTVWHLx4pA==/jp.co.cyberagent.stf-Q8kJLE1FdIcBrgJyIsEUiA==/base.apk\";exec app_process /system/bin jp.co.cyberagent.stf.Agent",
    f"{adb_path} -s 127.0.0.1:16416 shell chmod 755 /data/local/tmp/minitouch && {adb_path} -s 127.0.0.1:16416 shell /data/local/tmp/minitouch",
    f"{adb_path} -s 127.0.0.1:16416 forward tcp:1091 localabstract:minitouch"
]
# Define the CREATE_NO_WINDOW flag
CREATE_NO_WINDOW = 0x08000000

for i, command in enumerate(commands):
    subprocess.Popen(command, creationflags=CREATE_NO_WINDOW, shell=True)
    time.sleep(2)


SCREENSHOT_DIR = r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots"
SCREENSHOT_MAIN = os.path.join(SCREENSHOT_DIR, "main_screenshot.png")
SCREENSHOT_THREAD = os.path.join(SCREENSHOT_DIR, "thread_screenshot.png")
processed_texts = []
device_serial = "127.0.0.1:16416"  # 指定目标设备
PORT = 1091         # minitouch服务端口

ocr = PaddleOCR(use_angle_cls=True, lang='en',det_db_unclip_ratio=1.0)  # 这里可以选择不同的语言

# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""  # ADB 的完整路径
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接!请确认设备 {device_serial} 已开启USB调试模式")

# -------------------- 2. ADB截图函数 --------------------
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

def cv_imread(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在！")
        return None
    try:
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None
    
# -------------------- 3. ADB点击函数 --------------------
def adb_tap(x, y):
    """
    使用ADB命令模拟点击屏幕坐标 (x, y)
    """  # ADB 的完整路径
    x = int(x)
    y = int(y)
    command = f'"{adb_path}" -s {device_serial} shell input tap {x} {y}'
    print(f"执行的命令: {command}")
    os.system(command)

# -------------------- 6. adb返回键命令函数 --------------------
def adb_back():
    """使用ADB命令模拟返回键"""  # ADB 的完整路径
    command = f'"{adb_path}" -s {device_serial} shell input keyevent KEYCODE_ESCAPE'
    print(f"执行的命令: {command}")
    os.system(command)

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

    
    # -------------------- 5. 基于socket的minitouch点击函数 --------------------
def dj(x, y):
    """使用socket发送minitouch触摸指令(替换原ADB点击)"""
    HOST = '127.0.0.1'  # minitouch服务地址
    x = int(x)
    y = int(y)

    # 构造触摸指令（d:按下, w:等待, c:提交, u:抬起）
    # 注意：坐标顺序为y在前，x在后（根据你的模板调整）
    content = f"d 0 {720-y} {x} 50\nw 400\nc\nu 0\nc\n"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(str2byte(content))
    time.sleep(0.5)
    sock.shutdown(socket.SHUT_WR)

    res = ''
    while True:
        data = sock.recv(1024)
        if (not data):
            break
        res += data.decode()

    print(res)
    print('closed')
    sock.close()

def routine(img_model_path, name, timeout=None):
    while True:
        avg = get_xy(img_model_path, SCREENSHOT_MAIN)
        if avg:
            print(f'正在点击 {name}')
            dj(avg[0], avg[1])
            return True
        time.sleep(1)

def bring_window_to_front(window_title):
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"No window found with title: {window_title}")
            return
        
        window = windows[0]
        
        # 如果窗口是最小化的，则还原它
        if window.isMinimized:
            window.restore()
            print(f"Window '{window_title}' restored from minimized state.")
        
        # 将窗口置于前台
        window.activate()
        print(f"Window '{window_title}' brought to front.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def minimize_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.minimize()
        print(f"Window '{window_title}' minimized.")
    except IndexError:
        print(f"No window found with title: {window_title}")

def find_and_click_text(SCREENSHOT_MAIN, target_text):
    """
    截屏并检测目标文字，识别到后点击
    :param SCREENSHOT_MAIN: 截图保存路径
    :param target_text: 目标文字
    :return: 点击的坐标 (x, y)，如果未找到则返回 None
    """
    adb_screenshot(SCREENSHOT_MAIN)
    processed_path = preprocess_image(SCREENSHOT_MAIN)
    time.sleep(1)  # 等待截图保存完成
    results = reader.readtext(processed_path, detail=1, paragraph=False)  # 获取详细信息，包括坐标
    for (bbox, text, prob) in results:
        if target_text in text:
            print(f"找到目标文字 '{target_text}'，坐标: {bbox}")
            # 计算文字区域的中心点
            (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
            center_x = int((x_min + x_max) / 2)
            center_y = int((y_min + y_max) / 2)

            print(f"点击坐标: ({center_x}, {center_y})")
            dj(center_x, center_y)  # 点击中心点
            print(f"已点击目标文字 '{target_text}'")
            return center_x, center_y
    print(f"未找到目标文字 '{target_text}'")
    return None

def preprocess_image(image_path):
    """
    预处理图片以提高 OCR 识别率
    :param image_path: 图片路径
    :return: 图片路径（直接返回原路径，因为不再保存新的截图）
    """
    return image_path  # 直接返回原路径

def match_and_click(template_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    使用 OpenCV 模板匹配检测目标并点击
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值
    """
    while True:
        adb_screenshot(SCREENSHOT_MAIN)
        time.sleep(1)
        screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {SCREENSHOT_MAIN} 或 {template_path}")
            return False

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:  # 如果截图是 4 通道（带透明通道）
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)  # 转为 3 通道
        if template.shape[2] == 4:  # 如果模板是 4 通道（带透明通道）
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)  # 转为 3 通道

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 计算模板中心点
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2

            print(f"匹配成功，点击坐标: ({center_x}, {center_y})")
            dj(center_x, center_y)
            return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...") 

def wait_for_image(template_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    循环检测目标图片是否出现，不点击
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值
    :return: 是否检测到目标
    """
    while True:
        adb_screenshot(SCREENSHOT_MAIN)
        screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {SCREENSHOT_MAIN} 或 {template_path}")
            return False

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:  # 如果截图是 4 通道（带透明通道）
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)  # 转为 3 通道
        if template.shape[2] == 4:  # 如果模板是 4 通道（带透明通道）
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)  # 转为 3 通道

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            print(f"检测到目标图片: {template_path}")
            return True
        else:
            print(f"未检测到目标图片: {template_path}，继续检测...")
        time.sleep(1)


def match_and_click_with_retry(template_path, SCREENSHOT_MAIN, event_template_path, threshold=0.8, click_once=False, wait_before_click=0):
    """
    使用 OpenCV 模板匹配检测目标并点击，点击后验证是否成功
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param event_template_path: 点击后验证的事件图片路径
    :param threshold: 匹配阈值
    :param click_once: 是否只点击一次
    :param wait_before_click: 点击前等待的时间（秒）
    """
    clicked_once = False
    while True:
        # 截取全屏并匹配目标
        adb_screenshot(SCREENSHOT_MAIN)
        time.sleep(1)
        max_retries = 4
        retry_delay = 5  # 重试间隔时间（秒）
        for attempt in range(max_retries):
            # 尝试读取图像
            screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

            # 检查图片是否成功读取
            if screenshot is not None and template is not None:
                break
            else:
                print(f"第 {attempt + 1} 次尝试：无法读取图片: {SCREENSHOT_MAIN} 或 {template_path}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 计算模板中心点
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2

            print(f"匹配成功，点击坐标: ({center_x}, {center_y})")

            # 如果设置了只点击一次且已经点击过，则直接返回
            if click_once and clicked_once:
                print(f"目标 {template_path} 已点击一次，不再重复点击")
                return True

            # 等待指定时间后点击
            if wait_before_click > 0:
                print(f"等待 {wait_before_click} 秒后点击...")
                time.sleep(wait_before_click)

            dj(center_x, center_y)
            clicked_once = True
            time.sleep(1)  # 等待点击效果生效

            # 验证点击是否成功
            if event_template_path:
                while True:
                    adb_screenshot(SCREENSHOT_MAIN)
                    event_screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
                    event_template = cv2.imread(event_template_path, cv2.IMREAD_UNCHANGED)

                    if event_screenshot is None or event_template is None:
                        print(f"无法加载事件图片: {SCREENSHOT_MAIN} 或 {event_template_path}")
                        return False

                    # 确保事件图片和截图的通道一致
                    if event_screenshot.shape[2] == 4:
                        event_screenshot = cv2.cvtColor(event_screenshot, cv2.COLOR_BGRA2BGR)
                    if event_template.shape[2] == 4:
                        event_template = cv2.cvtColor(event_template, cv2.COLOR_BGRA2BGR)

                    # 执行事件图片匹配
                    event_result = cv2.matchTemplate(event_screenshot, event_template, cv2.TM_CCOEFF_NORMED)
                    _, event_max_val, _, _ = cv2.minMaxLoc(event_result)

                    if event_max_val >= threshold:
                        print(f"点击事件成功触发: {event_template_path}")
                        return True
                    else:
                        print(f"点击后未检测到事件图片: {event_template_path}，再次点击...")
                        dj(center_x, center_y)
                        time.sleep(1)  # 等待点击效果生效
            else:
                return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...")
time.sleep(1)

def detect_and_click_tg_and_s():
    """ 
    持续检测并点击 tg.png 和 s.png
    """
    print("开始循环检测并点击 'tg.png' 和 's.png'")
    while True:
        # 你可以在这里加点击或其它逻辑
        jq_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\tg.png", SCREENSHOT_THREAD, threshold=0.6)
        zcys_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\zcys.png", SCREENSHOT_THREAD, threshold=0.6)
        adb_screenshot(save_path=SCREENSHOT_THREAD)  # 使用全局常量路径
        if jq_coords:
            print("跳过剧情")
            dj(1183, 52)
            dj(720, 360)
            time.sleep(6)
            if jq_coords:
                print("跳过剧情")
                dj(1183, 52)
                dj(800, 450)
        if zcys_coords:
            print("至纯源石")
            dj(640,100)
        time.sleep(5)  # 每秒检测一次
    


def Clear_levels(name):

    time.sleep(1)
        # 第三步：全屏截图并匹配 s2.png
    adb_screenshot(SCREENSHOT_MAIN)  # 全屏截图
    start_coords = (1245,661)
    s2_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/s2.png", SCREENSHOT_MAIN)  # 匹配 s2.png
    if s2_coords:
        print("吃个药药")
        dj(s2_coords[0], s2_coords[1])  
        time.sleep(2)  # 等待 1 秒
        dj(start_coords[0], start_coords[1])
    else:
        print("启动！")

    time.sleep(2)
    start_coords = (1245,661)
    ks1_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/ks1.png", SCREENSHOT_MAIN)
    if ks1_coords:
        dj(start_coords[0], start_coords[1])  # 修复：确保 ks1_coords 已赋值
        print("磨难模式启动！")
    else:
        print("还没有到磨难模式")

    # 后续步骤：使用 OpenCV 模板匹配检测并点击，验证点击事件
    print("检测并点击 '助战干员'")
    match_and_click_with_retry(
        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/zz.png",
        SCREENSHOT_MAIN,
        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/jr.png"
    )

    dj(56,203)  # 使用第一步的点击坐标

    jr_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/jr.png", SCREENSHOT_MAIN, threshold=0.6)
    while True:
        adb_screenshot(SCREENSHOT_MAIN)
        if jr_coords:
            dj(jr_coords[0],jr_coords[1])  # 使用第一步的点击坐标
            break

    print("检测并点击 '招募助战'")
    match_and_click_with_retry(
        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/zm.png",
        SCREENSHOT_MAIN,
        None,  # 无需验证事件
        click_once=True  # 只点击一次
    )

    time.sleep(3)  # 等待 1 秒
    dj(1099, 505)  # 使用第一步的点击坐标
    print("点击坐标: (1099, 505)")

    # 第四步：全屏截图并匹配 s1.png
    adb_screenshot(SCREENSHOT_MAIN)  # 全屏截图
    s1_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/s1.png", SCREENSHOT_MAIN)  # 匹配 s1.png
    if s1_coords:
        print(f"确认ban位")
        dj(s1_coords)  # 点击 s1.png 的位置
    else:
        print("下一步")

    
        # 第七步：检测并点击 "暂停"
    print("部署干员")  
    while True:
        onebs_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/1bs.png", SCREENSHOT_MAIN)    
        if onebs_coords:
            mini_record(r"C:\Users\Administrator\Desktop\Matcha Parfait/mouse_operations.txt",PORT)
            break
    time.sleep(25)  # 等待 25 秒     
    # 第五步：检测并点击 "1倍速"
    print("检测并点击 '1倍速'")
    match_and_click_with_retry(
        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/1bs.png",
        SCREENSHOT_MAIN,
        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/2bs.png"
    )

    # 第六步：等待 "2倍速" 出现
    print("等待 '2倍速' 出现")
    wait_for_image(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/2bs.png", SCREENSHOT_MAIN)

    time.sleep(35)

    # 第八步：检测并点击 "行动结束"
    print("检测并点击 '行动结束'")
    match_and_click_with_retry(
        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/xd.png",
        SCREENSHOT_MAIN,
        None,  # 最后一步无需验证事件
        click_once=True,  # 点击一次
        wait_before_click=2  # 点击前等待 2 秒
    )
    print(f"{name} 结束")
    return False

def process_stage(SCREENSHOT_MAIN, max_retries):
    """rightmost_entry
    处理游戏关卡流程的主函数
    :param SCREENSHOT_MAIN: 截图存储路径
    :param max_retries: 最大重试次数
    :return: True表示流程成功完成，False表示失败
    """
    # 关键坐标定义
    START_COORDS = (1245, 661)
    COMMON_TAP_POINTS = {
        'story': (977, 368),      # 剧情关卡坐标
        'confirm': (640, 360),    # 通用确认坐标
        'exercise': (1085, 500),  # 演习确认坐标
        'close': (208, 217)       # 关闭按钮坐标
    }
    
    # 图像模板路径配置
    TEMPLATE_PATHS = {
        'yx': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/yx.png",
        'ys': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/ys.png",
        'txms': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/txms.png",
        'ksjq': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/ksjq.png",
        'jzyx': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/jzyx.png",
        'xd': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/xd.png",
        '代理': r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/代理.png"
    }

    for attempt in range(max_retries):
        try:
            # 图像匹配检测
            coords = get_xy(TEMPLATE_PATHS['yx'], SCREENSHOT_MAIN, threshold=0.8)
            coords1 = get_xy(TEMPLATE_PATHS['ys'], SCREENSHOT_MAIN, threshold=0.8)
            txms_coords = get_xy(TEMPLATE_PATHS['txms'], SCREENSHOT_MAIN, threshold=0.7)
            coords2 = get_xy(TEMPLATE_PATHS['ksjq'], SCREENSHOT_MAIN)
            coords3 = get_xy(TEMPLATE_PATHS['jzyx'], SCREENSHOT_MAIN, threshold=0.7)
            代理 = get_xy(TEMPLATE_PATHS['代理'], SCREENSHOT_MAIN, threshold=0.7)

            def record_thread_func(stop_event):
                last_record_time = 0
                while not stop_event.is_set():
                    now = time.time()
                    if now - last_record_time >= 28:
                        mini_record(r"C:\Users\38384\Desktop\Matcha Parfait\mouse_operations.txt", PORT)
                        last_record_time = now

            def detect_thread_func(stop_event):
                while not stop_event.is_set():
                    if wait_for_image(TEMPLATE_PATHS['xd'], SCREENSHOT_MAIN):
                        print("检测到operation图片,已终止mini_record")
                        stop_event.set()
                        break
                    time.sleep(1)

            # 普通关卡处理流程
            if coords:
                print("[流程] 检测到普通关卡")
                if 代理:
                    print("[状态] 有代理")
                    time.sleep(0.5)
                    dj(*代理)
                    dj(*START_COORDS)
                    time.sleep(1)
                    print("[操作] 进入普通关卡")
                    s2_coords = get_xy(r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/s2.png", SCREENSHOT_MAIN)  # 匹配 s2.png
                    start_coords = (1245,661)
                    if s2_coords:
                        print("吃个药药")
                        dj(s2_coords[0], s2_coords[1])  
                        time.sleep(2)  # 等待 1 秒
                        dj(start_coords[0], start_coords[1])
                    else:
                        print("启动！")
                    time.sleep(2)
                    dj(1099, 505)  
                    print("点击坐标: (1099, 505)")
                    print("检测并点击 '行动结束'")
                    match_and_click_with_retry(
                        r"C:\Users\Administrator\Desktop\Matcha Parfait/Pictures/Screenshots/xd.png",
                        SCREENSHOT_MAIN,
                        None,  # 最后一步无需验证事件
                        click_once=True,  # 点击一次
                        wait_before_click=2  # 点击前等待 2 秒
                    )
                    return True
                else:
                    print("没代理")
                    dj(*START_COORDS)
                    print("[操作] 进入突袭关卡")
                    if not Clear_levels("突袭关卡"):
                        return True


            # 剧情关卡处理流程
            if coords2:
                print("[流程] 检测到剧情关卡")
                dj(*COMMON_TAP_POINTS['story'])
                print("[操作] 进入剧情关卡")
                time.sleep(5)
                dj(*COMMON_TAP_POINTS['confirm'])
                time.sleep(20)
                dj(*COMMON_TAP_POINTS['confirm'])
                time.sleep(2)
                dj(640,100)
                return "特殊关卡"

            # 演习关卡处理流程
            if coords3:
                print("[流程] 检测到演习关卡")
                if coords1:
                    print("[状态] 没打")
                    dj(*START_COORDS)
                    time.sleep(1)
                    dj(*COMMON_TAP_POINTS['exercise'])
                    print("[操作] 进入演习关卡")

                    stop_event = threading.Event()
                    t1 = threading.Thread(target=record_thread_func, args=(stop_event,))
                    t2 = threading.Thread(target=detect_thread_func, args=(stop_event,))
                    t1.start()
                    t2.start()
                    t1.join()
                    t2.join()

                    time.sleep(28)
                    dj(603, 442)
                    return "特殊关卡"
            # 未匹配到任何有效关卡
            if attempt == max_retries - 1:
                print("[错误] 已达到最大重试次数")
                return True

            print(f"[重试] 第 {attempt+1} 次重试...")
            time.sleep(1)

        except Exception as e:
            print(f"[异常] 流程执行出错: {str(e)}")
            if attempt == max_retries - 1:
                return True
            time.sleep(2)

def main_process():
    """
    主流程逻辑
    """
    print("开始主流程...")

    # 检查ADB连接
    check_adb_connection()

    adb_screenshot(save_path=SCREENSHOT_MAIN)
    
    img = cv2.imread(SCREENSHOT_MAIN)
        
# 合并匹配规则：同时匹配 13-14 和 TR-15 格式
    pattern = r'^([A-Za-z]{1,})?(\d+|[A-Za-z]{1,})(-[A-Za-z]{1,2})?-\d+$' # 前段允许数字/字母，后段必须数字
    
    # 执行OCR并过滤
    filtered = []
    matched_texts = []
    matched_texts0 = []

    result = ocr.ocr(img)

    rec_texts = result[0]["rec_texts"]
    rec_boxes = result[0]["rec_boxes"]

    filtered = list(zip(rec_texts, rec_boxes))

    filtered.sort(key=lambda x: x[1][0], reverse=False)
    print(f"文本: {filtered}")
    for item in filtered:
        if re.match(pattern, item[0]):
            matched_texts.append(item)
            print(f"匹配成功: {item[0]}")
        else:
            print(f"不匹配: {item[0]}")

    for item2 in matched_texts:
        
        time.sleep(2)
        print(f"文本666")
    
        adb_screenshot(save_path=SCREENSHOT_MAIN)

        new_img = cv2.imread(SCREENSHOT_MAIN)

        new_results = ocr.ocr(new_img)

        new_rec_texts = new_results[0]["rec_texts"]
        new_rec_boxes = new_results[0]["rec_boxes"]

        new_results = list(zip(new_rec_texts, new_rec_boxes))

        new_results.sort(key=lambda x: x[1][0], reverse=False)

        for item0 in new_results:
            if re.match(pattern, item0[0]):
                matched_texts0.append(item0)

            
        if item2[0] in processed_texts:
            continue
        new_bbox = next((item1[1] for item1 in matched_texts0 if item1[0] == item2[0]), None)

        if new_bbox is not None:
            print(f"新坐标: {str(new_bbox)}")
            print(f"文本: {item2[0]}")

            # 计算 x 坐标的平均值
            x_center = (abs(new_bbox[0]) + abs(new_bbox[2]))/2

            # 计算 y 坐标的平均值
            y_center = (abs(new_bbox[1]) + abs(new_bbox[3]))/2
            
            print(f"坐标: {new_bbox[0]}{new_bbox[1]}{new_bbox[2]}{new_bbox[3]}")
            print(f"坐标: ({x_center}, {y_center})")
            print(matched_texts0)
            dj(x_center, y_center)
            print(f"执行点击")
            
            result = process_stage(SCREENSHOT_MAIN, max_retries=3)
            if result == "特殊关卡":
                print(f"√ {item2[0]} 验证成功")
                processed_texts.append(item2[0])
                adb_tap(640,1)
                time.sleep(2)
                continue

            elif result:
                print(f"√ {item2[0]} 验证成功")
                print("点击 '返回' 按钮")
                processed_texts.append(item2[0])
                adb_tap(640,1)
                time.sleep(2)
                continue
            else:
                print("再来一次！")

                time.sleep(13)

                new_img = adb_screenshot()

                new_results = ocr.ocr(new_img)

                new_rec_texts = new_results[0]["rec_texts"]
                new_rec_boxes = new_results[0]["rec_boxes"]

                new_results = list(zip(new_rec_texts, new_rec_boxes))

                new_results.sort(key=lambda x: x[1][0], reverse=False)
                
                for item1 in new_results:

                    if item1[0] == item2[0]:
                        
                        new_bbox = item1[1]
                        print(f"新坐标: {str(new_bbox)}")

                        # 计算 x 坐标的平均值
                        x_center = sum([new_bbox[0] + new_bbox[2]])/2

                        # 计算 y 坐标的平均值
                        y_center = sum([new_bbox[1] + new_bbox[3]])/2

                        print(f"坐标: ({x_center}, {y_center})")
                        print(matched_texts0)
                        dj(x_center, y_center)
                        process_stage(SCREENSHOT_MAIN, max_retries=3)
                        adb_tap(640,1)
                        time.sleep(2)
                        continue
        else:
            print(f"未找到与 {item2[0]} 匹配的bbox,跳过。")
            continue

if __name__ == "__main__":
    # 启动独立线程进行循环检测
    detection_thread = threading.Thread(target=detect_and_click_tg_and_s, daemon=True)
    detection_thread.start()

    # 主流程循环
    while True:
        print("开始新一轮主流程...")
        main_process()
        print("主流程完成，等待 6 秒后重新开始...")
        time.sleep(6)  # 等待 7 秒后重新开始