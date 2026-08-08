from pathlib import Path

import pytest

from image_dataset_audit.discovery import (
    DiscoveryCounts,
    count_image_candidates,
    discover_classes,
    discover_image_candidates,
    discover_unsupported_files,
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
    
    
def test_discover_image_candidates_groups_images_by_class(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    dogs = tmp_path / "dogs"

    cats.mkdir()
    dogs.mkdir()

    (cats / "cat.jpg").touch()
    (dogs / "dog.png").touch()

    result = discover_image_candidates(tmp_path)

    assert list(result) == ["cats", "dogs"]

    assert [path.name for path in result["cats"]] == ["cat.jpg"]
    assert [path.name for path in result["dogs"]] == ["dog.png"]


def test_discover_image_candidates_is_case_insensitive(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    cats.mkdir()

    (cats / "cat.JPG").touch()
    (cats / "second.PNG").touch()

    result = discover_image_candidates(tmp_path)

    assert [path.name for path in result["cats"]] == [
        "cat.JPG",
        "second.PNG",
    ]


def test_discover_image_candidates_ignores_unsupported_files(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    cats.mkdir()

    (cats / "cat.jpg").touch()
    (cats / "notes.txt").touch()
    (cats / "metadata.csv").touch()

    result = discover_image_candidates(tmp_path)

    assert [path.name for path in result["cats"]] == ["cat.jpg"]


def test_discover_image_candidates_scans_class_recursively(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    nested = cats / "persian"

    nested.mkdir(parents=True)

    (cats / "cat_01.jpg").touch()
    (nested / "cat_02.jpg").touch()

    result = discover_image_candidates(tmp_path)

    relative_paths = [
        path.relative_to(cats).as_posix()
        for path in result["cats"]
    ]

    assert relative_paths == [
        "cat_01.jpg",
        "persian/cat_02.jpg",
    ]


def test_discover_image_candidates_preserves_empty_classes(
    tmp_path: Path,
) -> None:
    (tmp_path / "birds").mkdir()

    result = discover_image_candidates(tmp_path)

    assert result == {"birds": []}
        
        
        
def test_count_image_candidates_returns_total_and_per_class() -> None:
    candidates = {
        "birds": [],
        "cats": [
            Path("/dataset/cats/cat_01.jpg"),
            Path("/dataset/cats/cat_02.jpg"),
            Path("/dataset/cats/cat_03.png"),
        ],
        "dogs": [
            Path("/dataset/dogs/dog_01.jpg"),
            Path("/dataset/dogs/dog_02.webp"),
        ],
    }

    result = count_image_candidates(candidates)

    assert result == DiscoveryCounts(
        total=5,
        by_class={
            "birds": 0,
            "cats": 3,
            "dogs": 2,
        },
    )


def test_count_image_candidates_handles_empty_dataset() -> None:
    result = count_image_candidates({})

    assert result == DiscoveryCounts(
        total=0,
        by_class={},
    )


def test_count_image_candidates_preserves_empty_classes() -> None:
    candidates = {
        "birds": [],
        "cats": [Path("/dataset/cats/cat.jpg")],
    }

    result = count_image_candidates(candidates)

    assert result.by_class == {
        "birds": 0,
        "cats": 1,
    }
    assert result.total == 1
    
    
def test_discover_unsupported_files_groups_files_by_class(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    dogs = tmp_path / "dogs"

    cats.mkdir()
    dogs.mkdir()

    (cats / "notes.txt").touch()
    (dogs / "metadata.csv").touch()

    result = discover_unsupported_files(tmp_path)

    assert [path.name for path in result["cats"]] == ["notes.txt"]
    assert [path.name for path in result["dogs"]] == ["metadata.csv"]


def test_discover_unsupported_files_ignores_supported_images(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    cats.mkdir()

    (cats / "cat.jpg").touch()
    (cats / "notes.txt").touch()

    result = discover_unsupported_files(tmp_path)

    assert [path.name for path in result["cats"]] == ["notes.txt"]


def test_discover_unsupported_files_ignores_root_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "cats").mkdir()
    (tmp_path / "README.txt").touch()

    result = discover_unsupported_files(tmp_path)

    assert result == {"cats": []}