"""Dataset discovery utilities."""

import os
from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    }
)


def validate_dataset_path(dataset_path: str | Path) -> Path:
    """Validate and normalize a dataset directory path.

    Args:
        dataset_path: Path to the dataset root directory.

    Returns:
        The validated dataset path as an absolute ``Path``.

    Raises:
        ValueError: If the provided path is an empty string.
        FileNotFoundError: If the path does not exist.
        NotADirectoryError: If the path exists but is not a directory.
        PermissionError: If the directory cannot be read or traversed.
    """
    if isinstance(dataset_path, str) and not dataset_path.strip():
        raise ValueError("Dataset path cannot be empty.")

    path = Path(dataset_path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {path}")

    if not path.is_dir():
        raise NotADirectoryError(
            f"Dataset path is not a directory: {path}"
        )

    if not os.access(path, os.R_OK | os.X_OK):
        raise PermissionError(
            f"Dataset directory cannot be accessed: {path}"
        )

    return path.resolve()


def discover_classes(dataset_path: str | Path) -> list[Path]:
    """Discover first-level class directories in a dataset.

    Args:
        dataset_path: Path to the dataset root directory.

    Returns:
        A deterministically ordered list of class directories.
    """
    root = validate_dataset_path(dataset_path)

    classes = [
        entry
        for entry in root.iterdir()
        if entry.is_dir()
    ]

    return sorted(
        classes,
        key=lambda path: (path.name.casefold(), path.name),
    )
    
    
def discover_image_candidates(
    dataset_path: str | Path,
) -> dict[str, list[Path]]:
    """Discover supported image candidates grouped by class.

    Args:
        dataset_path: Path to the dataset root directory.

    Returns:
        A dictionary mapping each class name to a deterministically
        ordered list of image candidate paths.
    """
    classes = discover_classes(dataset_path)

    candidates: dict[str, list[Path]] = {}

    for class_path in classes:
        class_candidates = [
            path
            for path in class_path.rglob("*")
            if path.is_file()
            and path.suffix.casefold() in SUPPORTED_IMAGE_EXTENSIONS
        ]

        candidates[class_path.name] = sorted(
            class_candidates,
            key=lambda path: (
                path.relative_to(class_path).as_posix().casefold(),
                path.relative_to(class_path).as_posix(),
            ),
        )

    return candidates
    