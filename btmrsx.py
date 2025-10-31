import subprocess
import time
from keyboard import press_and_release
from Window_btscreenshot import window_btscreenshot
from cv2的图片点击 import get_xy
from qywxftp import send_image_to_wechat_robot
from output_capture import routine
import pygetwindow as gw

def bring_window_to_front(window_title):
    """将指定标题的窗口前置并激活"""
    try:
        # 查找标题包含指定字符串的所有窗口
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"未找到标题包含 '{window_title}' 的窗口")
            return
        
        # 获取第一个匹配的窗口
        window = windows[0]
        
        # 如果窗口是最小化的，则还原它
        if window.isMinimized:
            window.restore()
            print(f"窗口 '{window_title}' 已从最小化状态还原")
        
        # 将窗口置于前台并激活
        window.activate()
        print(f"窗口 '{window_title}' 已前置")
        
    except Exception as e:
        print(f"操作窗口时出错：{e}")


time.sleep(5)
bring_window_to_front("崩坏：星穹铁道")
time.sleep(1)
# 执行按键操作
press_and_release("Escape")
print("已按下Escape")
time.sleep(2)
press_and_release("F4")
print("已按下F4")

# 执行点击操作
while not get_xy("C:/Users/Administrator/Desktop/Matcha Parfait/Pictures/huo.png"):
    if get_xy("C:/Users/Administrator/Desktop/Matcha Parfait/Pictures/mrsx.png"):
       routine("C:/Users/Administrator/Desktop/Matcha Parfait/Pictures/mrsx.png", "每日实训")
       break
    if get_xy("C:/Users/Administrator/Desktop/Matcha Parfait/Pictures/mrsx1.png"):
       routine("C:/Users/Administrator/Desktop/Matcha Parfait/Pictures/mrsx1.png", "每日实训")
       break
time.sleep(2)

# 截图操作
window_btscreenshot("崩坏：星穹铁道")

# 发送图片到企业微信
try:
    WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=949cfed3-6a47-4bcd-baf5-582d6e8b79df"
    IMAGE_PATH = "C:/Users/Administrator/Pictures/GameScreenshots/mihayo.png"
    send_image_to_wechat_robot(WEBHOOK_URL, IMAGE_PATH)
    print("已发送图片到企业微信机器人")
except Exception as e:
    print(f"发送图片失败: {str(e)}")

press_and_release("Enter")
print("所有操作已完成")
# 等待用户查看结果
time.sleep(5)