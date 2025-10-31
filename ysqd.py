import getpass
import json
import cv2
import pyautogui
import time
import os
import sys
import ctypes
import numpy as np
import subprocess
import pygetwindow as gw
import psutil
import sys
import win32com
import win32gui
import win32con
import ruamel.yaml
from account_manager import import_account, save_account_name, gamereg_export, btsave_account_name, get_uid
from window_screenshot import window_screenshot
from paddleocr import PaddleOCR
from OCR import ocr_image
import re
from Window_btscreenshot import window_btscreenshot
from output_capture import gotta_clue
from Djjr import djjr

pyautogui.FAILSAFE = False  # 警告：关闭安全保护，风险自负!
ocr = PaddleOCR(use_angle_cls=True, lang='en',det_db_unclip_ratio=1.0)  

# 常量定义
BT_PATH = r"D:\BaiduNetdiskDownload\March7thAssistant_v2025.4.18_full\March7th Launcher.exe"
YS_PATH = r"D:\BetterGI\BetterGI\BetterGI.exe"
BT_PATH1 = r"D:\miHoYo Launcher\games\Star Rail Game\StarRail.exe"
YS_PATH1 = r"D:\miHoYo Launcher\games\Genshin Impact Game\YuanShen.exe"
YS_PATHB = r"C:\Users\Administrator\Desktop\网瘾少女\YuanShen.lnk"
ZY_PATH = r"D:\BaiduNetdiskDownload\远程本地多用户桌面1.19r\远程本地多用户桌面1.19r\SimpleRemote.exe"
lingse = r"C:\Users\Administrator\Desktop\Remote_Desktop_Connect\lingse.rdp"
lingse1 = r"C:\Users\Administrator\Desktop\Remote_Desktop_Connect\lingse1.rdp"
lingse2 = r"C:\Users\Administrator\Desktop\Remote_Desktop_Connect\lingse2.rdp"
lingse3 = r"C:\Users\Administrator\Desktop\Remote_Desktop_Connect\lingse3.rdp"
lingse4 = r"C:\Users\Administrator\Desktop\Remote_Desktop_Connect\lingse4.rdp"
dc = "./Pictures/dc.png"
dc1 = "./Pictures/dc1.png"
tc1 = "./Pictures/tc1.png"
sj1 = "./Pictures/sj1.png"
jryx1 = "./Pictures/jryx1.png"
tc = "./Pictures/tc.png"
sj = "./Pictures/sj.png"
jryx = "./Pictures/jryx.png"
ksyx = "./Pictures/ksyx.png"
djjr1 = "./Pictures/djjr.png"
yx1 = "./Pictures/yx1.png"
ty = "./Pictures/ty.png"
qhzh = "./Pictures/qhzh.png"
dq = "./Pictures/dq.png"
qd = "./Pictures/qd.png"
xf = "./Pictures/xf.png"
ty1 = "./Pictures/ty1.png"
pm = "./Pictures/pm.png"
zf = "./Pictures/zf.png"
mys = "./Pictures/mys.png"
BT_BUTTON_1 = "./Pictures/wzyx.png"
IMAGE_PATH_DONE = "./Pictures/ahcjg.png"
ytl_BUTTON_1 = "./Pictures/ytl.png"
ysqd_BUTTON_2 = "./Pictures/ysqd.png"
IMAGE_PATH_DONE_1 = "./Pictures/jrjlylq.png"
BT_TITLE = "March7th Assistant"
BT_TITLE1 = "崩坏：星穹铁道"
YS_TITLE = "更好的原神"
YS_TITLE1 = "原神"
ZY_TITLE = "GlowWindow"

namebox = []
nameboxb = []
btnamebox = []
n = [1,2,3]




ysjson = r"D:\BetterGI\BetterGI\User\config.json"
btjson = r"D:\BaiduNetdiskDownload\March7thAssistant_v2025.4.18_full\config.yaml"



# ------------------------ 核心功能函数 ------------------------

def start_application(app_path):
    try:
        subprocess.Popen(app_path, shell=True)
    except Exception as e:
        raise RuntimeError(f"启动应用失败：{e}")

def close_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print(f"已关闭窗口 (句柄: {hwnd})")
        return True
    except Exception as e:
        print(f"关闭失败 (句柄: {hwnd}): {str(e)}")
        return False


def close_window_gw(window_name):
    """使用pygetwindow(gw)库关闭指定标题的窗口
    
    Args:
        window_name: 窗口标题字符串
        
    Returns:
        bool: 操作是否成功
    """
    try:
        # 获取所有匹配标题的窗口
        windows = gw.getWindowsWithTitle(window_name)
        
        if not windows:
            print(f"未找到标题为 '{window_name}' 的窗口")
            return False
        
        # 处理找到的第一个窗口
        window = windows[0]
        
        # 如果窗口最小化，先还原
        if window.isMinimized:
            window.restore()
            time.sleep(0.5)  # 给系统一点时间响应
        
        # 关闭窗口
        window.close()
        print(f"已使用gw方法关闭窗口：{window_name}")
        return True
        
    except Exception as e:
        print(f"使用gw方法关闭窗口时出错：{e}")
        return False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        print("wsm")
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    else:
        print("已管理员权限运行")

def cv_imread(file_path):
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

def get_xy(img_model_path, threshold=0.7):
    screenshot_dir = "./screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    pyautogui.screenshot().save(screenshot_path)
    
    img = cv_imread(screenshot_path)
    img_terminal = cv2.imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)

    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

def auto_click(var_avg):
    if var_avg:
        pyautogui.click(var_avg[0], var_avg[1], duration=0)

def routine(img_model_path, name, timeout=None, threshold=0.7):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path, threshold=threshold)  # 将阈值从默认的 0.7 降低到 0.6
        if avg:
            print(f'正在点击 {name}')
            print(avg)
            auto_click(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
        time.sleep(1)

def routinesj(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path, threshold=0.8)  # 将阈值从默认的 0.7 降低到 0.6
        if avg:
            print(f'正在点击 {name}')
            avg = (avg[0], avg[1]+250)
            auto_click(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
        time.sleep(1)

def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")

def is_process_running(process_name):
    """检查指定进程是否正在运行"""
    for proc in psutil.process_iter(['name']):
        print(proc.info['name'])
        if proc.info['name'] == process_name:
            return True
    return False

def change_json(key,value):
    with open(ysjson, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 修改 JSON 数据
    # 假设 JSON 文件内容是一个字典，我们修改其中的某个键值对

    data[key] = value
    print(f'修改 {key} 为 {value}')

    # 将修改后的数据写回 JSON 文件
    with open(ysjson, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("JSON 文件已修改。")

def change_json_bt(value,value1):
    try:
        # 使用ruamel.yaml.YAML类来保留注释和格式
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        
        # 读取YAML文件，保留注释和格式
        with open(btjson, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
        
        # 修改instance_type值

        data["instance_names"]["拟造花萼（赤）"] = value1
        data["instance_type"] = value
        print(f'修改为 {value}')
        
        # 写入文件，保持原始格式和注释
        with open(btjson, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        print("YAML 文件已修改（保留注释和格式）。")
        return True
    except Exception as e:
        print(f"修改YAML文件时出错：{e}")
        return False


def set_window_foreground(window_title):
    """将指定标题的窗口置顶并聚焦"""
    try:
        # 尝试使用pygetwindow获取窗口
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            hwnd = window._hWnd  # 获取窗口句柄
            
            # 使用Windows API设置窗口为前台
            # 首先显示窗口（如果最小化）
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # 设置为前台窗口
            win32gui.SetForegroundWindow(hwnd)
            # 额外步骤：发送一个Alt键按下和释放事件，确保窗口真正获得焦点
            win32gui.keybd_event(0x12, 0, 0, 0)  # Alt键按下
            win32gui.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt键释放
            
            print(f"已成功激活窗口：{window_title}")
            return True
        else:
            print(f"未找到标题为 '{window_title}' 的窗口")
            return False
    except Exception as e:
        print(f"激活窗口时出错：{e}")
        return False
    
def maximize_window_to_fullscreen(window_title):
    """将指定标题的窗口最大化到全屏模式"""
    try:
        # 获取所有匹配标题的窗口
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"未找到标题为 '{window_title}' 的窗口")
            return False
        
        pyautogui.hotkey('win', 'up')  # Win+Up 快捷键最大化窗口
        
        print(f"已成功将窗口 '{window_title}' 设置为全屏")
        return True
    except Exception as e:
        print(f"设置窗口全屏时出错：{e}")
        return False


def ys():

    print(111)

    while True:
        
        if len(namebox) == 3:
            print("退出")
            break
            
        print("111")

        start_application(YS_PATH1)

        print("222")
        while not get_xy(tc1):
            print("111")
            if get_xy(jryx1, threshold=0.9):
                routine(jryx1, "jryx1", threshold=0.9)
            if get_xy(ty1, threshold=0.9):
                routine(ty1, "ty1", threshold=0.9)
            if get_xy(dc1, threshold=0.7):
                routine(dc1, "dc1")

        routine(tc1, "tc1")
        time.sleep(1)
        if get_xy(sj1, threshold=0.7):
            routine(sj1, "sj1")
            avg = get_xy(sj1, threshold=0.7)
            avg = (avg[0], avg[1]+287)
        elif get_xy(yx1, threshold=0.7):
            routine(yx1, "yx1")
            avg = get_xy(yx1, threshold=0.7) 
            avg = (avg[0], avg[1]+287)
        else:
            routine(mys, "mys")
            avg = get_xy(mys, threshold=0.7) 
            avg = (avg[0], avg[1]+287)
        time.sleep(1)
        auto_click(avg)
        time.sleep(1)
        routine(jryx1, "jryx1")
        global xhdjjr
        xhdjjr = False
        while True:
            djjr("原神")
            result = ocr_image(r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png")
            rec_texts = result[0]["rec_texts"]
            for item in rec_texts:
                if item == "点击进入":
                    auto_click(avg)
                    xhdjjr = True
                    break
            if xhdjjr == True:
                break
        
        while True:
            if get_xy(pm, threshold=0.8):
                window_screenshot("原神")
                break
            if get_xy(zf, threshold=0.8):
                window_screenshot("原神")
                break


        result = ocr_image(r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png")
        #print(result)
        rec_texts = result[0]["rec_texts"]
        #pattern = r'^\d{3}\*+(\d{2}|\d\*\d)$'

        with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for name in data:
                uid = data[name]["uid"]
                ysconfig = data[name]["ysconfig"]
                user = data[name]["user"]
                print(f'当前账号: {name}, UID: {uid}, 配置: {ysconfig}, 用户: {user}')
                if name in namebox:
                    print(f'已处理账号: {name}{namebox}')
                    continue
                
                if user == getpass.getuser():
                    print(user)
                    print(rec_texts[0])
                    print(rec_texts)
                    if rec_texts[-1][-3:] == uid[-3:]:
                        namebox.append(name)

                        #import_account(uid)
                        change_json("selectedOneDragonFlowConfigName",ysconfig)

        start_application(YS_PATH)
        routine(ytl_BUTTON_1, "ytl", threshold=0.8)
        routine(ysqd_BUTTON_2, "ysqd", threshold=0.8)
        print("等待 200 秒后重试...")
        time.sleep(200)   
        while is_process_running("YuanShen.exe"):
            print("YuanShen.exe 仍在运行，等待 30 秒后重试...")
            time.sleep(30)
        #btsave_account_name(user, name, ysconfig, key)    

def ysb():

    print("b服")

    while True:

        if len(nameboxb) == 3:
            print("退出")
            break
        
        print("111")

        start_application(YS_PATHB)

        while not get_xy(qd, threshold=0.9):
            if get_xy(dc1, threshold=0.6):
                print("找到dc1")
                routine(dc1, "dc1", threshold=0.6)

            if get_xy(ty, threshold=0.9):
                print("找到ty")
                routine(ty, "ty", threshold=0.9)

            if get_xy(dq, threshold=0.9):
                print("找到dq")
                routine(dq, "dq", threshold=0.9)
        print("分界点")
        avg = get_xy(dc1, threshold=0.6) 
        print(avg)
        routine(qd, "qd", threshold=0.9)
        while True:
            if get_xy(dq, threshold=0.9):
                avg1 = ((avg[0]-519, avg[1]-601))
                avg2 = ((avg[0]-1200, avg[1]-158))
                auto_click(avg1)
                time.sleep(1)
                auto_click(avg2)
                routine(dq, "dq")
                break
        global xhdjjr
        xhdjjr = False
        while True:
            djjr("原神")
            result = ocr_image(r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png")
            rec_texts = result[0]["rec_texts"]
            for item in rec_texts:
                if item == "点击进入":
                    auto_click(avg1)
                    xhdjjr = True
                    break
            if xhdjjr == True:
                break

        while True:
            if get_xy(pm, threshold=0.8):
                window_screenshot("原神")
                break
            if get_xy(zf, threshold=0.8):
                window_screenshot("原神")
                break

        result = ocr_image(r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png")
        #print(result)
        rec_texts = result[0]["rec_texts"]
        #pattern = r'^\d{3}\*+(\d{2}|\d\*\d)$'

        with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for name in data:
                uid = data[name]["uid"]
                ysconfig = data[name]["ysconfig"]
                user = data[name]["user"]
                print(f'当前账号: {name}, UID: {uid}, 配置: {ysconfig}, 用户: {user}')
                if name in namebox:
                    print(f'已处理账号: {name}{namebox}')
                    continue
                
                if user == (getpass.getuser()+"b"):
                    print(user)
                    print(rec_texts[-1])
                    print(rec_texts[-1][-3:])
                    if rec_texts[-1][-3:] == uid[-3:]:
                        nameboxb.append(name)

                        #import_account(uid)
                        change_json("selectedOneDragonFlowConfigName",ysconfig)

        start_application(YS_PATH)
        routine(ytl_BUTTON_1, "ytl", threshold=0.8)
        routine(ysqd_BUTTON_2, "ysqd", threshold=0.8)
        print("等待 200 秒后重试...")
        time.sleep(200)   
        while is_process_running("YuanShen.exe"):
            print("YuanShen.exe 仍在运行，等待 30 秒后重试...")
            time.sleep(30)
        #btsave_account_name(user, name, ysconfig, key)    


def bt():
    while True:

        print(btnamebox)
        if len(btnamebox) == 3:
            print("退出")
            break

        #import_account(uid)
        start_application(BT_PATH1)
        while not get_xy(tc, threshold=0.7):
            if get_xy(dc, threshold=0.7):
                print("找到dc")
                routine(dc, "dc")
            if get_xy(jryx, threshold=0.7):
                print("找到jryx")
                routine(jryx, "jryx")
        time.sleep(2)
        avg = get_xy(tc, threshold=0.7) 
        routine(tc, "tc")
        avg1 = ((avg[0]- 336, avg[1]- 213))
        avg2 = ((avg[0]- 374, avg[1]+40))
        time.sleep(1)
        auto_click(avg1)
        time.sleep(1)
        auto_click(avg2)
        routine(jryx, "jryx")
        time.sleep(3)
        auto_click(avg1)
        routine(djjr1, "djjr")
        time.sleep(7)

        #window_btscreenshot("崩坏：星穹铁道")

        #result = ocr_image(r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png")
        #print(result)
        #rec_texts = result[0]["rec_texts"]
        #pattern = r'^\d{3}\*+(\d{2}|\d\*\d)$'

        with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\btconfig.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for name in data:
                uid = data[name]["uid"]
                user = data[name]["user"]
                value = data[name]["instance_type"]
                value1 = data[name]["instance_names"]
                print(f'当前账号: {name}, UID: {uid}, 配置: {value}, 用户: {user}',value1)
                if name in namebox:
                    print(f'已处理账号: {name}{namebox}')
                    continue
                
                if user == getpass.getuser():

                    print(user)
                    print(uid,get_uid())
                    #print(rec_texts[0])
                    #print(rec_texts)
                    if str(get_uid()) == uid:
                        print(uid)
                        btnamebox.append(name)

                        #import_account(uid)
                        change_json_bt(value,value1)
            
        #start_application(BT_PATH)
        #routine(BT_BUTTON_1, "完整运行")
        gotta_clue()
        close_window_gw("崩坏：星穹铁道")

        
        #print("等待 200 秒后重试...")
        #time.sleep(200)   
        #while is_process_running("StarRail.exe"):
            #print("StarRail.exe 仍在运行，等待 30 秒后重试...")
            #time.sleep(30)
        #time.sleep(10)
        #btsave_account_name(user, name, value, va
        # lue1)

users = [lingse,lingse1,lingse2,lingse3,lingse4]
username = ["lingse","lingse1","lingse2","lingse3","lingse4"]

i = [2,3,4,5,6]

def account_cycle():
    for user,username,i in zip(users,username,i):
        start_application(user)
        time.sleep(2)
        start_application(fr'psexec -i {i} -u {username} -p 107881 cmd.exe /k "C:\\Python313\\python.exe C:\Users\lingse\Desktop\ysqd.py || echo 脚本执行出错！错误码：%errorlevel% & pause"')
        while True:
            result = subprocess.run(
            "cmd.exe /c query session", 
            shell=True, 
            text=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=10  # 设置超时时间防止命令卡住
        )

            # 打印命令输出
            print(f"命令输出:{result.stdout}")
            lines = result.stdout.strip().split('\n')
            print(lines[i+1])
            if "断开" in lines[i+1]:
                print("账号已断开")
                break
            time.sleep(60)
            


if __name__ == '__main__':
    
    print(getpass.getuser())
    run_as_admin()
    #start_application(lingse)
    time.sleep(2)
    if "Administratorb" == getpass.getuser():
        if 1 in n:
            ys()
        if 2 in n:
            ysb()
        if 3 in n:
            bt()
        account_cycle()
    else:
        for username,i in zip(username,i):
            if getpass.getuser() == username:
                if 1 in n:
                    ys()
                if 2 in n:
                    ysb()
                if 3 in n:
                    bt()
                start_application(fr'psexec -i {i} -u {username} -p 107881 cmd.exe /k "shutdown /l"')
