from pathlib import Path

import pytest
from PIL import Image

from image_dataset_audit.cli import main


def _create_test_dataset(
    tmp_path: Path,
) -> Path:
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

    return dataset


def test_cli_generates_reports_in_default_directory(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    dataset = _create_test_dataset(
        tmp_path
    )

    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            str(dataset),
        ]
    )

    assert exit_code == 0

    reports = tmp_path / "reports"

    assert (
        reports / "images.csv"
    ).exists()

    assert (
        reports / "summary.json"
    ).exists()

    assert (
        reports / "audit_report.pdf"
    ).exists()

    captured = capsys.readouterr()

    assert (
        "Image Dataset Audit"
        in captured.out
    )

    assert (
        "Generated reports"
        in captured.out
    )


def test_cli_uses_custom_output_directory(
    tmp_path: Path,
) -> None:
    dataset = _create_test_dataset(
        tmp_path
    )

    output_dir = (
        tmp_path
        / "custom-reports"
    )

    exit_code = main(
        [
            str(dataset),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0

    assert (
        output_dir / "images.csv"
    ).exists()

    assert (
        output_dir / "summary.json"
    ).exists()

    assert (
        output_dir / "audit_report.pdf"
    ).exists()


def test_cli_rejects_missing_dataset(
    tmp_path: Path,
    capsys,
) -> None:
    missing_dataset = (
        tmp_path
        / "missing"
    )

    with pytest.raises(
        SystemExit
    ) as error:
        main(
            [
                str(missing_dataset),
            ]
        )

    assert error.value.code == 2

    captured = capsys.readouterr()

    assert (
        "Dataset path does not exist"
        in captured.err
    )
