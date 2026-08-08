from pathlib import Path

from PIL import Image

from image_dataset_audit.audit import audit_dataset
from image_dataset_audit.reporting import render_terminal_report


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