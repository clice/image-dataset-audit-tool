"""Image inspection models and utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, UnidentifiedImageError


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
    """Inspect an image candidate.

    Args:
        image_path: Path to an image candidate.

    Returns:
        Metadata collected from the image. Invalid or unreadable
        images are returned with status ``invalid`` instead of
        interrupting the audit.
    """
    path = Path(image_path).expanduser().resolve()
    extension = path.suffix.casefold()

    try:
        with Image.open(path) as image:
            image.load()

            image_format = image.format
            width, height = image.size

    except (UnidentifiedImageError, OSError) as exc:
        return ImageInspection(
            path=path,
            extension=extension,
            format=None,
            width=None,
            height=None,
            status="invalid",
            error=str(exc),
        )

    return ImageInspection(
        path=path,
        extension=extension,
        format=image_format,
        width=width,
        height=height,
        status="valid",
    )
    