import csv
import json
import pytest
from pathlib import Path

from PIL import Image

from image_dataset_audit.audit import audit_dataset
from image_dataset_audit.reporting import (
    build_json_summary,
    render_terminal_report,
    write_csv_report,
    write_json_report,
    write_pdf_report,
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
    assert "dogs/broken.jpg" in row["error"]
    assert str(dataset.resolve()) not in row["error"]


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


def test_build_json_summary_contains_dataset_statistics(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    birds = dataset / "birds"
    cats = dataset / "cats"
    dogs = dataset / "dogs"

    birds.mkdir(parents=True)
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

    audit = audit_dataset(dataset)
    summary = build_json_summary(audit)

    assert summary["dataset"] == {
        "name": "dataset",
        "class_count": 3,
        "total_candidates": 3,
    }

    assert summary["integrity"] == {
        "valid": 2,
        "invalid": 1,
    }

    assert summary["empty_classes"] == [
        "birds",
    ]

    assert summary["formats"] == {
        "JPEG": 1,
        "PNG": 1,
    }


def test_build_json_summary_contains_distribution_and_imbalance(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    cats = dataset / "cats"
    dogs = dataset / "dogs"

    cats.mkdir(parents=True)
    dogs.mkdir()

    Image.new(
        "RGB",
        (100, 100),
    ).save(
        cats / "cat.jpg",
        format="JPEG",
    )

    Image.new(
        "RGB",
        (100, 100),
    ).save(
        dogs / "dog_01.jpg",
        format="JPEG",
    )

    Image.new(
        "RGB",
        (100, 100),
    ).save(
        dogs / "dog_02.jpg",
        format="JPEG",
    )

    audit = audit_dataset(dataset)
    summary = build_json_summary(audit)

    assert summary["class_distribution"] == {
        "cats": {
            "count": 1,
            "percentage": pytest.approx(100 / 3),
        },
        "dogs": {
            "count": 2,
            "percentage": pytest.approx(200 / 3),
        },
    }

    assert summary["imbalance"] == {
        "non_empty_class_count": 2,
        "largest_class_count": 2,
        "smallest_class_count": 1,
        "ratio": 2.0,
    }


def test_build_json_summary_contains_dimension_statistics(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    images = dataset / "images"

    images.mkdir(parents=True)

    Image.new(
        "RGB",
        (100, 50),
    ).save(
        images / "small.jpg",
        format="JPEG",
    )

    Image.new(
        "RGB",
        (300, 250),
    ).save(
        images / "large.jpg",
        format="JPEG",
    )

    audit = audit_dataset(dataset)
    summary = build_json_summary(audit)

    assert summary["dimensions"] == {
        "image_count": 2,
        "width": {
            "min": 100,
            "max": 300,
            "mean": 200,
            "median": 200.0,
        },
        "height": {
            "min": 50,
            "max": 250,
            "mean": 150,
            "median": 150.0,
        },
    }


def test_build_json_summary_uses_relative_unsupported_paths(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    cats = dataset / "cats"

    cats.mkdir(parents=True)

    unsupported_path = cats / "notes.txt"
    unsupported_path.touch()

    audit = audit_dataset(dataset)
    summary = build_json_summary(audit)

    assert summary["unsupported_files"] == {
        "total": 1,
        "by_class": {
            "cats": [
                "cats/notes.txt",
            ],
        },
    }

    assert str(dataset.resolve()) not in str(summary)


def test_write_json_report_creates_valid_json(
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

    output_path = (
        tmp_path
        / "reports"
        / "summary.json"
    )

    result = write_json_report(
        audit,
        output_path,
    )

    assert result == output_path.resolve()
    assert result.exists()

    with result.open(
        encoding="utf-8",
    ) as json_file:
        data = json.load(json_file)

    assert data["dataset"]["name"] == "dataset"
    assert data["dataset"]["total_candidates"] == 1
    assert data["integrity"]["valid"] == 1


def test_build_json_summary_handles_empty_dataset(
    tmp_path: Path,
) -> None:
    audit = audit_dataset(tmp_path)

    summary = build_json_summary(audit)

    assert summary["dataset"] == {
        "name": tmp_path.name,
        "class_count": 0,
        "total_candidates": 0,
    }

    assert summary["integrity"] == {
        "valid": 0,
        "invalid": 0,
    }

    assert summary["class_distribution"] == {}
    assert summary["empty_classes"] == []
    assert summary["formats"] == {}

    assert summary["dimensions"]["image_count"] == 0
    assert summary["dimensions"]["width"]["min"] is None
    assert summary["dimensions"]["height"]["min"] is None

    assert summary["imbalance"]["ratio"] is None

    assert summary["unsupported_files"] == {
        "total": 0,
        "by_class": {},
    }


def test_write_pdf_report_creates_pdf_file(
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

    output_path = (
        tmp_path
        / "reports"
        / "audit_report.pdf"
    )

    result = write_pdf_report(
        audit,
        output_path,
    )

    assert result == output_path.resolve()
    assert result.exists()
    assert result.stat().st_size > 0

    with result.open("rb") as pdf_file:
        assert pdf_file.read(4) == b"%PDF"


def test_write_pdf_report_handles_empty_dataset(
    tmp_path: Path,
) -> None:
    audit = audit_dataset(tmp_path)

    output_path = (
        tmp_path
        / "audit_report.pdf"
    )

    result = write_pdf_report(
        audit,
        output_path,
    )

    assert result.exists()
    assert result.stat().st_size > 0

    with result.open("rb") as pdf_file:
        assert pdf_file.read(4) == b"%PDF"
