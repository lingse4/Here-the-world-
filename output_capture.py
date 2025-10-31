import os
import re
import subprocess
import sys
import threading
import time
import tempfile
import cv2
import numpy as np
from paddleocr import PaddleOCR
import pyautogui
from qywxftp import send_image_to_wechat_robot
from keyboard import press_and_release
from Window_btscreenshot import window_btscreenshot 
from threading import Lock
import win32pipe
import win32file
import win32con

# 全局变量保持不变
global_output = []  # 存储外部程序的输出
global_output_lock = Lock()  # 保护全局输出的锁
process_running = True  # 标记外部进程是否在运行
ocr = PaddleOCR(use_angle_cls=True, lang='en',det_db_unclip_ratio=1.0)  
btmrsx = "C:/Users/Administrator/Desktop/Matcha Parfait/btmrsx.py"



def decode_with_fallback(data):
    """尝试多种编码解码数据，确保中文正确显示"""
    encodings = ['utf-8', 'gbk', 'latin-1']
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    # 如果所有编码都失败，使用replace策略
    return data.decode('utf-8', errors='replace')


# 新增函数：使用命名管道在新CMD窗口中运行命令并实时捕获输出
def run_in_new_cmd_and_capture_output_realtime(cmd, timeout=None):
    """
    在新的CMD窗口中运行命令并实时捕获其输出（使用命名管道，无需临时文件）
    cmd: 要执行的命令
    timeout: 超时时间（秒），None表示不超时
    返回: 包含输出内容的字符串
    """
    # 生成唯一的管道名称
    pipe_name = f'\\\\.\\pipe\\output_capture_pipe_{int(time.time())}'
    print(f"创建命名管道: {pipe_name}")
    
    # 创建管道服务器
    pipe = win32pipe.CreateNamedPipe(
        pipe_name,
        win32pipe.PIPE_ACCESS_INBOUND,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None
    )
    
    # 存储捕获的输出
    captured_output = []
    
    try:
        # 构建Windows命令 - 使用命名管道重定向输出
        # 关键点1: 使用^转义特殊字符
        # 关键点2: 使用2>&1确保标准错误也被捕获
        # 关键点3: 使用start /wait确保等待进程完成
        windows_cmd = f'cmd.exe /c "start "新窗口执行" /wait cmd.exe /c "{cmd}" ^> {pipe_name} 2^>^&1"'
        print(f"执行命令: {windows_cmd}")
        
        # 启动进程执行命令
        process = subprocess.Popen(
            windows_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 启动一个线程来读取管道数据
        def read_pipe():
            # 连接到管道
            win32pipe.ConnectNamedPipe(pipe, None)
            
            try:
                while process_running:
                    # 读取管道数据（每次最多4096字节）
                    try:
                        data = win32file.ReadFile(pipe, 4096)
                        if data[0] == 0 and len(data[1]) > 0:
                            # 解码数据
                            chunk = decode_with_fallback(data[1])
                            captured_output.append(chunk)
                            
                            # 实时添加到全局输出
                            with global_output_lock:
                                global_output.append(chunk)
                            
                            print(f"实时捕获输出: {chunk.strip()}")
                        else:
                            # 没有数据可读，休眠一小段时间
                            time.sleep(0.1)
                    except Exception as e:
                        # 管道读取错误，可能是管道已关闭
                        print(f"管道读取错误: {str(e)}")
                        break
            finally:
                # 关闭管道连接
                win32pipe.DisconnectNamedPipe(pipe)
        
        # 启动管道读取线程
        pipe_thread = threading.Thread(target=read_pipe)
        pipe_thread.daemon = True
        pipe_thread.start()
        
        # 等待进程完成或超时
        start_time = time.time()
        while True:
            # 检查进程是否已结束
            if process.poll() is not None:
                print(f"命令执行完成，返回码: {process.returncode}")
                # 等待管道读取线程完成
                time.sleep(1)  # 给管道读取线程一点时间完成最后的读取
                break
            # 检查是否超时
            if timeout and time.time() - start_time > timeout:
                process.kill()
                return "命令执行超时！"
            time.sleep(0.5)
        
        # 合并捕获的输出
        full_output = ''.join(captured_output)
        print(f"捕获到的总输出长度: {len(full_output)} 字符")
        
        return full_output
    except Exception as e:
        error_msg = f"执行命令出错: {str(e)}"
        print(error_msg)
        # 将错误信息添加到全局输出
        with global_output_lock:
            global_output.append(error_msg)
        return error_msg
    finally:
        # 关闭管道
        try:
            win32file.CloseHandle(pipe)
            print(f"已关闭命名管道: {pipe_name}")
        except Exception as e:
            print(f"关闭管道时出错: {str(e)}")

# 修改capture_cmd_output_advanced函数以使用实时捕获方法
def capture_cmd_output_advanced(cmd, shell=True, show_output=True, run_in_new_window=False):
    """
    捕获命令行输出，支持在当前窗口或新窗口运行
    run_in_new_window: 是否在新窗口中运行命令
    """
    global process_running
    
    print("run_in_new_window:", run_in_new_window)

    if run_in_new_window:
        print("cmd:", cmd)
        # 使用新窗口实时执行命令并获取输出
        result = run_in_new_cmd_and_capture_output_realtime(cmd)
        return {
            'success': True,  # 简化处理，实际应根据结果判断
            'output': result,
            'error': '',
            'return_code': 0
        }
    
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

def execute_next_steps_in_new_cmd():
    """在新的CMD窗口中执行后续操作"""


    # 在新CMD窗口中运行临时脚本 - 修改版
    windows_cmd = f'start "后续操作" cmd.exe /c C:/Users/Administrator/AppData/Local/Microsoft/WindowsApps/python3.11.exe "{btmrsx}" && pause'
    subprocess.Popen(windows_cmd, shell=True)
    
    # 标记原进程运行状态为False，停止监控
    global process_running
    process_running = False


# 定义一个函数，用于在线程中执行正则匹配和后续操作
def monitor_winotify_notification():
    """
    在线程中监控winotify通知完成的消息
    """
    # 定义正则表达式模式
    flexible_pattern = re.compile(
        r'.*开拓力剩余.*', 
        re.IGNORECASE
    )
    print("开始监控输出...")
    while process_running:
        # 获取当前的输出内容进行检查
        with global_output_lock:
            current_output = ''.join(global_output)
            print(f"当前global_output长度: {len(global_output)}, 内容: {current_output}")  # 详细的调试信息

        # 检查是否匹配到目标文本
        if flexible_pattern.search(current_output):
            print("成功捕获到winotify通知相关提示!")
            
            # 执行后续操作
            execute_next_steps_in_new_cmd()
            
            break
        
        time.sleep(1)  # 添加休眠防止CPU占用过高


# 使用示例
def gotta_clue():
    global global_output, process_running
    global_output = []  # 清空之前的输出
    process_running = True  # 重置运行状态
    
    # 创建并启动命令执行线程
    cmd_thread = threading.Thread(
        target=capture_cmd_output_advanced,
        args=("D:\BaiduNetdiskDownload\March7thAssistant_v2025.4.18_full\March7th Assistant.exe",),
        kwargs={'run_in_new_window': True},  # 设置在新窗口运行
        daemon=False
    )
    cmd_thread.start()

    # 创建并启动监控线程

    monitor_winotify_notification()
    
    print("主线程继续执行其他任务...")
    time.sleep(50)

if __name__ == "__main__":
    gotta_clue()