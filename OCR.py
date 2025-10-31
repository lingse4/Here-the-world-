from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import os
import sys

# 确保中文正常显示
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

formatted_result = []

def ocr_image(image_path):
    """
    对指定路径的图像进行OCR识别，使用PIL库读取图像以解决中文路径问题
    
    参数:
    image_path: 图像文件路径
    
    返回:
    识别结果，如果识别失败则返回None
    """

        
    # 打印文件路径信息用于调试
    print(f"原始文件路径: {image_path}")
    
    # 使用PIL库直接读取图像，这样可以避免中文路径问题
    try:
        print("尝试使用PIL库读取图像...")
        # 直接用PIL读取图像文件
        pil_image = Image.open(image_path)
        # 转换为RGB模式，确保兼容性
        #if pil_image.mode != 'RGB':
            #pil_image = pil_image.convert('RGB')
        
        # 添加黑白化处理
        print("对图像进行黑白化处理...")
        # 首先转换为灰度图
        pil_image = pil_image.convert('L')
        # 可选：进行二值化处理（阈值可以根据需要调整）
        # threshold = 128  # 阈值，像素值大于阈值设为255（白），小于设为0（黑）
        # pil_image = pil_image.point(lambda x: 255 if x > threshold else 0, '1')
        
        # 转换为numpy数组，这是PaddleOCR可以接受的格式
        img_array = np.array(pil_image)
        # 检查数组形状，确保它有3个通道
        print("转换前图像形状:", img_array.shape)
        # 如果是灰度图，需要扩展维度以符合PaddleOCR的输入要求
        if len(img_array.shape) == 2:
            # 将灰度图转换为3通道格式
            img_array = np.stack((img_array,) * 3, axis=-1)
        # 确保图像是uint8类型
        img_array = img_array.astype(np.uint8)
        print("转换后图像形状:", img_array.shape)
    except Exception as img_error:
        print(f"PIL库读取图像失败: {img_error}")
        return None
    
    # 初始化OCR模型，使用最简单的配置
    try:
        print("初始化OCR模型...")
        # 只使用必要的参数，避免兼容性问题
        ocr = PaddleOCR(lang='ch')
    except Exception as ocr_error:
        print(f"OCR模型初始化失败: {ocr_error}")
        return None
    
    # 执行OCR识别，直接传入numpy数组

    result = ocr.predict(img_array)
    print(result)

    return result



# 测试文件路径是否可访问
def test_file_access(file_path):
    """测试文件是否可以被正常访问"""
    try:
        with open(file_path, 'rb') as f:
            print(f"成功打开文件: {file_path}")
            # 读取一小部分数据进行测试
            header = f.read(12)
            print(f"文件头信息: {header}")
            return True
    except Exception as e:
        print(f"无法访问文件: {file_path}, 错误: {e}")
        return False

# 重命名主函数，避免与ocr_image函数重名


        

if __name__ == "__main__":
    # 调用重命名后的主函数
    ocr_image(r"C:\Users\Administrator\Pictures\GameScreenshots\mihayo.png")