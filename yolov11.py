import os
from ultralytics import YOLO

# Load a pretrained YOLO model
model = YOLO(r"C:\Users\Administrator\Desktop\Matcha Parfait\runs\detect\train17\weights\best.pt")  # load a custom model

output_dir = r"C:\Users\Administrator\Desktop\YOLO_results"
os.makedirs(output_dir, exist_ok=True)

results = model(
    r"C:\Users\Administrator\Desktop\8.png",
    save=True, 
    project=output_dir, 
    name="result",
    # 以下是提高精度的关键参数
    conf=0.1,  # 提高置信度阈值，过滤低置信度检测结果
    iou=0.1,   # 提高IOU阈值，使边界框更严格
    imgsz=1280,  # 增加输入图像尺寸，提高小物体检测精度
    augment=True,  # 使用测试时增强，提高整体检测精度
    max_det=500  # 增加最大检测目标数量
)


# Perform object detection on an image

# Visualize the results
for result in results:
    result.show()