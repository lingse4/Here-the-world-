import base64
import json
import os
import winreg
from gameaccount import gamereg_export, gamereg_import ,reg_delete,findkey
#from module.logger import log

data_dir = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\accounts"
data_dir1 = r"D:\BetterGI\BetterGI\User\OneDragon"
xor_key = "TI4ftRSDaP63kBxxoLoZ5KpVmRBz00JikzLNweryzZ4wecWJxJO9tbxlH9YDvjAr"
path1 = r"C:\Users\Administrator\Desktop\Matcha Parfait\settings\accounts\0.reg"
ysjson = r"D:\BetterGI\BetterGI\User\config.json"
ysbtjson = r"C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json"

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

class Account:
    def __init__(self, account_id: int, account_name: str, timestamp: int = 0):
        self.account_id = account_id
        self.account_name = account_name
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.account_id}: {self.account_name}"

def read_all_account_from_files():
    """
    读取所有账户信息
    :return: List of Account objects
    """
    accounts = []
    for file in os.listdir(data_dir):
        if file.endswith(".reg"):
            timestamp = os.path.getmtime(os.path.join(data_dir, file))
            account_id = int(file.split(".")[0])
            account_name = str(account_id)
            name_file = os.path.join(data_dir, f"{account_id}.name")
            if os.path.exists(name_file):
                with open(name_file, "r") as f:
                    account_name = f.read().strip()
            accounts.append(Account(account_id, account_name, timestamp))
            print(f"Account loaded: {account_id} - {account_name} (timestamp: {timestamp})")
    return accounts

accounts = []

try:
    accounts = read_all_account_from_files()
except Exception as e:
    print(f"read_all_account_from_files: {e}")

def reload_all_account_from_files():
    """
    重新加载所有账户信息
    """
    global accounts
    accounts.clear()
    for a in read_all_account_from_files():
        accounts.append(a)

def dump_current_account(uid):
    """
    导出当前游戏账号到文件
    """

    account_reg_file = os.path.join(data_dir, f"{uid}.reg")
    findkey(account_reg_file)
    reload_all_account_from_files()

def delete_account(account_name: str, account_id: int):
    """
    删除指定账号
    :param account_id: 账号ID
    """
    name_file = os.path.join(data_dir, f"{account_id,account_name}.name")
    if os.path.exists(name_file):
        os.remove(name_file)
    account_reg_file = os.path.join(data_dir, f"{account_id}.reg")
    if os.path.exists(account_reg_file):
        os.remove(account_reg_file)
    ysconfig_file = os.path.join(data_dir1, f"{account_id}.json")
    if os.path.exists(ysconfig_file):
        os.remove(ysconfig_file)

    try:
        # 检查文件是否存在
        if not os.path.exists(ysbtjson):
            print(f"错误: 文件 {ysbtjson} 不存在")
            return False
        
        # 读取JSON文件
        with open(ysbtjson, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 检查数据是否为字典类型
        if not isinstance(data, dict):
            print(f"错误: JSON数据不是有效的字典格式")
            return False
        
        # 检查键是否存在
        if account_name not in data:
            print(f"警告: 键 '{account_name}' 在文件中不存在")
            return True  # 视为成功，因为目标键已经不存在
        
        # 删除指定的键及其值
        del data[account_name]
        
        # 将修改后的数据写回JSON文件，确保中文正常显示
        with open(ysbtjson, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        print(f"成功: 已从 {ysbtjson} 中删除键 '{account_name}' 及其所有嵌套值")
        return True
        
    except Exception as e:
        print(f"错误: 删除过程中发生异常 - {str(e)}")
        return False

def auto_renewal_account(uid):
    """
    更新保存的账户
    打开游戏前，游戏结束后调用，无论是否开启了多账户功能
    及时更新注册表到文件
    """
    try:

        if os.path.exists(os.path.join(data_dir, f"{uid}.reg")):
            dump_current_account()
    except Exception as e:
        print(f"auto_renewal_account: {e}")

def import_account(account_id: int):

    account_reg_file = os.path.join(data_dir, f"{account_id}.reg")
    print(account_reg_file) 
    if not os.path.exists(account_reg_file):
        raise FileNotFoundError(f"Account {account_id} not found (load)")
    gamereg_import(account_reg_file)

def import_account(account_id: int):

    account_reg_file = os.path.join(data_dir, f"{account_id}.reg")
    print(account_reg_file) 
    if not os.path.exists(account_reg_file):
        raise FileNotFoundError(f"Account {account_id} not found (load)")
    gamereg_import(account_reg_file)


def save_account_name(account_user: str,  account_name: str, account_id: int,  account_config: str, key: str):
    """
    保存账号名称
    :param account_id: 账号ID
    :param account_name: 账号名称
    """
    
    account_reg_file = os.path.join(data_dir, f"{account_id}.reg")
    findkey(account_reg_file)

    name_file = os.path.join(data_dir, f"{account_id,account_name}.name")
    with open(name_file, "w", encoding="utf-8") as f:
        f.write(account_name)
    
    with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        data[account_name] = {}
        data[account_name]["uid"] = account_id
        data[account_name]["ysconfig"] = account_config
        data[account_name]["user"] = account_user
        data[account_name]["key"] = key

        with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

reg_path = r"Software\miHoYo\崩坏：星穹铁道"
key_name = "App_LastUserID_h2841727341"

def get_uid():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            uid, regtype = winreg.QueryValueEx(key, key_name)
            print(f"{key_name} 的值为: {uid}")
            return uid
    except Exception as e:
        print(f"读取注册表时出错: {e}")

def btsave_account_name(account_user,account_name,value,value1,key):
    """
    保存账号名称
    :param account_id: 账号ID
    :param account_name: 账号名称
    """
    
    path = os.path.join(data_dir, f"{get_uid()}.reg")
    reg_path_cn0 = "Software\\miHoYo\\崩坏：星穹铁道"

    subcommand = f'C:\\Windows\\System32\\reg.exe EXPORT "HKCU\\{reg_path_cn0}" "{path}" /y'
    os.system(subcommand)

    name_file = os.path.join(data_dir, f"{get_uid(),account_name}.name")
    with open(name_file, "w", encoding="utf-8") as f:
        f.write(account_name)
    
    with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        data[account_name] = {}
        data[account_name]["instance_names"] = {}
        data[account_name]["uid"] = get_uid()
        data[account_name]["instance_type"] = value
        data[account_name]["instance_names"][value] = value1
        data[account_name]["user"] = account_user
        data[account_name]["key"] = key

        with open(r'C:\Users\Administrator\Desktop\Matcha Parfait\ysconfig.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def load_to_account(account_id: int) -> bool:
    """
    将游戏账号切换到account_id
    return True: 切换成功且需要重新加载游戏
    return False: 不需要重新加载游戏
    抛出异常: 切换失败，账号不存在
    """
    import_account(account_id)
    return True

def save_acc_and_pwd(account_id: int, account_name: str, account_pass: str):
    encrypted_text = xor_encrypt_to_base64(account_name + "," + account_pass)
    name_file = os.path.join(data_dir, f"{account_id}.acc")
    with open(name_file, "w") as f:
        f.write(encrypted_text)

def load_acc_and_pwd(account_id: int) -> (str):
    name_file = os.path.join(data_dir, f"{account_id}.acc")
    if not os.path.exists(name_file):
        return None, None
    with open(name_file, "r") as f:
        encrypted_text = f.read().strip()
    decrypted_text = xor_decrypt_from_base64(encrypted_text)
    return decrypted_text.split(",")

def xor_encrypt_to_base64(plaintext: str) -> str:
    secret_key = xor_key
    plaintext_bytes = plaintext.encode('utf-8')
    key_bytes = secret_key.encode('utf-8')

    encrypted_bytes = bytearray()
    for i in range(len(plaintext_bytes)):
        byte_plaintext = plaintext_bytes[i]
        byte_key = key_bytes[i % len(key_bytes)]
        encrypted_byte = byte_plaintext ^ byte_key
        encrypted_bytes.append(encrypted_byte)

    base64_encoded = base64.b64encode(encrypted_bytes).decode('utf-8')
    return base64_encoded

def xor_decrypt_from_base64(encrypted_base64: str) -> str:
    secret_key = xor_key
    encrypted_bytes = base64.b64decode(encrypted_base64.encode('utf-8'))
    key_bytes = secret_key.encode('utf-8')

    decrypted_bytes = bytearray()
    for i in range(len(encrypted_bytes)):
        byte_encrypted = encrypted_bytes[i]
        byte_key = key_bytes[i % len(key_bytes)]
        decrypted_byte = byte_encrypted ^ byte_key
        decrypted_bytes.append(decrypted_byte)

    decrypted_str = decrypted_bytes.decode('utf-8')
    return decrypted_str

def json_chang(config_path,key_path,value):
    with open(config_path, 'r', encoding='utf-8') as f:
        data=json.load(f)

    # 解析key_path，同时支持点表示法和数组索引
    current = data
    parts = []
    i = 0
    while i < len(key_path):
        if key_path[i] == '[':
            # 处理数组索引，如[0], [123]
            end = key_path.find(']', i)
            if end == -1:
                raise ValueError(f"无效的键路径: {key_path}")
            idx = int(key_path[i+1:end])
            parts.append(('index', idx))
            i = end + 1
            # 跳过可能的点
            if i < len(key_path) and key_path[i] == '.':
                i += 1
        else:
            # 处理对象键，如name, user.profile
            end = key_path.find('.', i)
            if end == -1:
                end = len(key_path)
            parts.append(('key', key_path[i:end]))
            i = end + 1
    
    # 遍历路径除最后一部分外的所有部分
    for part_type, part_value in parts[:-1]:
        if part_type == 'key':
            if part_value not in current or not isinstance(current[part_value], (dict, list)):
                raise ValueError(f"路径不存在或类型错误: {part_value}")
            current = current[part_value]
        else:  # index
            if not isinstance(current, list) or part_value >= len(current):
                raise ValueError(f"数组索引无效或越界: {part_value}")
            current = current[part_value]
    
    # 设置最后一个部分的值
    last_type, last_value = parts[-1]
    if last_type == 'key':
        current[last_value] = value
    else:
        current[last_value] = value

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def change_json(key,value):
    with open(ysjson, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 修改 JSON 数据
    # 假设 JSON 文件内容是一个字典，我们修改其中的某个键值对

    data[key] = value
    print(f'修改 {key} 为 {value}')

    # 将修改后的数据写回 JSON 文件
    with open(ysjson, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("JSON 文件已修改。")


if __name__ == "__main__":
    """"
    1和2绑定
    """
    #gamereg_export()
    #save_account_name("seling", "不觉", "218928220", "不觉", "15395408279")
    btsave_account_name("btseling", "bt慢慢", "拟造花萼（赤）" , "「纷争荒墟」悬锋城", "13140797617")
    #delete_account("慢慢", 156753041)
    #gamereg_export0("flyinstar")

