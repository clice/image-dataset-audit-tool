import csv
from pathlib import Path

from PIL import Image

from image_dataset_audit.audit import audit_dataset
from image_dataset_audit.reporting import (
    render_terminal_report,
    write_csv_report,
)


def test_render_terminal_report_contains_dataset_summary(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    dogs = tmp_path / "dogs"

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

    audit = audit_dataset(tmp_path)
    report = render_terminal_report(audit)

    assert "Image Dataset Audit" in report
    assert f"Path: {tmp_path.resolve()}" in report
    assert "Classes: 2" in report
    assert "Image candidates: 3" in report

    assert "Valid: 2" in report
    assert "Invalid: 1" in report
    assert "Unsupported files: 1" in report


def test_render_terminal_report_contains_analysis_results(
    tmp_path: Path,
) -> None:
    cats = tmp_path / "cats"
    dogs = tmp_path / "dogs"

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

    audit = audit_dataset(tmp_path)
    report = render_terminal_report(audit)

    assert "cats: 1 (50.00%)" in report
    assert "dogs: 1 (50.00%)" in report

    assert "JPEG: 1" in report
    assert "PNG: 1" in report

    assert "Width: 320-640" in report
    assert "Height: 240-480" in report

    assert "Class imbalance ratio" in report
    assert "  1.00" in report


def test_render_terminal_report_handles_empty_dataset(
    tmp_path: Path,
) -> None:
    audit = audit_dataset(tmp_path)
    report = render_terminal_report(audit)

    assert "Classes: 0" in report
    assert "Image candidates: 0" in report
    assert "Valid: 0" in report
    assert "Invalid: 0" in report
    assert "Unsupported files: 0" in report

    assert "Detected formats\n  None" in report
    assert "Dimensions\n  N/A" in report
    assert "Class imbalance ratio\n  N/A" in report
    
    
def test_write_csv_report_creates_expected_columns(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    cats = dataset / "cats"

    cats.mkdir(parents=True)

    Image.new(
        "RGB",
        (640, 480),
    ).save(
        cats / "cat.jpg",
        format="JPEG",
    )

    audit = audit_dataset(dataset)

    output_path = tmp_path / "reports" / "images.csv"

    result = write_csv_report(
        audit,
        output_path,
    )

    assert result == output_path.resolve()
    assert result.exists()

    with result.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        assert reader.fieldnames == [
            "path",
            "class",
            "extension",
            "format",
            "width",
            "height",
            "status",
            "error",
        ]
        
        
def test_write_csv_report_writes_valid_image_metadata(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    cats = dataset / "cats"

    cats.mkdir(parents=True)

    Image.new(
        "RGB",
        (640, 480),
    ).save(
        cats / "cat.jpg",
        format="JPEG",
    )

    audit = audit_dataset(dataset)

    output_path = tmp_path / "images.csv"

    write_csv_report(
        audit,
        output_path,
    )

    with output_path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(
            csv.DictReader(csv_file)
        )

    assert rows == [
        {
            "path": "cats/cat.jpg",
            "class": "cats",
            "extension": ".jpg",
            "format": "JPEG",
            "width": "640",
            "height": "480",
            "status": "valid",
            "error": "",
        }
    ]
    
    
def test_write_csv_report_writes_invalid_image_metadata(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    dogs = dataset / "dogs"

    dogs.mkdir(parents=True)

    broken_path = dogs / "broken.jpg"
    broken_path.touch()

    audit = audit_dataset(dataset)

    output_path = tmp_path / "images.csv"

    write_csv_report(
        audit,
        output_path,
    )

    with output_path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(
            csv.DictReader(csv_file)
        )

    assert len(rows) == 1

    row = rows[0]

    assert row["path"] == "dogs/broken.jpg"
    assert row["class"] == "dogs"
    assert row["extension"] == ".jpg"

    assert row["format"] == ""
    assert row["width"] == ""
    assert row["height"] == ""

    assert row["status"] == "invalid"
    assert row["error"]
    
    
def test_write_csv_report_preserves_nested_relative_path(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"

    persian = dataset / "cats" / "persian"
    persian.mkdir(parents=True)

    Image.new(
        "RGB",
        (100, 100),
    ).save(
        persian / "cat.jpg",
        format="JPEG",
    )

    audit = audit_dataset(dataset)

    output_path = tmp_path / "images.csv"

    write_csv_report(
        audit,
        output_path,
    )

    with output_path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(
            csv.DictReader(csv_file)
        )

    assert rows[0]["path"] == (
        "cats/persian/cat.jpg"
    )

    assert rows[0]["class"] == "cats"
    
    
def test_write_csv_report_handles_empty_dataset(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    dataset.mkdir()

    audit = audit_dataset(dataset)

    output_path = tmp_path / "images.csv"

    write_csv_report(
        audit,
        output_path,
    )

    with output_path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(
            csv.DictReader(csv_file)
        )

    assert rows == []