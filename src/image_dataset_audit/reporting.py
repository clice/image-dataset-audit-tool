"""Dataset audit reporting utilities."""

from image_dataset_audit.audit import DatasetAudit


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
