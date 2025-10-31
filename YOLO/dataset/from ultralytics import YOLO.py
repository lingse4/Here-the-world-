from ultralytics import YOLO
import os

# 设置中文显示（Matplotlib）
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

# 选择训练模式：从头训练(new)、基于预训练模型训练(finetune)、继续中断的训练(resume)
train_mode = "new"  # 可选: "new", "finetune", "resume"

# 数据集配置文件路径
data_config = r"C:\Users\Administrator\Desktop\YOLO\Untitled-2.yaml"

if train_mode == "new":
    # 从头开始训练（创建空模型）
    model = YOLO("yolo11n.yaml")  # 根据需要选择不同大小的模型配置：n/s/m/l/x
elif train_mode == "finetune":
    # 基于预训练模型微调
    model = YOLO("yolo11n.pt")  # 加载预训练权重
else:
    # 继续之前中断的训练
    model = YOLO("runs/detect/train/weights/last.pt")

# 开始训练
results = model.train(
    data=data_config,
    epochs=100,           # 训练轮数
    batch=16,             # 批次大小
    imgsz=640,            # 输入图像大小
    workers=0,            # 数据加载工作线程数
    device="cpu",             # GPU设备ID，-1表示CPU
    optimizer='auto',     # 优化器选择
    lr0=0.01,             # 初始学习率
    momentum=0.937,       # 动量
    weight_decay=0.0005,  # 权重衰减
    patience=10,          # 早停耐心值
    save_period=10,       # 每多少轮保存一次检查点
    project='runs/detect', # 结果保存目录
    name='train',         # 实验名称
    exist_ok=False,       # 是否覆盖现有实验
    pretrained=True,      # 是否使用预训练权重
    verbose=True,         # 是否显示详细输出
    seed=42,              # 随机种子
    deterministic=True,   # 是否使用确定性算法
    single_cls=False,     # 是否单类别训练
    rect=False,           # 是否使用矩形训练
    cos_lr=False,         # 是否使用余弦学习率调度
    close_mosaic=10,      # 最后多少轮关闭马赛克增强
    resume=False          # 是否从上次中断处恢复训练
)

# 验证模型性能
metrics = model.val()

# 导出模型为其他格式（可选）
# model.export(format='onnx')
