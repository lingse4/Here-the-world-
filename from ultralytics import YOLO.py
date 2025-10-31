from ultralytics import YOLO
import cv2
import os

# 加载预训练的YOLO模型
def process_video(video_path, output_path=None, show_real_time=True):
    # 加载YOLOv11模型
    model = YOLO("yolo11l.pt")  # 可以根据需要替换为yolo11n.pt, yolo11s.pt等

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return
    
    # 获取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"视频信息: {width}x{height}, {fps} FPS, {total_frames} 帧")
    
    
    # 创建视频写入对象（如果需要保存结果）
    out = None
    if output_path:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # 定义编解码器并创建VideoWriter对象
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 可以根据需要修改编解码器
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # 处理视频的每一帧
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 调整置信度阈值、IOU阈值等
        results = model(frame, conf=0.5, iou=0.7)

        # 仅检测特定类别（例如只检测人）
        #results = model(frame, classes=[0])  # 0是人的类别ID

        # 使用更高的检测分辨率（提高精度但降低速度）
        results = model(frame, imgsz=1280)
        
        # 显示处理进度
        frame_count += 1
        if frame_count % 10 == 0:  # 每10帧显示一次进度
            print(f"处理中: {frame_count}/{total_frames} 帧 ({frame_count/total_frames*100:.1f}%)")
        
        # 对当前帧进行目标检测
        results = model(frame)
        
        # 获取带有预测框的图像
        annotated_frame = results[0].plot()
        
        # 实时显示结果
        if show_real_time:
            cv2.imshow("YOLOv11 视频目标检测", annotated_frame)
            # 按'q'键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # 保存处理后的帧到输出视频
        if out:
            out.write(annotated_frame)
    
    # 释放资源
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    print("视频处理完成!")

if __name__ == "__main__":
    # 视频文件路径
    video_path = r"C:\Users\Administrator\Desktop\f15248e1a3bb144eee4f28a2ae6b46ec.mp4"
    # 输出视频保存路径（可选）
    output_path = r"C:\Users\Administrator\Desktop\YOLO_results\processed_video.mp4"
    
    # 处理视频
    process_video(video_path, output_path=output_path, show_real_time=True)
