import json
import os
import winreg
import itertools

reg_path_cn = "Software\\miHoYo\\原神"
reg_path_cn0 = "Software\\miHoYo\\崩坏：星穹铁道"
reg_path_cn1 = "Software\miHoYo\原神"
reg_path_oversea = "Software\\Cognosphere\\Star Rail"
uid_key = "GENERAL_DATA_h2389025596"
uid_key1 = "MIHOYOSDK_ADL_PROD_CN_h3123967166"
uid_key2 = '"GENERAL_DATA_h2389025596"=hex:'
uid_key3 = '"MIHOYOSDK_ADL_PROD_CN_h3123967166"=hex:'
uid_key4 = "App_LastUserID_h2841727341"
export_path = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\intoin\1.reg"
export_path1 = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\intoin\2.reg"
regkt = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\intoin\regkt.txt"
a = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\accounts\156753041.reg"
ysbtconfig_path = r"C:\Users\Administrator\Desktop\Matcha Parfait\ysbtconfig.json"
path1 = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\accounts\0.reg"


#def get_reg_path():
    #with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_cn):
        #return reg_path_cn

def get_uid():
    try:
        print(f"Accessing registry path: {reg_path_cn}")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_cn) as key:
            uid = winreg.QueryValueEx(key, uid_key)
            print(uid)
            uid16 = uid[0].hex()
            uid2 = ','.join(uid16[i:i+2] for i in range(0, len(uid16), 2))
            print(f"转换结果 (bytes.hex): {uid2}")
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"{uid_key2}{uid2}")
    except Exception as e:
        print(f"Error accessing registry: {e}")
        return ""

def get_uid1():
    try:
        print(f"Accessing registry path: {reg_path_cn}")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_cn) as key:
            uid = winreg.QueryValueEx(key, uid_key1)
            uid16 = uid[0].hex()
            uid2 = ','.join(uid16[i:i+2] for i in range(0, len(uid16), 2))
            print(f"转换结果 (bytes.hex): {uid2}")
            with open(export_path1, 'w', encoding='utf-8') as f:
                f.write(f"{uid_key3}{uid2}")
    except Exception as e:
        print(f"Error accessing registry: {e}")
        return ""

# 定义一个函数，用于合并文本文件
def merge_text_files(uid):
    """
    合并多个文本文件到一个输出文件中
    :param file_list: 要合并的文件列表
    :param output_file: 输出文件的路径
    """
        # 示例文件列表
    intoin = [regkt,export_path, export_path1]
    # 输出文件路径
    output = f"C:\\Users\\Administrator\\Desktop\\Matcha Parfait\\settings\\accounts\\{uid}.reg"

    with open(output, 'w', encoding='utf-8') as outfile:
        for into in intoin:
            with open(into, 'r', encoding='utf-8') as infile:
                # 将每个文件的内容写入输出文件
                outfile.write(infile.read())
                # 在每个文件内容之间添加换行符，避免内容粘连
                outfile.write('\n')

def reg_delete():
    with open(ysbtconfig_path, 'r', encoding='utf-8') as f:
        data=json.load(f)

# 将字符串 "1,2" 转换为数组 ["1", "2"]
    values = data['reg_key'].split(',')

    # 迭代数组
    for value in values:
        print(value)
        # 删除注册表项
        subcommand = f"reg delete HKCU\{reg_path_cn1} /v {value} /f"
        os.system(subcommand)

def findkey(path):
    with open(path1, 'r', encoding='utf-16-le') as f:
        lines = f.readlines()
        found_key = False
        full_value = ""

        
        for line in lines:
            # 查找目标键
            if uid_key1 in line or uid_key in line:
                found_key = True
                full_value += line
                print(f"找到目标键: {full_value}")
            # 捕获后续的十六进制数据行（以空格开头的行通常是值的延续）
            elif found_key and line.startswith(" "):
                full_value += line.lstrip()
                print(f"追加数据: {line}")
            # 如果找到了键并且遇到了新的键行，说明当前键的值已结束
            elif found_key and line.startswith('"'):
                print(f"完整的注册表值:{full_value}")
                # 如果只需要第一个匹配项，可以在这里break
                # break
                # 重置状态以查找可能的其他匹配项
                found_key = False

        with open(path, 'w', encoding='utf-16-le') as f1:
            with open(regkt, 'r', encoding='utf-16-le') as f2:
                f1.write(f2.read())
                f1.write('\n')
            f1.write(f"{full_value}")

            # 在每个文件内容之间添加换行符，避免内容粘连


def gamereg_export():

    subcommand = f'C:\\Windows\\System32\\reg.exe EXPORT "HKCU\\{reg_path_cn}" "{path1}" /y'
    os.system(subcommand)




def gamereg_export0():

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path_cn0) as key:
        key0 = winreg.QueryValueEx(key, uid_key4)
        uid = key0[0]


    path = f"C:\\Users\\Administrator\\Desktop\\Matcha Parfait\\settings\\accounts\\{uid}.reg"
    subcommand = f'C:\\Windows\\System32\\reg.exe EXPORT "HKCU\\{reg_path_cn0}" "{path}" /y'
    os.system(subcommand)


def gamereg_import(path: str) -> None:
    subcommand = f'REG IMPORT "{path}"'
    os.system(subcommand)

# 新增：打印关键信息（仅在直接运行脚本时执行）
if __name__ == "__main__":
    #reg_delete()
    gamereg_export0()
    
    
