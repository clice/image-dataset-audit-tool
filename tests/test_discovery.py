from pathlib import Path

import pytest

from image_dataset_audit.discovery import (
    discover_classes,
    validate_dataset_path,
)


def test_validate_dataset_path_returns_absolute_path(
    tmp_path: Path,
) -> None:
    result = validate_dataset_path(tmp_path)

    assert result == tmp_path.resolve()
    assert result.is_absolute()


def test_validate_dataset_path_expands_user_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()

    result = validate_dataset_path("~/dataset")

    assert result == dataset_dir.resolve()


def test_validate_dataset_path_rejects_empty_string() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_dataset_path("")


def test_validate_dataset_path_rejects_missing_path(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        validate_dataset_path(missing_path)


def test_validate_dataset_path_rejects_file(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "image.jpg"
    file_path.touch()

    with pytest.raises(NotADirectoryError, match="not a directory"):
        validate_dataset_path(file_path)
        
        
def test_discover_classes_returns_first_level_directories_sorted(
    tmp_path: Path,
) -> None:
    (tmp_path / "dogs").mkdir()
    (tmp_path / "birds").mkdir()
    (tmp_path / "cats").mkdir()

    result = discover_classes(tmp_path)

    assert [path.name for path in result] == [
        "birds",
        "cats",
        "dogs",
    ]


def test_discover_classes_ignores_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "cats").mkdir()
    (tmp_path / "README.txt").touch()

    result = discover_classes(tmp_path)

    assert [path.name for path in result] == ["cats"]


def test_discover_classes_ignores_nested_directories_as_classes(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    cats.mkdir()

    (cats / "persian").mkdir()

    result = discover_classes(tmp_path)

    assert [path.name for path in result] == ["cats"]


def test_discover_classes_returns_empty_list_when_no_classes_exist(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.txt").touch()

    result = discover_classes(tmp_path)

    assert result == []
        