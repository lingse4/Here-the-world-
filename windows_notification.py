import os
import sys
import time
from winotify import Notification, audio

icon_path = r"D:\Pictures\Screenshots\huo.png"

# 检查并安装必要的库
def install_required_libraries():
    try:
        # 尝试导入winotify以检查是否已安装
        import winotify
        print("winotify库已安装")
    except ImportError:
        print("正在安装winotify库...")
        # 使用pip安装winotify
        os.system(f"{sys.executable} -m pip install winotify")
        print("winotify库安装完成")

# 发送Windows 11通知的函数
def send_windows_notification(title="测试通知", message="这是一条来自Python的Windows 11通知", 
                              duration="short", app_id="Python通知", icon=None, sound=True):
    """
    发送Windows通知
    
    参数:
    title (str): 通知标题
    message (str): 通知内容
    duration (str): 通知显示时长，可选"short"或"long"
    app_id (str): 应用程序ID
    icon (str, optional): 通知图标路径，如果为None则使用默认图标
    sound (bool): 是否播放通知声音
    """
    # 创建通知对象
    toast = Notification(app_id=app_id, title=title, msg=message, duration=duration)
    
    # 设置图标（如果提供）
    if icon and os.path.exists(icon):
        toast.set_icon(icon)
    
    # 设置声音（如果需要）
    if sound:
        toast.set_audio(audio.Mail, loop=False)  # 使用邮件通知声音
    
    # 添加点击事件（点击通知时打开一个URL或文件）
    # 这里我们设置为打开当前目录
    toast.add_actions(label="打开文件夹", launch=f"explorer.exe {os.getcwd()}")
    
    # 显示通知
    toast.show()

# 测试通知发送
def test_notifications():
    print("开始发送测试通知...")
    
    # 发送基本通知
    send_windows_notification(
        title="基本测试通知", 
        message="这是一条基本的Windows 11通知测试",
        sound=True
    )
    time.sleep(3)  # 等待3秒
    
    # 发送自定义标题和内容的通知
    send_windows_notification(
        title="自定义通知", 
        message="这个通知有自定义的标题和内容",
        duration="long",  # 长显示时间
        sound=True
    )
    time.sleep(5)  # 等待5秒
    
    # 尝试发送带有图标（如果存在的话）的通知
    # 检查项目中是否有合适的图标文件
    # 尝试查找一个常见的图片文件作为图标

    
    if icon_path:
        send_windows_notification(
            title="带图标通知", 
            message=f"这个通知使用了图标: {icon_path}",
            icon=icon_path,
            sound=True
        )
    else:
        print("未找到合适的图标文件，跳过带图标通知测试")
    
    print("测试通知发送完成")

# 主函数
if __name__ == "__main__":
    # 安装必要的库
    install_required_libraries()
    
    # 运行测试
    test_notifications()