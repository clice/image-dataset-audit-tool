"""Command-line interface for Image Dataset Audit Tool."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from image_dataset_audit.audit import audit_dataset
from image_dataset_audit.reporting import (
    render_terminal_report,
    write_csv_report,
    write_json_report,
    write_pdf_report,
)


DEFAULT_OUTPUT_DIR = "reports"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="image-dataset-audit",
        description=(
            "Audit an image classification dataset and "
            "generate CSV, JSON, and PDF reports."
        ),
    )

    parser.add_argument(
        "dataset_path",
        help=(
            "Path to the image classification dataset "
            "root directory."
        ),
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Directory where reports will be written "
            f"(default: {DEFAULT_OUTPUT_DIR})."
        ),
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """Run the dataset audit command-line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        audit = audit_dataset(
            args.dataset_path
        )
    except (ValueError, OSError) as error:
        parser.error(str(error))

    output_dir = Path(
        args.output_dir
    ).expanduser().resolve()

    try:
        csv_path = write_csv_report(
            audit,
            output_dir / "images.csv",
        )

        json_path = write_json_report(
            audit,
            output_dir / "summary.json",
        )

        pdf_path = write_pdf_report(
            audit,
            output_dir / "audit_report.pdf",
        )
    except OSError as error:
        parser.exit(
            status=1,
            message=(
                "error: could not write reports: "
                f"{error}\n"
            ),
        )

    print(
        render_terminal_report(audit)
    )

    print()
    print("Generated reports")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  PDF: {pdf_path}")

    return 0
