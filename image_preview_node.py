import torch
import numpy as np
from PIL import Image

class ImagePreviewNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "preview"
    CATEGORY = "image/preview"
    OUTPUT_NODE = True

    def preview(self, image):
        return {}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN") 