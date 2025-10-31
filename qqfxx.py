import pyautogui
import time
import subprocess
import pyperclip
import win32gui
import win32con
from PIL import Image
import cv2
import numpy as np
import win32clipboard
from io import BytesIO

def close_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print(f"已关闭窗口 (句柄: {hwnd})")
        return True
    except Exception as e:
        print(f"关闭失败 (句柄: {hwnd}): {str(e)}")
        return False

def screenshot_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"未找到窗口：{window_title}")
        return None
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    screenshot = pyautogui.screenshot()
    crop = screenshot.crop((left, top, right, bottom))
    return cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)

def routine(template_path, target_name, threshold=0.85):
    """
    基于pyautogui截图的图像匹配点击
    """
    hwnd = win32gui.FindWindow(None, "QQ")
    if not hwnd:
        print(f"错误：未找到{target_name}窗口")
        return False

    screenshot = screenshot_window("QQ")
    if screenshot is None or screenshot.size == 0:
        print(f"错误：{target_name}截图失败")
        return False

    template = cv2.imread(template_path)
    if template is None:
        print(f"错误：模板图片{template_path}不存在")
        return False

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        window_left, window_top, _, _ = win32gui.GetWindowRect(hwnd)
        click_x = window_left + max_loc[0] + w // 2
        click_y = window_top + max_loc[1] + h // 2
        pyautogui.click(click_x, click_y)
        print(f"成功点击{target_name}（相似度：{max_val:.2f}）")
        return True
    else:
        print(f"{target_name}匹配失败（相似度：{max_val:.2f} < {threshold}）")
        return False

def copy_image_to_clipboard(image_path):
    """
    将图片复制到剪贴板
    """
    try:
        # 打开图片
        image = Image.open(image_path)
        # 创建一个字节流对象
        output = BytesIO()
        # 将图片保存到字节流（PNG格式保持透明度）
        image.convert('RGB').save(output, 'BMP')
        # 获取字节数据
        data = output.getvalue()[14:]  # BMP文件头有14个字节
        output.close()
        
        # 打开剪贴板
        win32clipboard.OpenClipboard()
        # 清空剪贴板
        win32clipboard.EmptyClipboard()
        # 设置剪贴板数据
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        # 关闭剪贴板
        win32clipboard.CloseClipboard()
        print(f"已将图片 {image_path} 复制到剪贴板")
        return True
    except Exception as e:
        print(f"复制图片到剪贴板失败: {str(e)}")
        return False
qqs = [
    r"C:\Users\Administrator\Desktop\生活必须品\代肝交流群原神崩铁鸣潮绝区零三角洲.lnk",
    r"C:\Users\Administrator\Desktop\生活必须品\代肝友友交流群原神鸣潮星铁绝区零.lnk",
    r"C:\Users\Administrator\Desktop\生活必须品\原神长草摸鱼弹琴唠嗑代肝群.lnk"
]
if __name__ == '__main__':
    for shortcut_path in qqs:

        # 1. 打开QQ群快捷方式 (替换为你的快捷方式路径)
        subprocess.Popen(f'cmd /c start "" "{shortcut_path}"', shell=True)

        time.sleep(7)
        routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\fxx.png", "发消息", threshold=0.6)
        time.sleep(1)
        routine(r"C:\Users\Administrator\Desktop\Matcha Parfait\Pictures\Screenshots\fs.png", "发送", threshold=0.6)


        # 发送图片，而不是图片路径
        image_path = r"C:\Users\Administrator\Desktop\乐奈哈气了.jpg"
        if copy_image_to_clipboard(image_path):
            pyautogui.hotkey('ctrl', 'v')  # 粘贴图片
            time.sleep(1)  # 等待图片加载
            pyautogui.hotkey('ctrl', 'enter')  # QQ默认发送快捷键
            print("图片已发送!")



        # 4. 关闭QQ主窗口
        close_window("QQ")
        close_window("原神接单 - QQ群")
        close_window("原神接单 - QQ群")
        close_window("原神接单 - QQ群")

