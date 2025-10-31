import re
import subprocess
import sys
import threading
import time
from paddleocr import PaddleOCR
from qywxftp import send_image_to_wechat_robot
from ysqd import routine
from keyboard import press_and_release
from Window_btscreenshot import window_btscreenshot 
from threading import Lock

global_output = []  # 存储外部程序的输出
global_output_lock = Lock()  # 保护全局输出的锁
process_running = True  # 标记外部进程是否在运行
ocr = PaddleOCR(use_angle_cls=True, lang='en',det_db_unclip_ratio=1.0)  

def capture_cmd_output_advanced(cmd, shell=True, show_output=True):

    global process_running

    try:
        # 创建进程，重定向标准输出和错误输出
        process = subprocess.Popen(
            cmd, 
            shell=shell, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,  # 合并标准错误到标准输出
            text=True, 
            bufsize=1
        )
        
        output_lines = []
        # 实时读取输出并显示
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line)
                with global_output_lock:
                    global_output.append(line)
                if show_output:
                    print(line, end='')  # 不自动添加换行符，因为line已经包含
        
        process.stdout.close()
        process.wait()
        
        return {
            'success': process.returncode == 0,
            'output': ''.join(output_lines),
            'error': '',
            'return_code': process.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'return_code': -1
        }

# 定义一个函数，用于在线程中执行正则匹配和后续操作
def monitor_winotify_notification(current_output):
    """
    在线程中监控winotify通知完成的消息
    """
    # 定义正则表达式模式
    flexible_pattern = re.compile(
        r'.*winotify\s+通知发送完成', 
        re.IGNORECASE
    )

    while process_running:
        time.sleep(5)  # 短暂休眠以避免CPU占用过高

        # 获取当前的输出内容进行检查
        current_output = ''
        with global_output_lock:
            current_output = ''.join(global_output)

        # 检查是否匹配到目标文本
        if flexible_pattern.search(current_output):
            print("成功捕获到winotify通知相关提示!")
            press_and_release("Escape")
            time.sleep(2)   
            press_and_release("F4")
            routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\mrsx.png","每日实训")
            time.sleep(2)
            window_btscreenshot("崩坏：星穹铁道")
             # 替换为你的企业微信机器人Webhook地址
            WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=949cfed3-6a47-4bcd-baf5-582d6e8b79df"
    
             # 替换为你要发送的图片路径
            IMAGE_PATH = r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png"
    
            # 发送图片
            send_image_to_wechat_robot(WEBHOOK_URL, IMAGE_PATH)

            press_and_release("Enter")
            break


# 使用示例
def gotta_clue():


        # 创建并启动监控线程
    monitor_thread = threading.Thread(
        target=monitor_winotify_notification,
        args=(global_output,),
        daemon=False
    )
    monitor_thread.start()

    capture_cmd_output_advanced("D:\BaiduNetdiskDownload\March7thAssistant_v2025.4.18_full\March7th Assistant.exe")
   
    # 主线程继续执行其他任务
    print("主线程继续执行其他任务...")
