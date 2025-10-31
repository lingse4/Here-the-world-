import subprocess
import time

YS_PATHB = r'psexec -i 2 -u lingse -p 107881 cmd.exe /k "C:\\Python313\\python.exe C:\Users\lingse\Desktop\ysqd.py || echo 脚本执行出错！错误码：%errorlevel% & pause"'
def start_application(app_path):
    try:
        time.sleep(3)
        subprocess.Popen(app_path, shell=True)
    except Exception as e:
        raise RuntimeError(f"启动应用失败：{e}")
    
start_application(YS_PATHB)
