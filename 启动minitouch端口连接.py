import subprocess
import os
import time

commands = [
    "adb connect emulator-5554",
    "adb -s emulator-5554 shell am start-foreground-service --user 0 -a jp.co.cyberagent.stf.ACTION_START -n jp.co.cyberagent.stf/.Service && adb -s emulator-5554 forward tcp:1102 localabstract:stfservice",
    "adb -s emulator-5554 forward tcp:1092 localabstract:stfagent && adb -s emulator-5554 shell pm path jp.co.cyberagent.stf && adb -s emulator-5554 shell export CLASSPATH=\"package:/data/app/jp.co.cyberagent.stf-k4TOFwRWHHDXNz0Jq6FzVA==/base.apk\";exec app_process /system/bin jp.co.cyberagent.stf.Agent",
    "adb -s emulator-5554 shell /data/local/tmp/minitouch",
    "adb -s emulator-5554 forward tcp:1092 localabstract:minitouch"
]

# Define the CREATE_NO_WINDOW flag
CREATE_NO_WINDOW = 0x08000000

# 按顺序执行命令，并在第一个命令后添加等待
for i, command in enumerate(commands):
    subprocess.Popen(command, creationflags=CREATE_NO_WINDOW, shell=True)
    # 第一个命令（连接）执行后等待1秒
    if i == 0:
        time.sleep(1)

