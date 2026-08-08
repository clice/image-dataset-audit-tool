"""Image inspection models and utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image


ImageStatus = Literal["valid", "invalid"]


@dataclass(frozen=True)
class ImageInspection:
    """Result of inspecting a single image candidate."""

    path: Path
    extension: str
    format: str | None
    width: int | None
    height: int | None
    status: ImageStatus
    error: str | None = None


def inspect_image(image_path: str | Path) -> ImageInspection:
    """Inspect a valid image candidate.

    Args:
        image_path: Path to an image candidate.

    Returns:
        Metadata collected from the image.

    Raises:
        OSError: If Pillow cannot open or decode the image.
    """
    path = Path(image_path).expanduser().resolve()

    with Image.open(path) as image:
        image.load()

        image_format = image.format
        width, height = image.size

    return ImageInspection(
        path=path,
        extension=path.suffix.casefold(),
        format=image_format,
        width=width,
        height=height,
        status="valid",
    )
    