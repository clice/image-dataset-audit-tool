"""Dataset audit reporting utilities."""

import csv
import json
from pathlib import Path

from image_dataset_audit.audit import DatasetAudit
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure


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


PDF_PAGE_SIZE = (
    8.27,
    11.69,
)


def _style_pdf_table(
    table: object,
) -> None:
    """Apply consistent styling to a PDF table."""
    for (row_index, _), cell in table.get_celld().items():
        cell.set_linewidth(0.5)
        cell.PAD = 0.08

        if row_index == 0:
            cell.get_text().set_fontweight(
                "bold"
            )


def _add_pdf_table(
    axis: object,
    headers: list[str],
    rows: list[list[str]],
    bbox: list[float],
    font_size: float = 10.0,
) -> None:
    """Add a styled table to a PDF page."""
    table = axis.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="left",
        colLoc="left",
        bbox=bbox,
    )

    table.auto_set_font_size(False)
    table.set_fontsize(font_size)

    _style_pdf_table(table)


def _add_pdf_overview_page(
    pdf: PdfPages,
    audit: DatasetAudit,
    unsupported_total: int,
) -> None:
    """Add the dataset overview page."""
    figure = Figure(
        figsize=PDF_PAGE_SIZE,
    )

    axis = figure.subplots()
    axis.axis("off")

    axis.text(
        0.05,
        0.95,
        "Image Dataset Audit",
        fontsize=20,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    axis.text(
        0.05,
        0.90,
        audit.dataset_path.name,
        fontsize=12,
        va="top",
        transform=axis.transAxes,
    )

    axis.text(
        0.05,
        0.83,
        "Dataset Overview",
        fontsize=14,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    empty_classes = (
        ", ".join(
            audit.distribution.empty_classes
        )
        if audit.distribution.empty_classes
        else "None"
    )

    overview_rows = [
        [
            "Classes",
            str(
                len(
                    audit.distribution.counts
                )
            ),
        ],
        [
            "Image candidates",
            str(
                audit.distribution.total
            ),
        ],
        [
            "Valid images",
            str(
                audit.inspection_summary.valid
            ),
        ],
        [
            "Invalid images",
            str(
                audit.inspection_summary.invalid
            ),
        ],
        [
            "Unsupported files",
            str(unsupported_total),
        ],
        [
            "Empty classes",
            empty_classes,
        ],
    ]

    _add_pdf_table(
        axis,
        [
            "Metric",
            "Value",
        ],
        overview_rows,
        [
            0.05,
            0.48,
            0.90,
            0.30,
        ],
        font_size=10.5,
    )

    axis.text(
        0.05,
        0.41,
        "Quality Observations",
        fontsize=14,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    observations = []

    if audit.distribution.empty_classes:
        observations.append(
            "Empty classes detected: "
            + ", ".join(
                audit.distribution.empty_classes
            )
        )
    else:
        observations.append(
            "No empty classes detected."
        )

    observations.append(
        "Invalid image candidates: "
        f"{audit.inspection_summary.invalid}"
    )

    observations.append(
        "Unsupported files: "
        f"{unsupported_total}"
    )

    observation_text = "\n".join(
        f"- {observation}"
        for observation in observations
    )

    axis.text(
        0.07,
        0.36,
        observation_text,
        fontsize=10.5,
        va="top",
        linespacing=1.6,
        transform=axis.transAxes,
    )

    axis.text(
        0.05,
        0.08,
        (
            "The audit is read-only and does not "
            "modify the source dataset."
        ),
        fontsize=9,
        va="bottom",
        transform=axis.transAxes,
    )

    pdf.savefig(figure)


def _add_pdf_distribution_page(
    pdf: PdfPages,
    audit: DatasetAudit,
) -> None:
    """Add class distribution analysis to the PDF."""
    figure = Figure(
        figsize=PDF_PAGE_SIZE,
    )

    figure.text(
        0.07,
        0.94,
        "Class Distribution",
        fontsize=20,
        fontweight="bold",
        va="top",
    )

    class_names = list(
        audit.distribution.counts.keys()
    )

    class_counts = list(
        audit.distribution.counts.values()
    )

    if class_names:
        chart_axis = figure.add_axes(
            [
                0.16,
                0.61,
                0.75,
                0.22,
            ]
        )

        chart_axis.barh(
            class_names,
            class_counts,
        )

        chart_axis.invert_yaxis()

        chart_axis.set_xlabel(
            "Image candidates"
        )

        chart_axis.grid(
            axis="x",
            alpha=0.2,
        )

        chart_axis.spines[
            "top"
        ].set_visible(False)

        chart_axis.spines[
            "right"
        ].set_visible(False)

        maximum = max(
            class_counts,
            default=0,
        )

        chart_axis.set_xlim(
            0,
            max(
                1,
                maximum * 1.25,
            ),
        )

        label_offset = max(
            0.04,
            maximum * 0.025,
        )

        for index, count in enumerate(
            class_counts
        ):
            chart_axis.text(
                count + label_offset,
                index,
                str(count),
                va="center",
                fontsize=9,
            )
    else:
        figure.text(
            0.07,
            0.72,
            "No classes were detected.",
            fontsize=11,
        )

    table_axis = figure.add_axes(
        [
            0.08,
            0.29,
            0.84,
            0.23,
        ]
    )

    table_axis.axis("off")

    if class_names:
        distribution_rows = []

        for class_name, count in (
            audit.distribution.counts.items()
        ):
            percentage = (
                audit.distribution
                .percentages[class_name]
            )

            status = (
                "Empty"
                if count == 0
                else "Non-empty"
            )

            distribution_rows.append(
                [
                    class_name,
                    str(count),
                    f"{percentage:.2f}%",
                    status,
                ]
            )
    else:
        distribution_rows = [
            [
                "None",
                "0",
                "0.00%",
                "N/A",
            ]
        ]

    _add_pdf_table(
        table_axis,
        [
            "Class",
            "Candidates",
            "Share",
            "Status",
        ],
        distribution_rows,
        [
            0.00,
            0.00,
            1.00,
            1.00,
        ],
        font_size=9.5,
    )

    imbalance = audit.imbalance

    figure.text(
        0.08,
        0.22,
        "Class Imbalance",
        fontsize=13,
        fontweight="bold",
        va="top",
    )

    if imbalance.ratio is None:
        imbalance_text = (
            "Ratio: N/A\n"
            "At least two non-empty classes "
            "are required."
        )
    else:
        imbalance_text = (
            f"Ratio: {imbalance.ratio:.2f}\n"
            "Largest class: "
            f"{imbalance.largest_class_count} "
            "images\n"
            "Smallest non-empty class: "
            f"{imbalance.smallest_class_count} "
            "images\n"
            "Descriptive indicator only; "
            "no universal imbalance threshold "
            "is applied."
        )

    figure.text(
        0.08,
        0.18,
        imbalance_text,
        fontsize=9.5,
        va="top",
        linespacing=1.5,
    )

    pdf.savefig(figure)


def _add_pdf_quality_page(
    pdf: PdfPages,
    audit: DatasetAudit,
) -> None:
    """Add integrity, formats and dimensions tables."""
    figure = Figure(
        figsize=PDF_PAGE_SIZE,
    )

    axis = figure.subplots()
    axis.axis("off")

    axis.text(
        0.05,
        0.95,
        "Image Properties & Quality",
        fontsize=20,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    axis.text(
        0.05,
        0.87,
        "Image Integrity",
        fontsize=14,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    integrity_rows = [
        [
            "Valid",
            str(
                audit.inspection_summary.valid
            ),
        ],
        [
            "Invalid",
            str(
                audit.inspection_summary.invalid
            ),
        ],
    ]

    _add_pdf_table(
        axis,
        [
            "Status",
            "Count",
        ],
        integrity_rows,
        [
            0.05,
            0.69,
            0.42,
            0.14,
        ],
        font_size=10,
    )

    axis.text(
        0.53,
        0.87,
        "Detected Formats",
        fontsize=14,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    format_counts = (
        audit.inspection_summary.format_counts
    )

    if format_counts:
        format_rows = [
            [
                image_format,
                str(count),
            ]
            for image_format, count
            in format_counts.items()
        ]
    else:
        format_rows = [
            [
                "None",
                "0",
            ]
        ]

    _add_pdf_table(
        axis,
        [
            "Format",
            "Valid images",
        ],
        format_rows,
        [
            0.53,
            0.61,
            0.42,
            0.22,
        ],
        font_size=10,
    )

    axis.text(
        0.05,
        0.53,
        "Dimension Statistics",
        fontsize=14,
        fontweight="bold",
        va="top",
        transform=axis.transAxes,
    )

    dimensions = audit.dimensions

    if dimensions.image_count > 0:
        dimension_rows = [
            [
                "Minimum",
                str(dimensions.min_width),
                str(dimensions.min_height),
            ],
            [
                "Maximum",
                str(dimensions.max_width),
                str(dimensions.max_height),
            ],
            [
                "Mean",
                f"{dimensions.mean_width:.2f}",
                f"{dimensions.mean_height:.2f}",
            ],
            [
                "Median",
                f"{dimensions.median_width:.2f}",
                f"{dimensions.median_height:.2f}",
            ],
        ]
    else:
        dimension_rows = [
            [
                "Minimum",
                "N/A",
                "N/A",
            ],
            [
                "Maximum",
                "N/A",
                "N/A",
            ],
            [
                "Mean",
                "N/A",
                "N/A",
            ],
            [
                "Median",
                "N/A",
                "N/A",
            ],
        ]

    _add_pdf_table(
        axis,
        [
            "Statistic",
            "Width",
            "Height",
        ],
        dimension_rows,
        [
            0.05,
            0.27,
            0.90,
            0.21,
        ],
        font_size=10,
    )

    axis.text(
        0.05,
        0.21,
        (
            "Images with valid dimensions: "
            f"{dimensions.image_count}"
        ),
        fontsize=9.5,
        va="top",
        transform=axis.transAxes,
    )

    axis.text(
        0.05,
        0.16,
        (
            "Dimension statistics are calculated "
            "from valid images only."
        ),
        fontsize=9,
        va="top",
        transform=axis.transAxes,
    )

    pdf.savefig(figure)


def write_pdf_report(
    audit: DatasetAudit,
    output_path: str | Path,
) -> Path:
    """Write a compact multi-page dataset audit report to PDF.

    Args:
        audit: Complete dataset audit result.
        output_path: Destination path for the PDF report.

    Returns:
        Absolute path to the generated PDF file.
    """
    path = Path(output_path).expanduser().resolve()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    unsupported_total = sum(
        len(files)
        for files in audit.unsupported_files.values()
    )

    metadata = {
        "Title": "Image Dataset Audit Report",
        "Subject": (
            "Image classification dataset quality audit"
        ),
        "Creator": "Image Dataset Audit Tool",
    }

    with PdfPages(
        path,
        metadata=metadata,
    ) as pdf:
        _add_pdf_overview_page(
            pdf,
            audit,
            unsupported_total,
        )

        _add_pdf_distribution_page(
            pdf,
            audit,
        )

        _add_pdf_quality_page(
            pdf,
            audit,
        )

    return path
