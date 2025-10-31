import os
import time
from fzdef import check_adb_connection,adb_screenshot,routine

SCREENSHOT_DIR = r"C:\Users\38384\Pictures\Screenshots"
SCREENSHOT_MAIN = os.path.join(SCREENSHOT_DIR, "main_screenshot.png")
adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"
device_serial = "127.0.0.1:16416"  # 指定目标设备
password = "1078813860"
password = ""

check_adb_connection()
adb_screenshot(SCREENSHOT_MAIN)

command = "adb -s 127.0.0.1:16384 shell am start -n com.hypergryph.arknights.bilibili/com.u8.sdk.U8UnityContext"
os.system(command)

routine(r"C:\Users\38384\Pictures\Screenshots\START.png", "START")
routine(r"C:\Users\38384\Pictures\Screenshots\账户管理.png", "账号管理")
routine(r"C:\Users\38384\Pictures\Screenshots\登求其他账号.png", "登求其他账号")
routine(r"C:\Users\38384\Pictures\Screenshots\密码登求.png", "密码登求")
routine(r"C:\Users\38384\Pictures\Screenshots\请输入账号.png", "请输入账号")
# 替换原剪贴板操作：使用 adb 直接输入账号
account = "18176782840"
input_account_cmd = f"{adb_path} -s {device_serial} shell input text {account}"
os.system(input_account_cmd)
routine(r"C:\Users\38384\Pictures\Screenshots\请输入密码.png", "请输入密码")
input_password_cmd = f"{adb_path} -s {device_serial} shell input text {password}"
os.system(input_password_cmd)
routine(r"C:\Users\38384\Pictures\Screenshots\圆圈.png", "圆圈")
routine(r"C:\Users\38384\Pictures\Screenshots\登录.png", "登录")




