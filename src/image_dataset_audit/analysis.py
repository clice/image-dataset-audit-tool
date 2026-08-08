"""Dataset analysis models and utilities."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClassDistribution:
    """Class distribution statistics for an image dataset."""

    total: int
    counts: dict[str, int]
    percentages: dict[str, float]
    empty_classes: tuple[str, ...]
    
    
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