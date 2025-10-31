import requests
import base64
import hashlib
import os

def send_image_to_wechat_robot(webhook_url, image_path):
    """
    通过企业微信机器人发送图片
    
    参数:
    webhook_url: 企业微信机器人的Webhook地址
    image_path: 本地图片文件的路径
    """
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在 - {image_path}")
        return False
    
    # 检查文件是否为图片
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"错误: 不支持的图片格式 - {file_ext}，支持的格式: {valid_extensions}")
        return False
    
    try:
        # 读取图片文件
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 计算图片的base64编码和md5值
        base64_str = base64.b64encode(image_data).decode('utf-8')
        md5_str = hashlib.md5(image_data).hexdigest()
        
        # 构建请求数据
        payload = {
            "msgtype": "image",
            "image": {
                "base64": base64_str,
                "md5": md5_str
            }
        }
        
        # 发送请求
        response = requests.post(webhook_url, json=payload)
        response_data = response.json()
        
        # 检查发送结果
        if response_data.get('errcode') == 0:
            print("图片发送成功！")
            return True
        else:
            print(f"图片发送失败: {response_data.get('errmsg')}")
            return False
            
    except Exception as e:
        print(f"发送过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 替换为你的企业微信机器人Webhook地址
    WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=949cfed3-6a47-4bcd-baf5-582d6e8b79df"
    
    # 替换为你要发送的图片路径
    # 示例：IMAGE_PATH = r"C:\Pictures\example.png"
    IMAGE_PATH = r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png"
    
    # 发送图片
    send_image_to_wechat_robot(WEBHOOK_URL, IMAGE_PATH)
