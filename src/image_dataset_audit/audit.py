"""Dataset audit orchestration."""

from dataclasses import dataclass
from pathlib import Path

from image_dataset_audit.analysis import (
    ClassDistribution,
    DimensionStatistics,
    ImbalanceIndicator,
    InspectionSummary,
    analyze_class_distribution,
    analyze_class_imbalance,
    analyze_dimensions,
    analyze_inspection_results,
)
from image_dataset_audit.discovery import (
    discover_image_candidates,
    discover_unsupported_files,
    validate_dataset_path,
)
from image_dataset_audit.inspection import (
    ImageInspection,
    inspect_image_candidates,
)


@dataclass(frozen=True)
class DatasetAudit:
    """Complete result of auditing an image dataset."""

    dataset_path: Path
    candidates: dict[str, list[Path]]
    unsupported_files: dict[str, list[Path]]
    inspections: dict[str, list[ImageInspection]]
    distribution: ClassDistribution
    inspection_summary: InspectionSummary
    dimensions: DimensionStatistics
    imbalance: ImbalanceIndicator


def audit_dataset(
    dataset_path: str | Path,
) -> DatasetAudit:
    """Run the complete dataset audit pipeline.

    Args:
        dataset_path: Path to the image classification dataset.

    Returns:
        Complete discovery, inspection and analysis results.
    """
    path = validate_dataset_path(dataset_path)

    candidates = discover_image_candidates(path)
    unsupported_files = discover_unsupported_files(path)

    inspections = inspect_image_candidates(candidates)

    distribution = analyze_class_distribution(candidates)
    inspection_summary = analyze_inspection_results(inspections)
    dimensions = analyze_dimensions(inspections)
    imbalance = analyze_class_imbalance(distribution)

    return DatasetAudit(
        dataset_path=path,
        candidates=candidates,
        unsupported_files=unsupported_files,
        inspections=inspections,
        distribution=distribution,
        inspection_summary=inspection_summary,
        dimensions=dimensions,
        imbalance=imbalance,
    )
    