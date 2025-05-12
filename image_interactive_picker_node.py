import torch
import numpy as np
from PIL import Image
import json
import os

class ImageInteractivePickerNode:
    def __init__(self):
        self.output_dir = "interactive_picker"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.last_image = None
        self.last_coordinates = {"x": 0, "y": 0}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "point_color": (["red", "blue", "green", "yellow", "white"],),
                "point_size": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 50,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "x_coordinate", "y_coordinate", "coordinates_json")
    FUNCTION = "interactive_pick"
    CATEGORY = "image/interactive"

    def draw_point(self, image, x, y, color, size):
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = image
            
        # 转换为PIL图像
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

    def interactive_pick(self, image, point_color, point_size):
        # 获取图像尺寸
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = image
            
        height, width = image_np.shape[1:3]
        
        # 使用上次的坐标或默认值
        x = self.last_coordinates.get("x", width // 2)
        y = self.last_coordinates.get("y", height // 2)
        
        # 确保坐标在图像范围内
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        
        # 绘制带有坐标点的图像
        preview_image = self.draw_point(image, x, y, point_color, point_size)
        
        # 更新坐标
        self.last_coordinates = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        # 创建坐标JSON
        coordinates_json = json.dumps(self.last_coordinates)
        
        return (preview_image, x, y, coordinates_json)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")  # 使节点始终更新

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True 