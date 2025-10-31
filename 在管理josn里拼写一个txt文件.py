import os

data_dir = r"C:\Users\38384\Desktop\抹茶巴菲\settings\accounts"

# 1. 确保目录存在（避免目录缺失导致文件创建失败）
os.makedirs(data_dir, exist_ok=True)

# 2. 拼接完整文件路径
file_path = os.path.join(data_dir, "123.txt")

# 3. 显式创建并写入文件（即使写入空内容也会生成文件）
with open(file_path, "w") as f:
    f.write("")  # 写入空内容或实际数据（如 "示例内容"）

print(f"文件已创建：{file_path}")