"""Dataset analysis models and utilities."""

from dataclasses import dataclass
from pathlib import Path

from image_dataset_audit.inspection import ImageInspection


@dataclass(frozen=True)
class ClassDistribution:
    """Class distribution statistics for an image dataset."""

    total: int
    counts: dict[str, int]
    percentages: dict[str, float]
    empty_classes: tuple[str, ...]
    
    
@dataclass(frozen=True)
class InspectionSummary:
    """Summary statistics for inspected image candidates."""

    total: int
    valid: int
    invalid: int
    format_counts: dict[str, int]
    
    
def analyze_class_distribution(
    candidates: dict[str, list[Path]],
) -> ClassDistribution:
    """Calculate class distribution statistics.

    Args:
        candidates: Image candidate paths grouped by class name.

    Returns:
        Total image candidates, counts and percentages by class,
        and the names of empty classes.
    """
    counts = {
        class_name: len(images)
        for class_name, images in candidates.items()
    }

    total = sum(counts.values())

    if total == 0:
        percentages = {
            class_name: 0.0
            for class_name in counts
        }
    else:
        percentages = {
            class_name: (count / total) * 100
            for class_name, count in counts.items()
        }

    empty_classes = tuple(
        class_name
        for class_name, count in counts.items()
        if count == 0
    )

    return ClassDistribution(
        total=total,
        counts=counts,
        percentages=percentages,
        empty_classes=empty_classes,
    )
    
    
def analyze_inspection_results(
    inspections: dict[str, list[ImageInspection]],
) -> InspectionSummary:
    """Summarize image inspection results.

    Args:
        inspections: Image inspection results grouped by class name.

    Returns:
        Total, valid and invalid image counts, plus detected
        format counts for valid images.
    """
    total = 0
    valid = 0
    invalid = 0
    format_counts: dict[str, int] = {}

    for results in inspections.values():
        for result in results:
            total += 1

            if result.status == "valid":
                valid += 1

                if result.format is not None:
                    format_counts[result.format] = (
                        format_counts.get(result.format, 0) + 1
                    )
            else:
                invalid += 1

    format_counts = dict(sorted(format_counts.items()))

    return InspectionSummary(
        total=total,
        valid=valid,
        invalid=invalid,
        format_counts=format_counts,
    )
    