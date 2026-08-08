"""Image inspection models and utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


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
    