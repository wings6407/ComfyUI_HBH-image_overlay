import torch
import numpy as np
from PIL import Image
import json
import os

class ImageCoordinatePickerNode:
    def __init__(self):
        self.output_dir = "coordinate_picker"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "initial_x": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4096,
                    "step": 1
                }),
                "initial_y": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4096,
                    "step": 1
                }),
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
    FUNCTION = "get_coordinates"
    CATEGORY = "image/interactive"

    def get_coordinates(self, image, initial_x, initial_y, point_color, point_size):
        # 获取图像尺寸
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = image
            
        height, width = image_np.shape[1:3]
        
        # 确保初始坐标在图像范围内
        x = max(0, min(initial_x, width - 1))
        y = max(0, min(initial_y, height - 1))
        
        # 创建坐标JSON字符串
        coordinates = {
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "point_color": point_color,
            "point_size": point_size
        }
        coordinates_json = json.dumps(coordinates)
        
        return (image, x, y, coordinates_json) 