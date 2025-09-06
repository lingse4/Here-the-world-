import os
import time
from fzdef import check_adb_connection,adb_screenshot,routine
import pyautogui
import pyperclip
from Arknights_Auto_Map_Progressing_Official_Server import device_serial,main_process,detection_thread

SCREENSHOT_DIR = r"C:\Users\38384\Pictures\Screenshots"
SCREENSHOT_MAIN = os.path.join(SCREENSHOT_DIR, "main_screenshot.png")
adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"

check_adb_connection()

import os

# 账号密码列表 - 可以添加多个账号
accounts = [
    {'username': '账号1', 'password': '密码1'},
    {'username': '账号2', 'password': '密码2'},
    # 继续添加更多账号...
]

# 逐个处理每个账号
for account in accounts:
    username = account['username']
    password = account['password']
    print(f"正在处理账号: {username}")
    
    adb_screenshot(SCREENSHOT_MAIN)

    command = "adb -s " + device_serial + " shell am start -S -n com.hypergryph.arknights/com.u8.sdk.U8UnityContext"
    os.system(command)

    routine(r"C:\Users\38384\Pictures\Screenshots\START.png", "START")
    routine(r"C:\Users\38384\Pictures\Screenshots\账户管理.png", "账号管理")
    routine(r"C:\Users\38384\Pictures\Screenshots\登求其他账号.png", "登求其他账号")
    routine(r"C:\Users\38384\Pictures\Screenshots\密码登求.png", "密码登求")
    routine(r"C:\Users\38384\Pictures\Screenshots\请输入账号.png", "请输入账号")
    # 替换原剪贴板操作：使用 adb 直接输入账号

    input_account_cmd = f"{adb_path} -s {device_serial} shell input text {username}"
    os.system(input_account_cmd)
    time.sleep(1)  # 等待输入完成

    routine(r"C:\Users\38384\Pictures\Screenshots\请输入密码.png", "请输入密码")

    input_password_cmd = f"{adb_path} -s {device_serial} shell input text {password}"
    os.system(input_password_cmd)
    time.sleep(1)  # 等待输入完成
    routine(r"C:\Users\38384\Pictures\Screenshots\圆圈.png", "圆圈")
    routine(r"C:\Users\38384\Pictures\Screenshots\登录.png", "登录")




