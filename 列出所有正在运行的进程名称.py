# list_all_processes.py
import psutil
import win32gui

"""
列出所有正在运行的进程名称和窗口标题
使用psutil库获取系统中所有正在运行的进程信息
使用win32gui获取窗口标题信息
"""

def list_running_processes():
    """获取并打印所有正在运行的进程名称"""
    print("正在运行的进程名称列表：")
    print("=" * 50)
    
    # 存储已显示的进程名称，避免重复
    seen_processes = set()
    
    try:
        # 遍历所有正在运行的进程
        for proc in psutil.process_iter(['name']):
            try:
                # 获取进程名称
                process_name = proc.info['name']
                
                # 只显示未重复的进程名称
                if process_name not in seen_processes:
                    seen_processes.add(process_name)
                    print(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 处理可能出现的异常
                pass
    except Exception as e:
        print(f"获取进程信息时发生错误：{e}")
    
    print("=" * 50)
    print(f"共发现 {len(seen_processes)} 个不同的进程")

def get_window_titles():
    """获取并打印所有可见窗口的标题"""
    print("\n所有可见窗口标题：")
    print("=" * 50)
    
    # 存储窗口标题，避免重复
    window_titles = []
    
    def callback(hwnd, titles):
        """窗口枚举回调函数"""
        # 检查窗口是否可见
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            title = win32gui.GetWindowText(hwnd)
            titles.append(title)
        return True
    
    try:
        # 枚举所有窗口
        win32gui.EnumWindows(callback, window_titles)
        
        # 打印所有窗口标题
        for title in window_titles:
            print(title)
        
        print("=" * 50)
        print(f"共发现 {len(window_titles)} 个可见窗口")
    except Exception as e:
        print(f"获取窗口信息时发生错误：{e}")

def get_process_window_mapping():
    """获取进程和窗口标题的映射关系"""
    print("\n进程与窗口标题映射：")
    print("=" * 50)
    
    # 导入win32process库用于获取进程ID
    import win32process
    
    # 存储进程ID和窗口标题的映射
    process_windows = {}
    
    def callback(hwnd, mapping):
        """窗口枚举回调函数"""
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            try:
                # 获取窗口所属的进程ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                # 获取窗口标题
                title = win32gui.GetWindowText(hwnd)
                
                # 添加到映射中
                if pid not in mapping:
                    mapping[pid] = []
                mapping[pid].append(title)
            except:
                pass
        return True
    
    try:
        # 枚举所有窗口
        win32gui.EnumWindows(callback, process_windows)
        
        # 打印进程名和窗口标题的映射关系
        for pid, titles in process_windows.items():
            try:
                # 根据进程ID获取进程名称
                proc = psutil.Process(pid)
                process_name = proc.name()
                print(f"进程名: {process_name} (PID: {pid})")
                for title in titles:
                    print(f"  - {title}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"获取进程窗口映射时发生错误：{e}")

if __name__ == "__main__":
    list_running_processes()
    get_window_titles()
    get_process_window_mapping()