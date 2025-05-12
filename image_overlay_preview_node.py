import torch
import numpy as np
from PIL import Image
import os

class ImageOverlayPreviewNode:
    def __init__(self):
        self.output_dir = "preview"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_image": ("IMAGE",),
                "overlay_image": ("IMAGE",),
                "overlay_state": ("OVERLAY_STATE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "preview_overlay"
    CATEGORY = "image/preview"

    def preview_overlay(self, base_image, overlay_image, overlay_state):
        # 从状态中获取参数
        position_x = overlay_state["position_x"]
        position_y = overlay_state["position_y"]
        scale = overlay_state["scale"]
        rotation = overlay_state["rotation"]
        blend_mode = overlay_state["blend_mode"]
        opacity = overlay_state["opacity"]

        # 创建临时预览图像
        if isinstance(base_image, torch.Tensor):
            base_image = base_image.cpu().numpy()
        if isinstance(overlay_image, torch.Tensor):
            overlay_image = overlay_image.cpu().numpy()

        base_pil = Image.fromarray((base_image[0] * 255).astype(np.uint8))
        overlay_pil = Image.fromarray((overlay_image[0] * 255).astype(np.uint8))

        # 调整修改图大小
        new_size = (int(overlay_pil.width * scale), int(overlay_pil.height * scale))
        overlay_pil = overlay_pil.resize(new_size, Image.Resampling.LANCZOS)

        # 旋转修改图
        overlay_pil = overlay_pil.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)

        # 创建预览图像
        preview = Image.new('RGBA', base_pil.size, (0, 0, 0, 0))
        
        # 转换图像模式
        if base_pil.mode != 'RGBA':
            base_pil = base_pil.convert('RGBA')
        if overlay_pil.mode != 'RGBA':
            overlay_pil = overlay_pil.convert('RGBA')

        # 应用不透明度
        if opacity < 1.0:
            overlay_pil.putalpha(int(255 * opacity))

        # 粘贴修改图
        preview.paste(overlay_pil, (position_x, position_y), overlay_pil)
        
        # 合并图层
        preview = Image.alpha_composite(base_pil, preview)

        # 转换回numpy数组
        preview_np = np.array(preview)
        preview_np = preview_np.astype(np.float32) / 255.0
        preview_np = np.expand_dims(preview_np, 0)

        return (torch.from_numpy(preview_np),) 