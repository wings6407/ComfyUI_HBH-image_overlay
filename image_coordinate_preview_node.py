import torch
import numpy as np
from PIL import Image
import json
import os

class ImageCoordinatePreviewNode:
    def __init__(self):
        self.output_dir = "coordinate_preview"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "coordinates_json": ("STRING",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "preview_coordinates"
    CATEGORY = "image/preview"

    def draw_point(self, image, x, y, color, size):
        # 将numpy数组转换为PIL图像
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = image
            
        pil_image = Image.fromarray((image_np[0] * 255).astype(np.uint8))
        
        # 确保图像是RGB模式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 创建可绘制的图像副本
        draw_image = pil_image.copy()
        
        # 定义颜色映射
        color_map = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "green": (0, 255, 0),
            "yellow": (255, 255, 0),
            "white": (255, 255, 255)
        }
        
        # 获取选择的颜色
        point_color = color_map.get(color, (255, 0, 0))
        
        # 绘制点
        for i in range(-size, size + 1):
            for j in range(-size, size + 1):
                if i*i + j*j <= size*size:  # 圆形点
                    px = x + i
                    py = y + j
                    if 0 <= px < draw_image.width and 0 <= py < draw_image.height:
                        draw_image.putpixel((px, py), point_color)
        
        # 转换回numpy数组
        result = np.array(draw_image)
        result = result.astype(np.float32) / 255.0
        result = np.expand_dims(result, 0)
        
        return result

    def preview_coordinates(self, image, coordinates_json):
        try:
            # 解析坐标JSON
            coordinates = json.loads(coordinates_json)
            x = coordinates.get("x", 0)
            y = coordinates.get("y", 0)
            point_color = coordinates.get("point_color", "red")
            point_size = coordinates.get("point_size", 10)
            
            # 绘制预览图像
            preview_image = self.draw_point(image, x, y, point_color, point_size)
            
            return (preview_image,)
        except Exception as e:
            print(f"Error in preview_coordinates: {str(e)}")
            return (image,) 