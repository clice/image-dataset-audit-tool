"""Dataset discovery utilities."""

import os
from pathlib import Path


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