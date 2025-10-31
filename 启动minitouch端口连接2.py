import subprocess
import os
import time

commands = [
    "adb connect 127.0.0.1:16416",
    "adb -s 127.0.0.1:16416 shell am start-foreground-service --user 0 -a jp.co.cyberagent.stf.ACTION_START -n jp.co.cyberagent.stf/.Service && adb -s 127.0.0.1:16416 forward tcp:1101 localabstract:stfservice",
    "adb -s 127.0.0.1:16416 forward tcp:1091 localabstract:stfagent && adb -s 127.0.0.1:16416 shell pm path jp.co.cyberagent.stf && adb -s 127.0.0.1:16416 shell export CLASSPATH=\"package:/data/app/~~56jIni6IM7hPMTVWHLx4pA==/jp.co.cyberagent.stf-Q8kJLE1FdIcBrgJyIsEUiA==/base.apk\";exec app_process /system/bin jp.co.cyberagent.stf.Agent",
    "adb -s 127.0.0.1:16416 shell chmod 755 /data/local/tmp/minitouch && adb -s 127.0.0.1:16416 shell /data/local/tmp/minitouch",
    "adb -s 127.0.0.1:16416 forward tcp:1091 localabstract:minitouch"
]

# Define the CREATE_NO_WINDOW flag
CREATE_NO_WINDOW = 0x08000000

for i, command in enumerate(commands):
    subprocess.Popen(command, creationflags=CREATE_NO_WINDOW, shell=True)
    # 第一个命令（连接）执行后等待1秒
    if i == 0:
        time.sleep(1)


