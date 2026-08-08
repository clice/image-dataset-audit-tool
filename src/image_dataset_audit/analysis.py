"""Dataset analysis models and utilities."""

from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

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


@dataclass(frozen=True)
class DimensionStatistics:
    """Descriptive statistics for valid image dimensions."""

    image_count: int
    min_width: int | None
    max_width: int | None
    mean_width: float | None
    median_width: float | None
    min_height: int | None
    max_height: int | None
    mean_height: float | None
    median_height: float | None


@dataclass(frozen=True)
class ImbalanceIndicator:
    """Descriptive class imbalance indicator."""

    non_empty_class_count: int
    largest_class_count: int | None
    smallest_class_count: int | None
    ratio: float | None


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


def analyze_dimensions(
    inspections: dict[str, list[ImageInspection]],
) -> DimensionStatistics:
    """Calculate descriptive statistics for valid image dimensions.

    Args:
        inspections: Image inspection results grouped by class name.

    Returns:
        Minimum, maximum, mean and median width and height values
        calculated from valid images with available dimensions.
    """
    widths: list[int] = []
    heights: list[int] = []

    for results in inspections.values():
        for result in results:
            if (
                result.status == "valid"
                and result.width is not None
                and result.height is not None
            ):
                widths.append(result.width)
                heights.append(result.height)

    if not widths:
        return DimensionStatistics(
            image_count=0,
            min_width=None,
            max_width=None,
            mean_width=None,
            median_width=None,
            min_height=None,
            max_height=None,
            mean_height=None,
            median_height=None,
        )

    return DimensionStatistics(
        image_count=len(widths),
        min_width=min(widths),
        max_width=max(widths),
        mean_width=mean(widths),
        median_width=median(widths),
        min_height=min(heights),
        max_height=max(heights),
        mean_height=mean(heights),
        median_height=median(heights),
    )


def analyze_class_imbalance(
    distribution: ClassDistribution,
) -> ImbalanceIndicator:
    """Calculate a descriptive class imbalance ratio.

    The ratio is defined as the largest class count divided by the
    smallest non-empty class count. Empty classes are excluded from
    the ratio calculation.

    Args:
        distribution: Previously calculated class distribution.

    Returns:
        Counts used in the calculation and the descriptive ratio.
        The ratio is ``None`` when fewer than two non-empty classes
        are available for comparison.
    """
    non_empty_counts = [
        count
        for count in distribution.counts.values()
        if count > 0
    ]

    if len(non_empty_counts) < 2:
        return ImbalanceIndicator(
            non_empty_class_count=len(non_empty_counts),
            largest_class_count=(
                non_empty_counts[0]
                if non_empty_counts
                else None
            ),
            smallest_class_count=(
                non_empty_counts[0]
                if non_empty_counts
                else None
            ),
            ratio=None,
        )

    largest = max(non_empty_counts)
    smallest = min(non_empty_counts)

    return ImbalanceIndicator(
        non_empty_class_count=len(non_empty_counts),
        largest_class_count=largest,
        smallest_class_count=smallest,
        ratio=largest / smallest,
    )
