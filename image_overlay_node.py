import torch
import numpy as np
from PIL import Image
import json
import os

class ImageOverlayNode:
    def __init__(self):
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_image": ("IMAGE",),
                "overlay_image": ("IMAGE",),
                "coordinates": ("STRING", {
                    "default": '[{"x": 0, "y": 0}]',
                    "multiline": False
                }),
                "scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
                "rotation": ("FLOAT", {
                    "default": 0.0,
                    "min": -360.0,
                    "max": 360.0,
                    "step": 1.0
                }),
                "flip_horizontal": ("BOOLEAN", {
                    "default": False,
                    "label_on": "是",
                    "label_off": "否"
                }),
                "flip_vertical": ("BOOLEAN", {
                    "default": False,
                    "label_on": "是",
                    "label_off": "否"
                }),
                "blend_mode": (["normal", "multiply", "screen", "overlay", "soft_light", "hard_light", "color_dodge", "color_burn", "darken", "lighten"],),
                "opacity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "output_format": (["png", "jpg", "webp"],),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "overlay_images"
    CATEGORY = "image"

    def apply_blend_mode(self, base, overlay, mode):
        if mode == "normal":
            return overlay
        elif mode == "multiply":
            return base * overlay
        elif mode == "screen":
            return 1 - (1 - base) * (1 - overlay)
        elif mode == "overlay":
            mask = base > 0.5
            result = np.zeros_like(base)
            result[mask] = 1 - 2 * (1 - base[mask]) * (1 - overlay[mask])
            result[~mask] = 2 * base[~mask] * overlay[~mask]
            return result
        elif mode == "soft_light":
            mask = overlay > 0.5
            result = np.zeros_like(base)
            result[mask] = base[mask] * (1 - (1 - base[mask]) * (1 - (overlay[mask] - 0.5) * 2))
            result[~mask] = base[~mask] * (1 + (2 * overlay[~mask] - 1) * base[~mask])
            return result
        elif mode == "hard_light":
            mask = overlay > 0.5
            result = np.zeros_like(base)
            result[mask] = 1 - 2 * (1 - base[mask]) * (1 - overlay[mask])
            result[~mask] = 2 * base[~mask] * overlay[~mask]
            return result
        elif mode == "color_dodge":
            return np.minimum(1, base / (1 - overlay + 1e-6))
        elif mode == "color_burn":
            return 1 - np.minimum(1, (1 - base) / (overlay + 1e-6))
        elif mode == "darken":
            return np.minimum(base, overlay)
        elif mode == "lighten":
            return np.maximum(base, overlay)
        return overlay

    def overlay_images(self, base_image, overlay_image, coordinates, scale, rotation, flip_horizontal, flip_vertical, blend_mode, opacity, output_format):
        # 解析坐标JSON
        try:
            coords = json.loads(coordinates)
            if isinstance(coords, list) and len(coords) > 0:
                position_x = coords[0].get("x", 0)
                position_y = coords[0].get("y", 0)
            else:
                position_x = 0
                position_y = 0
        except:
            position_x = 0
            position_y = 0

        # 确保输入是numpy数组
        if isinstance(base_image, torch.Tensor):
            base_image = base_image.cpu().numpy()
        if isinstance(overlay_image, torch.Tensor):
            overlay_image = overlay_image.cpu().numpy()

        # 转换为PIL图像
        base_pil = Image.fromarray((base_image[0] * 255).astype(np.uint8))
        overlay_pil = Image.fromarray((overlay_image[0] * 255).astype(np.uint8))

        # 调整修改图大小
        new_size = (int(overlay_pil.width * scale), int(overlay_pil.height * scale))
        overlay_pil = overlay_pil.resize(new_size, Image.Resampling.LANCZOS)

        # 应用翻转
        if flip_horizontal:
            overlay_pil = overlay_pil.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_vertical:
            overlay_pil = overlay_pil.transpose(Image.FLIP_TOP_BOTTOM)

        # 旋转修改图
        if rotation != 0:
            overlay_pil = overlay_pil.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
            rotated_width, rotated_height = overlay_pil.size
            if rotation % 180 != 0:
                position_x = position_x - (rotated_width - new_size[0]) // 2
                position_y = position_y - (rotated_height - new_size[1]) // 2

        # 将底图转换为RGBA
        if base_pil.mode != 'RGBA':
            base_pil = base_pil.convert('RGBA')
        
        # 将修改图转换为RGBA
        if overlay_pil.mode != 'RGBA':
            overlay_pil = overlay_pil.convert('RGBA')

        # 应用不透明度
        if opacity < 1.0:
            overlay_pil.putalpha(int(255 * opacity))

        # 计算位置
        x = position_x
        y = position_y

        # 创建新的透明图层
        result = base_pil.copy()  # 使用底图的副本作为基础

        # 粘贴修改图
        result.paste(overlay_pil, (x, y), overlay_pil)
        
        # 应用混合模式
        if blend_mode != "normal":
            base_np = np.array(base_pil).astype(np.float32) / 255.0
            overlay_np = np.array(overlay_pil).astype(np.float32) / 255.0
            overlay_resized = np.zeros_like(base_np)
            
            h, w = overlay_np.shape[:2]
            bh, bw = base_np.shape[:2]
            
            x = max(0, min(x, bw - 1))
            y = max(0, min(y, bh - 1))
            
            end_x = min(x + w, bw)
            end_y = min(y + h, bh)
            
            usable_w = end_x - x
            usable_h = end_y - y
            
            overlay_resized[y:end_y, x:end_x] = overlay_np[:usable_h, :usable_w]
            
            blended = self.apply_blend_mode(base_np, overlay_resized, blend_mode)
            result = Image.fromarray((blended * 255).astype(np.uint8))

        # 创建遮罩蒙版
        mask = Image.new('L', base_pil.size, 0)
        if overlay_pil.mode == 'RGBA':
            # 使用alpha通道作为蒙版
            alpha = overlay_pil.split()[3]
            mask.paste(alpha, (x, y))
        else:
            # 如果没有alpha通道，使用图像亮度作为蒙版
            gray = overlay_pil.convert('L')
            mask.paste(gray, (x, y))

        # 根据输出格式保存
        if output_format == "jpg":
            result = result.convert('RGB')
        elif output_format == "webp":
            result = result.convert('RGBA')

        # 转换回numpy数组
        result_np = np.array(result)
        if output_format == "jpg":
            result_np = result_np.astype(np.float32) / 255.0
        else:
            result_np = result_np.astype(np.float32) / 255.0

        # 添加批次维度
        result_np = np.expand_dims(result_np, 0)

        # 转换蒙版为numpy数组
        mask_np = np.array(mask).astype(np.float32) / 255.0
        mask_np = np.expand_dims(mask_np, 0)

        return (torch.from_numpy(result_np), torch.from_numpy(mask_np))

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True 