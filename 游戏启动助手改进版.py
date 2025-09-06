import cv2
import pyautogui
import time
import os
import sys
import ctypes
import numpy as np
import subprocess
from pywinauto import Application
import pygetwindow as gw
from pywinauto.application import Application
import psutil
from qfluentwidgets.components.date_time.calendar_picker import FIF  # type: ignore # 用于检查进程是否存在
import switch_account
import sys
from PyQt5.QtCore import QEventLoop, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import NavigationItemPosition, SplashScreen, Theme, setTheme, setThemeColor
from qframelesswindow import FramelessWindow, QTimer
from home_interface import HomeInterface
from .help_interface import HelpInterface
# from .changelog_interface import ChangelogInterface
from .warp_interface import WarpInterface
from .tools_interface import ToolsInterface
from .setting_interface import SettingInterface
from contextlib import redirect_stdout
with redirect_stdout(None):
    from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, setThemeColor, NavigationBarPushButton, toggleTheme, setTheme, Theme
    from qfluentwidgets import FluentIcon as FIF
    from qfluentwidgets import InfoBar, InfoBarPosition
from .card.messagebox_custom import MessageBoxSupport
from .tools.check_update import checkUpdate
from .tools.check_theme_change import checkThemeChange
from .tools.announcement import checkAnnouncement
from .tools.disclaimer import disclaimer
from utils.gamecontroller import GameController
import base64

pyautogui.FAILSAFE = False  # 警告：关闭安全保护，风险自负!

# 常量定义
APP_PATH = r"D:\BaiduNetdiskDownload\March7thAssistant_v2025.4.18_full\March7th Launcher.exe"
SECOND_APP_PATH = r"D:\BetterGI\BetterGI\BetterGI.exe"
IMAGE_PATH_BUTTON = r"C:\Users\38384\Pictures\Screenshots\wzyx.png"
IMAGE_PATH_DONE = r"C:\Users\38384\Pictures\Screenshots\ahcjg.png"
IMAGE_PATH_BUTTON_3 = r"C:\Users\38384\Pictures\Screenshots\ytl.png"
IMAGE_PATH_BUTTON_4 = r"C:\Users\38384\Pictures\Screenshots\ysqd.png"
IMAGE_PATH_DONE_2 = r"C:\Users\38384\Pictures\Screenshots\jrjlylq.png"
WINDOW_TITLE = "March7th Assistant"
SECOND_WINDOW_TITLE = "更好的原神"

# ------------------------ 核心功能函数 ------------------------

def start_application(app_path):
    try:
        Application().start(app_path)
    except Exception as e:
        raise RuntimeError(f"启动应用失败：{e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

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

def routine(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path, threshold=0.6)  # 将阈值从默认的 0.7 降低到 0.6
        if avg:
            print(f'正在点击 {name}')
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
        if proc.info['name'] == process_name:
            return True
    return False

# 移除原有的 switch_account_thread 线程函数

def main_operation(progress_callback):
    progress_callback(0, "正在初始化...")
    print("---------- 开始执行主流程 ----------")
    try:
        # 新增：主流程延迟45秒执行
        progress_callback(10, "主流程将在45秒后启动...")
        progress_callback(30, "45秒等待完成,开始执行主操作...")

        # 原有主流程逻辑保持不变
        image_paths = [
            IMAGE_PATH_BUTTON, IMAGE_PATH_DONE, 
            IMAGE_PATH_BUTTON_3, IMAGE_PATH_BUTTON_3, 
            IMAGE_PATH_DONE_2
        ]
        for path in image_paths:
            check_file_exists(path)

        start_application(APP_PATH)
        time.sleep(5)
        routine(IMAGE_PATH_BUTTON, "完整运行")

        print("等待第一个任务完成...")
        routine(IMAGE_PATH_DONE, "按回车键关")

        subprocess.run(["taskkill","/IM","StarRail.exe","/F","/T"])
        subprocess.run(["taskkill", "/IM", "March7th Launcher.exe", "/F", "/T"], check=True)
        pyautogui.press('enter')
        
        # start_application(SECOND_APP_PATH)
        
        # # 删除了 routine(IMAGE_PATH_BUTTON_2, "启动按钮") 的调用
        # routine(IMAGE_PATH_BUTTON_3, "一条龙")
        # time.sleep(2)
        
        # # 替换点击按钮的图像路径为 IMAGE_PATH_BUTTON_4
        # routine(IMAGE_PATH_BUTTON_4, "原神启动！")
        
        # # 如果 YuanShen.exe 不存在，则不断尝试点击 ysqd 按钮
        # while not is_process_running("YuanShen.exe"):
        #     print("未检测到 YuanShen.exe，尝试点击确认启动按钮...")
        #     if routine(IMAGE_PATH_BUTTON_4, "原神启动", timeout=5):
        #         print("成功点击确认启动按钮")
        #     else:
        #         print("点击失败，继续尝试...")
        #     time.sleep(2)
        
        # print("等待第二个任务完成...")
        # if not routine(IMAGE_PATH_DONE_2, "最终完成标识"):
        #     raise TimeoutError("第二个任务等待超时")
        # subprocess.run(["taskkill","/IM","YuanShen.exe","/F","/T"])
        # subprocess.run(["taskkill","/IM","BetterGI.exe","/F","/T"])

    except Exception as e:
        print(f"操作异常终止：{str(e)}")
    finally:
        print("---------- 主流程执行完成 ----------")

# ------------------------ GUI 功能 ------------------------

class Demo(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        self.initInterface()
        self.initNavigation()

    def initWindow(self):
        setThemeColor('#f18cb9', lazy=True)
        setTheme(Theme.AUTO, lazy=True)

        self.titleBar.maxBtn.setHidden(True)
        self.titleBar.maxBtn.setDisabled(True)
        self.titleBar.setDoubleClickEnabled(False)
        self.setResizeEnabled(False)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        self.resize(1920, 1280)
        self.setWindowIcon(QIcon(r"C:\Users\38384\Desktop\泠色.ico"))
        self.setWindowTitle('泠色')

        # 1. 创建启动页面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.titleBar.maxBtn.setHidden(True)
        self.splashScreen.raise_()

        #titleBar = StandardTitleBar(self.splashScreen)
        #titleBar.setIcon(self.windowIcon())
        #titleBar.setTitle(self.windowTitle())
        #self.splashScreen.setTitleBar(titleBar)

        desktop =  QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.show()
        QApplication.processEvents()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()

    def initInterface(self):
        self.homeInterface = HomeInterface(self)
        self.helpInterface = HelpInterface(self)
        # self.changelogInterface = ChangelogInterface(self)
        self.warpInterface = WarpInterface(self)
        self.toolsInterface = ToolsInterface(self)
        self.settingInterface = SettingInterface(self)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('主页'))
        self.addSubInterface(self.helpInterface, FIF.BOOK_SHELF, self.tr('帮助'))
        # self.addSubInterface(self.changelogInterface, FIF.UPDATE, self.tr('更新日志'))
        self.addSubInterface(self.warpInterface, FIF.SHARE, self.tr('抽卡记录'))
        self.addSubInterface(self.toolsInterface, FIF.DEVELOPER_TOOLS, self.tr('工具箱'))

        self.navigationInterface.addWidget(
            'startGameButton',
            NavigationBarPushButton(FIF.PLAY, '启动游戏', isSelectable=False),
            self.startGame,
            NavigationItemPosition.BOTTOM)

        self.navigationInterface.addWidget(
            'themeButton',
            NavigationBarPushButton(FIF.BRUSH, '主题', isSelectable=False),
            lambda: toggleTheme(lazy=True),
            NavigationItemPosition.BOTTOM)

        self.navigationInterface.addWidget(
            'avatar',
            NavigationBarPushButton(FIF.HEART, '赞赏', isSelectable=False),
            lambda: MessageBoxSupport(
                '支持作者🥰',
                '此程序为免费开源项目，如果你付了钱请立刻退款\n如果喜欢本项目，可以微信赞赏送作者一杯咖啡☕\n您的支持就是作者开发和维护项目的动力🚀',
                './assets/app/images/sponsor.jpg',
                self
            ).exec(),
            NavigationItemPosition.BOTTOM
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('设置'), position=NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()
        self.themeListener = checkThemeChange(self)

        if not cfg.get_value(base64.b64decode("YXV0b191cGRhdGU=").decode("utf-8")):
            disclaimer(self)

    # main_window.py 只需修改关闭事件
    def closeEvent(self, e):
        if self.themeListener and self.themeListener.isRunning():
            self.themeListener.terminate()
            self.themeListener.deleteLater()
        super().closeEvent(e)

    def startGame(self):
        game = GameController(cfg.game_path, cfg.game_process_name, cfg.game_title_name, 'UnityWndClass')
        try:
            if game.start_game():
                InfoBar.success(
                    title=self.tr('启动成功(＾∀＾●)'),
                    content="",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.warning(
                    title=self.tr('游戏路径配置错误(╥╯﹏╰╥)'),
                    content="请在“设置”-->“程序”中配置",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
        except Exception as e:
            InfoBar.warning(
                title=self.tr('启动失败'),
                content=str(e),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()

#run_as_admin()


