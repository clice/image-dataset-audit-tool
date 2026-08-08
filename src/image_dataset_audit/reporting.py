"""Dataset audit reporting utilities."""

import csv
import json
from pathlib import Path

from image_dataset_audit.audit import DatasetAudit


CSV_FIELDS = (
    "path",
    "class",
    "extension",
    "format",
    "width",
    "height",
    "status",
    "error",
)


def render_terminal_report(audit: DatasetAudit) -> str:
    """Render a human-readable dataset audit summary.

    Args:
        audit: Complete dataset audit result.

    Returns:
        Formatted terminal report.
    """
    unsupported_total = sum(
        len(files)
        for files in audit.unsupported_files.values()
    )

    lines = [
        "Image Dataset Audit",
        "===================",
        "",
        "Dataset",
        f"  Path: {audit.dataset_path}",
        f"  Classes: {len(audit.distribution.counts)}",
        f"  Image candidates: {audit.distribution.total}",
        "",
        "Image integrity",
        f"  Valid: {audit.inspection_summary.valid}",
        f"  Invalid: {audit.inspection_summary.invalid}",
        f"  Unsupported files: {unsupported_total}",
        "",
        "Class distribution",
    ]

    if audit.distribution.counts:
        for class_name, count in audit.distribution.counts.items():
            percentage = audit.distribution.percentages[class_name]

            lines.append(
                f"  {class_name}: "
                f"{count} ({percentage:.2f}%)"
            )
    else:
        lines.append("  None")

    lines.extend(
        [
            "",
            "Empty classes",
        ]
    )

    if audit.distribution.empty_classes:
        for class_name in audit.distribution.empty_classes:
            lines.append(f"  {class_name}")
    else:
        lines.append("  None")

    lines.extend(
        [
            "",
            "Detected formats",
        ]
    )

    if audit.inspection_summary.format_counts:
        for image_format, count in (
            audit.inspection_summary.format_counts.items()
        ):
            lines.append(
                f"  {image_format}: {count}"
            )
    else:
        lines.append("  None")

    lines.extend(
        [
            "",
            "Dimensions",
        ]
    )

    dimensions = audit.dimensions

    if dimensions.image_count > 0:
        lines.extend(
            [
                (
                    "  Width: "
                    f"{dimensions.min_width}-"
                    f"{dimensions.max_width}"
                ),
                (
                    "  Height: "
                    f"{dimensions.min_height}-"
                    f"{dimensions.max_height}"
                ),
                (
                    "  Mean width: "
                    f"{dimensions.mean_width:.2f}"
                ),
                (
                    "  Mean height: "
                    f"{dimensions.mean_height:.2f}"
                ),
                (
                    "  Median width: "
                    f"{dimensions.median_width:.2f}"
                ),
                (
                    "  Median height: "
                    f"{dimensions.median_height:.2f}"
                ),
            ]
        )
    else:
        lines.append("  N/A")

    lines.extend(
        [
            "",
            "Class imbalance ratio",
        ]
    )

    if audit.imbalance.ratio is None:
        lines.append("  N/A")
    else:
        lines.append(
            f"  {audit.imbalance.ratio:.2f}"
        )

    return "\n".join(lines)


def _format_report_error(
    error: str | None,
    image_path: Path,
    dataset_path: Path,
) -> str | None:
    """Replace absolute image paths in errors with dataset-relative paths."""
    if error is None:
        return None

    relative_path = image_path.relative_to(
        dataset_path
    ).as_posix()

    return error.replace(
        str(image_path),
        relative_path,
    )


def write_csv_report(
    audit: DatasetAudit,
    output_path: str | Path,
) -> Path:
    """Write detailed image inspection results to CSV.

    Args:
        audit: Complete dataset audit result.
        output_path: Destination path for the CSV report.

    Returns:
        Absolute path to the generated CSV file.
    """
    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDS,
        )

        writer.writeheader()

        for class_name, results in audit.inspections.items():
            for result in results:
                relative_path = result.path.relative_to(
                    audit.dataset_path
                )

                writer.writerow(
                    {
                        "path": relative_path.as_posix(),
                        "class": class_name,
                        "extension": result.extension,
                        "format": result.format,
                        "width": result.width,
                        "height": result.height,
                        "status": result.status,
                        "error": _format_report_error(
                            result.error,
                            result.path,
                            audit.dataset_path,
                        ),
                    }
                )

    return path


def build_json_summary(
    audit: DatasetAudit,
) -> dict[str, object]:
    """Build a structured JSON-compatible audit summary.

    Args:
        audit: Complete dataset audit result.

    Returns:
        JSON-compatible dictionary containing dataset audit statistics.
    """
    class_distribution = {
        class_name: {
            "count": count,
            "percentage": audit.distribution.percentages[class_name],
        }
        for class_name, count in audit.distribution.counts.items()
    }

    unsupported_by_class = {
        class_name: [
            file_path.relative_to(
                audit.dataset_path
            ).as_posix()
            for file_path in files
        ]
        for class_name, files in audit.unsupported_files.items()
    }

    unsupported_total = sum(
        len(files)
        for files in audit.unsupported_files.values()
    )

    dimensions = audit.dimensions
    imbalance = audit.imbalance

    return {
        "dataset": {
            "name": audit.dataset_path.name,
            "class_count": len(audit.distribution.counts),
            "total_candidates": audit.distribution.total,
        },
        "integrity": {
            "valid": audit.inspection_summary.valid,
            "invalid": audit.inspection_summary.invalid,
        },
        "class_distribution": class_distribution,
        "empty_classes": list(
            audit.distribution.empty_classes
        ),
        "formats": audit.inspection_summary.format_counts,
        "dimensions": {
            "image_count": dimensions.image_count,
            "width": {
                "min": dimensions.min_width,
                "max": dimensions.max_width,
                "mean": dimensions.mean_width,
                "median": dimensions.median_width,
            },
            "height": {
                "min": dimensions.min_height,
                "max": dimensions.max_height,
                "mean": dimensions.mean_height,
                "median": dimensions.median_height,
            },
        },
        "imbalance": {
            "non_empty_class_count": (
                imbalance.non_empty_class_count
            ),
            "largest_class_count": (
                imbalance.largest_class_count
            ),
            "smallest_class_count": (
                imbalance.smallest_class_count
            ),
            "ratio": imbalance.ratio,
        },
        "unsupported_files": {
            "total": unsupported_total,
            "by_class": unsupported_by_class,
        },
    }
    
    
def write_json_report(
    audit: DatasetAudit,
    output_path: str | Path,
) -> Path:
    """Write the structured dataset audit summary to JSON.

    Args:
        audit: Complete dataset audit result.
        output_path: Destination path for the JSON report.

    Returns:
        Absolute path to the generated JSON file.
    """
    path = Path(output_path).expanduser().resolve()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = build_json_summary(audit)

    with path.open(
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(
            summary,
            json_file,
            indent=2,
            ensure_ascii=False,
        )

        json_file.write("\n")

    return path
