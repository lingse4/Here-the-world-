import os
import sys
import time
import ctypes
from PIL import Image
import tempfile

# 确保必要的库已安装
def install_required_libraries():
    print("检查并安装必要的库...")
    
    # 检查并安装plyer库
    try:
        import plyer
        print("plyer库已安装")
    except ImportError:
        print("正在安装plyer库...")
        os.system(f"{sys.executable} -m pip install plyer")
        try:
            import plyer
            print("plyer库安装成功")
        except ImportError:
            print("plyer库安装失败，请手动运行以下命令安装：")
            print(f"{sys.executable} -m pip install plyer")
            return False
    
    # 检查并安装Pillow库（用于图片转换）
    try:
        from PIL import Image
        print("Pillow库已安装")
    except ImportError:
        print("正在安装Pillow库...")
        os.system(f"{sys.executable} -m pip install Pillow")
        try:
            from PIL import Image
            print("Pillow库安装成功")
        except ImportError:
            print("Pillow库安装失败，请手动运行以下命令安装：")
            print(f"{sys.executable} -m pip install Pillow")
            return False
    
    return True

# 将PNG图片转换为ICO格式
def convert_to_ico(png_path):
    """将PNG图片转换为ICO格式"""
    try:
        # 创建临时ICO文件
        temp_dir = tempfile.gettempdir()
        ico_path = os.path.join(temp_dir, f"temp_notification_icon_{os.path.basename(png_path)}.ico")
        
        # 打开PNG图片并转换为ICO
        image = Image.open(png_path)
        # 保存为ICO格式（确保尺寸适合通知）
        image.save(ico_path, format='ICO', sizes=[(32, 32)])
        
        print(f"已将 {png_path} 转换为 {ico_path}")
        return ico_path
    except Exception as e:
        print(f"转换PNG到ICO时出错: {str(e)}")
        return None

# 查找项目中的图标文件
def find_icon_file():
    """在项目中查找合适的图标文件"""
    # 检查用户提供的图标路径
    user_icon = r"D:\Pictures\Screenshots\huo.png"
    if os.path.exists(user_icon):
        return user_icon
    
    # 在项目的Pictures文件夹中查找常见的图标
    picture_folder = "Pictures"
    if os.path.exists(picture_folder):
        common_icons = ["huo.png", "ys.png", "lingse.png", "ys1.png"]
        for icon in common_icons:
            icon_path = os.path.join(picture_folder, icon)
            if os.path.exists(icon_path):
                return icon_path
    
    print("未找到合适的图标文件")
    return None

# 使用plyer发送带图标的通知
def send_notification_with_icon(title="测试通知", message="这是一条带图标的Windows通知", 
                               icon_path=None, timeout=10, app_name="我的应用"):
    from plyer import notification
    
    try:
        ico_path = None
        
        # 如果提供了图标路径
        if icon_path:
            # 检查文件是否存在
            if not os.path.exists(icon_path):
                print(f"警告: 找不到图标文件: {icon_path}")
            else:
                # 如果是PNG文件，转换为ICO
                if icon_path.lower().endswith('.png'):
                    ico_path = convert_to_ico(icon_path)
                # 如果已经是ICO文件，直接使用
                elif icon_path.lower().endswith('.ico'):
                    ico_path = icon_path
        
        # 发送通知
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,  # 现在可以自定义应用名称
            app_icon=ico_path,
            timeout=timeout
        )
        
        print(f"通知已发送: {title}")
        print(f"内容: {message}")
        print(f"应用名称: {app_name}")
        if ico_path:
            print(f"使用图标: {ico_path}")
        else:
            print("未使用自定义图标")
            
        return True
    except Exception as e:
        print(f"发送通知时出错: {str(e)}")
        # 如果带图标的通知失败，尝试发送不带图标的通知
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=timeout
            )
            print("已尝试发送不带图标的通知")
            return True
        except Exception as e2:
            print(f"发送不带图标的通知也失败了: {str(e2)}")
            return False

# 使用Windows原生API发送通知
def send_windows_native_notification(title="测试通知", message="这是一条Windows原生通知"):
    """
    使用Windows原生API发送通知，不支持自定义图标
    但更可靠，在大多数Windows版本上都能工作
    """
    try:
        # 加载user32.dll
        user32 = ctypes.windll.LoadLibrary('user32.dll')
        
        # 使用MessageBox函数显示通知
        # MB_ICONINFORMATION = 0x00000040L
        # MB_TOPMOST = 0x00000008L
        user32.MessageBoxW(0, message, title, 0x00000040 | 0x00000008)
        
        print(f"Windows原生通知已显示: {title}")
        return True
    except Exception as e:
        print(f"使用Windows原生API发送通知时出错: {str(e)}")
        return False

# 测试不同类型的通知
def test_notifications():
    print("开始发送测试通知...")
    
    # 1. 发送基本通知（无自定义图标）
    print("\n1. 发送基本通知（无自定义图标）...")
    send_notification_with_icon(
        title="基本测试通知",
        message="这是一条不带自定义图标的基本通知\n点击此通知不会有任何操作",
        icon_path=None,
        timeout=10,
        app_name="测试应用"
    )
    time.sleep(11)  # 等待通知显示
    
    # 2. 尝试发送带图标的通知
    print("\n2. 尝试发送带图标的通知...")
    icon_path = find_icon_file()
    
    if icon_path:
        send_notification_with_icon(
            title="带图标通知",
            message=f"这个通知尝试使用图标: {os.path.basename(icon_path)}\n（PNG会自动转换为ICO格式）",
            icon_path=icon_path,
            timeout=10,
            app_name="图标测试应用"
        )
    else:
        print("未找到图标文件，无法发送带图标的通知")
    
    time.sleep(11)  # 等待通知显示
    
    # 3. 发送自定义内容的通知
    print("\n3. 发送自定义内容的通知...")
    send_notification_with_icon(
        title="自定义通知",
        message="这个通知包含了自定义的标题、内容和应用名称！\n\n感谢您的测试！",
        icon_path=icon_path,
        timeout=15,
        app_name="自定义应用名称"
    )
    
    print("\n测试通知发送完成")

# 提供Windows通知设置检查指南
def check_windows_settings():
    print("\n=== 请检查以下Windows设置 ===")
    print("1. 右键点击任务栏上的音量/网络图标区域")
    print("2. 选择'通知设置'")
    print("3. 确保'通知'开关已打开")
    print("4. 向下滚动，找到'通知来自这些应用和其他发送者'")
    print("5. 确保Python相关应用的通知权限已开启")
    print("\n如果仍然无法看到通知，请尝试以管理员身份运行此脚本")

# 主函数
if __name__ == "__main__":
    print("=== Windows通知（支持图标）测试程序 ===")
    
    # 安装必要的库
    if install_required_libraries():
        # 运行测试
        test_notifications()
        
        # 提供Windows设置检查指南
        check_windows_settings()
    else:
        print("无法安装必要的库，程序无法继续运行")
        sys.exit(1)