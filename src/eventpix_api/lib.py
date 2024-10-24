import io
from typing import Any

from PIL import Image


def pick_schedule_from_image(image_data: bytes) -> dict[str, Any]:
    try:
        image = Image.open(io.BytesIO(image_data))

        width, height = image.size

        return {"width": width, "height": height}
    except Exception as e:
        return {"error": str(e)}
