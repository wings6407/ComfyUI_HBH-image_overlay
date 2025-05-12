from .image_overlay_node import ImageOverlayNode
from .image_overlay_preview_node import ImageOverlayPreviewNode
from .image_coordinate_picker_node import ImageCoordinatePickerNode
from .image_coordinate_preview_node import ImageCoordinatePreviewNode
from .image_interactive_picker_node import ImageInteractivePickerNode
from .image_preview_node import ImagePreviewNode

NODE_CLASS_MAPPINGS = {
    "HBH_ImageOverlay": ImageOverlayNode,
    "HBH_ImageOverlayPreview": ImageOverlayPreviewNode,
    "HBH_ImageCoordinatePicker": ImageCoordinatePickerNode,
    "HBH_ImageCoordinatePreview": ImageCoordinatePreviewNode,
    "HBH_ImageInteractivePicker": ImageInteractivePickerNode,
    "HBH_ImagePreview": ImagePreviewNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HBH_ImageOverlay": "HBH Image Overlay",
    "HBH_ImageOverlayPreview": "HBH Image Overlay Preview",
    "HBH_ImageCoordinatePicker": "HBH Image Coordinate Picker",
    "HBH_ImageCoordinatePreview": "HBH Image Coordinate Preview",
    "HBH_ImageInteractivePicker": "HBH Image Interactive Picker",
    "HBH_ImagePreview": "HBH Image Preview"
} 