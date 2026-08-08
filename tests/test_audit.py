from pathlib import Path

from PIL import Image

from image_dataset_audit.audit import audit_dataset


def test_audit_dataset_runs_complete_pipeline(
    tmp_path: Path,
) -> None:
    birds = tmp_path / "birds"
    cats = tmp_path / "cats"
    dogs = tmp_path / "dogs"

    birds.mkdir()
    cats.mkdir()
    dogs.mkdir()

    Image.new(
        "RGB",
        (640, 480),
    ).save(
        cats / "cat.jpg",
        format="JPEG",
    )

    Image.new(
        "RGB",
        (320, 240),
    ).save(
        dogs / "dog.png",
        format="PNG",
    )

    (dogs / "broken.jpg").touch()
    (dogs / "notes.txt").touch()

    result = audit_dataset(tmp_path)

    assert result.dataset_path == tmp_path.resolve()

    assert result.distribution.total == 3

    assert result.distribution.counts == {
        "birds": 0,
        "cats": 1,
        "dogs": 2,
    }

    assert result.distribution.empty_classes == (
        "birds",
    )

    assert result.inspection_summary.valid == 2
    assert result.inspection_summary.invalid == 1

    assert result.inspection_summary.format_counts == {
        "JPEG": 1,
        "PNG": 1,
    }

    assert result.dimensions.image_count == 2

    assert result.imbalance.ratio == 2.0

    assert [
        path.name
        for path in result.unsupported_files["dogs"]
    ] == ["notes.txt"]


def test_audit_dataset_handles_empty_dataset(
    tmp_path: Path,
) -> None:
    result = audit_dataset(tmp_path)

    assert result.dataset_path == tmp_path.resolve()
    assert result.distribution.total == 0
    assert result.inspection_summary.total == 0
    assert result.dimensions.image_count == 0
    assert result.imbalance.ratio is None
    assert result.candidates == {}
    assert result.inspections == {}
    assert result.unsupported_files == {}
