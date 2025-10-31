import pygetwindow as gw
import pyautogui
import time
import os
from datetime import datetime

# 确保中文正常显示
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

# 创建截图保存目录
def ensure_screenshot_dir():
    """确保截图保存目录存在"""
    dir_path = r"C:\Users\Administrator\Pictures\GameScreenshots"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

# 获取窗口位置并截图
def get_window_position_and_screenshot(window_title, activate_window=True, delay=1):
    """
    查找指定窗口的位置并截取其截图
    
    参数:
    window_title: 窗口标题（可以是部分标题）
    activate_window: 是否先激活窗口，默认为True
    delay: 激活窗口后等待的秒数，给窗口切换提供时间
    
    返回:
    如果成功，返回截图保存的完整路径；否则返回None
    """
    try:
        # 查找所有窗口标题中包含特定字符串的窗口
        windows = gw.getWindowsWithTitle(window_title)
        
        if not windows:
            print(f"没有找到标题包含 '{window_title}' 的窗口")
            return None
        
        # 假设第一个匹配的窗口就是我们要找的目标窗口
        window = windows[0]
        
        # 获取窗口的位置信息 (left, top, width, height)
        left, top, width, height = window.left, window.top, window.width, window.height
        
        # 显示窗口位置信息
        print(f"找到窗口 '{window.title}' 的绝对位置: 左上角 ({left}, {top}), 宽度 {width}, 高度 {height}")
        
        # 计算窗口右下角坐标
        right = left + width
        bottom = top + height
        
        # 验证窗口坐标是否有效
        if width <= 0 or height <= 0:
            print(f"窗口尺寸无效: 宽度 {width}, 高度 {height}")
            return None
        
        # 如果需要激活窗口
        if activate_window and not window.isActive:
            try:
                print("尝试激活窗口...")
                window.activate()
                time.sleep(delay)  # 等待窗口激活并显示
            except Exception as e:
                print(f"激活窗口时出错: {e}")
                # 即使激活失败，也继续尝试截图
        
        # 截取窗口区域
        try:
            print(f"准备截取窗口区域: ({left+1225}, {top+1276}, {width-1800}, {height-900})")
            screenshot = pyautogui.screenshot(region=(left+900, top+1048, width-1800, height-1000))
            
            # 生成保存路径
            screenshot_dir = ensure_screenshot_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 清理标题中的特殊字符以用作文件名
            safe_title = "".join([c for c in window.title if c.isalnum() or c in ["_", "-", " "]]).strip()
            file_name = f"mihayo.png"
            save_path = os.path.join(screenshot_dir, file_name)
            
            # 保存截图
            screenshot.save(save_path)
            print(f"窗口截图已成功保存到: {save_path}")
            return save_path
        except Exception as e:
            print(f"截取窗口截图时出错: {e}")
            
            # 备选方案：尝试截取全屏并裁剪
            try:
                print("尝试备选方案：截取全屏并裁剪...")
                full_screenshot = pyautogui.screenshot()
                # 确保裁剪区域在屏幕范围内
                screen_width, screen_height = pyautogui.size()
                crop_left = max(0, left)
                crop_top = max(0, top)
                crop_right = min(screen_width, right)
                crop_bottom = min(screen_height, bottom)
                crop_width = crop_right - crop_left
                crop_height = crop_bottom - crop_top
                
                if crop_width > 0 and crop_height > 0:
                    cropped_screenshot = full_screenshot.crop((crop_left, crop_top, crop_right, crop_bottom))
                    
                    # 生成保存路径
                    screenshot_dir = ensure_screenshot_dir()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = f"mihayo.png"
                    save_path = os.path.join(screenshot_dir, file_name)
                    
                    # 保存截图
                    cropped_screenshot.save(save_path)
                    print(f"备选方案成功: 裁剪后的截图已保存到: {save_path}")
                    return save_path
                else:
                    print("备选方案失败: 裁剪区域无效")
                    return None
            except Exception as crop_error:
                print(f"备选方案执行失败: {crop_error}")
                return None
    except Exception as e:
        print(f"执行过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None

# 主程序
def djjr(window_title):
    print("程序启动，开始查找并截图指定窗口...")
    
    # 定义要查找的窗口标题关键字
    # 您可以根据需要修改这个标题关键字
    target_window_titles = [window_title]
    
    for window_title in target_window_titles:
        print(f"\n尝试查找窗口: '{window_title}'")
        result = get_window_position_and_screenshot(
            window_title=window_title,
            activate_window=True,
            delay=2  # 增加延迟时间，确保窗口完全显示
        )
        
        if result:
            print(f"\n任务成功完成！截图已保存到: {result}")
            return
        
    print("\n无法找到并截图任何目标窗口。请确保游戏或应用程序已经启动。")

if __name__ == "__main__":
    djjr("原神")
