from pathlib import Path

import pytest

from image_dataset_audit.analysis import (
    ClassDistribution,
    DimensionStatistics,
    InspectionSummary,
    analyze_class_distribution,
    analyze_dimensions,
    analyze_inspection_results,
)

from image_dataset_audit.inspection import ImageInspection


def test_analyze_class_distribution_calculates_counts_and_percentages() -> None:
    candidates = {
        "birds": [],
        "cats": [
            Path("/dataset/cats/cat_01.jpg"),
            Path("/dataset/cats/cat_02.jpg"),
            Path("/dataset/cats/cat_03.jpg"),
            Path("/dataset/cats/cat_04.jpg"),
            Path("/dataset/cats/cat_05.jpg"),
        ],
        "dogs": [
            Path("/dataset/dogs/dog_01.jpg"),
            Path("/dataset/dogs/dog_02.jpg"),
            Path("/dataset/dogs/dog_03.jpg"),
        ],
    }

    result = analyze_class_distribution(candidates)

    assert result.total == 8

    assert result.counts == {
        "birds": 0,
        "cats": 5,
        "dogs": 3,
    }

    assert result.percentages["birds"] == 0.0
    assert result.percentages["cats"] == pytest.approx(62.5)
    assert result.percentages["dogs"] == pytest.approx(37.5)

    assert result.empty_classes == ("birds",)
    
    
def test_analyze_class_distribution_handles_all_empty_classes() -> None:
    candidates: dict[str, list[Path]] = {
        "birds": [],
        "cats": [],
    }

    result = analyze_class_distribution(candidates)

    assert result.total == 0

    assert result.percentages == {
        "birds": 0.0,
        "cats": 0.0,
    }

    assert result.empty_classes == (
        "birds",
        "cats",
    )
    
    
def test_analyze_class_distribution_handles_empty_input() -> None:
    result = analyze_class_distribution({})

    assert result == ClassDistribution(
        total=0,
        counts={},
        percentages={},
        empty_classes=(),
    )
    
    
def test_analyze_inspection_results_counts_valid_and_invalid_images() -> None:
    inspections = {
        "cats": [
            ImageInspection(
                path=Path("/dataset/cats/cat.jpg"),
                extension=".jpg",
                format="JPEG",
                width=640,
                height=480,
                status="valid",
            ),
            ImageInspection(
                path=Path("/dataset/cats/broken.jpg"),
                extension=".jpg",
                format=None,
                width=None,
                height=None,
                status="invalid",
                error="cannot identify image file",
            ),
        ],
        "dogs": [
            ImageInspection(
                path=Path("/dataset/dogs/dog.png"),
                extension=".png",
                format="PNG",
                width=320,
                height=240,
                status="valid",
            ),
        ],
    }

    result = analyze_inspection_results(inspections)

    assert result.total == 3
    assert result.valid == 2
    assert result.invalid == 1    
    
    
def test_analyze_inspection_results_counts_detected_formats() -> None:
    inspections = {
        "images": [
            ImageInspection(
                path=Path("/dataset/image_01.jpg"),
                extension=".jpg",
                format="JPEG",
                width=640,
                height=480,
                status="valid",
            ),
            ImageInspection(
                path=Path("/dataset/image_02.png"),
                extension=".png",
                format="PNG",
                width=320,
                height=240,
                status="valid",
            ),
            ImageInspection(
                path=Path("/dataset/misnamed.jpg"),
                extension=".jpg",
                format="PNG",
                width=100,
                height=50,
                status="valid",
            ),
        ],
    }

    result = analyze_inspection_results(inspections)

    assert result.format_counts == {
        "JPEG": 1,
        "PNG": 2,
    }
    
    
def test_analyze_inspection_results_excludes_invalid_images_from_formats() -> None:
    inspections = {
        "cats": [
            ImageInspection(
                path=Path("/dataset/cats/broken.jpg"),
                extension=".jpg",
                format=None,
                width=None,
                height=None,
                status="invalid",
                error="cannot identify image file",
            ),
        ],
    }

    result = analyze_inspection_results(inspections)

    assert result.total == 1
    assert result.valid == 0
    assert result.invalid == 1
    assert result.format_counts == {}
    
    
def test_analyze_inspection_results_handles_empty_input() -> None:
    result = analyze_inspection_results({})

    assert result == InspectionSummary(
        total=0,
        valid=0,
        invalid=0,
        format_counts={},
    )
    
    
def test_analyze_dimensions_calculates_descriptive_statistics() -> None:
    inspections = {
        "images": [
            ImageInspection(
                path=Path("/dataset/image_01.jpg"),
                extension=".jpg",
                format="JPEG",
                width=100,
                height=50,
                status="valid",
            ),
            ImageInspection(
                path=Path("/dataset/image_02.png"),
                extension=".png",
                format="PNG",
                width=320,
                height=240,
                status="valid",
            ),
            ImageInspection(
                path=Path("/dataset/image_03.jpg"),
                extension=".jpg",
                format="JPEG",
                width=640,
                height=480,
                status="valid",
            ),
        ],
    }

    result = analyze_dimensions(inspections)

    assert result.image_count == 3

    assert result.min_width == 100
    assert result.max_width == 640
    assert result.mean_width == pytest.approx(353.333333)
    assert result.median_width == 320

    assert result.min_height == 50
    assert result.max_height == 480
    assert result.mean_height == pytest.approx(256.666667)
    assert result.median_height == 240
    
    
def test_analyze_dimensions_excludes_invalid_images() -> None:
    inspections = {
        "cats": [
            ImageInspection(
                path=Path("/dataset/cats/valid.jpg"),
                extension=".jpg",
                format="JPEG",
                width=200,
                height=100,
                status="valid",
            ),
            ImageInspection(
                path=Path("/dataset/cats/broken.jpg"),
                extension=".jpg",
                format=None,
                width=None,
                height=None,
                status="invalid",
                error="cannot identify image file",
            ),
        ],
    }

    result = analyze_dimensions(inspections)

    assert result.image_count == 1

    assert result.min_width == 200
    assert result.max_width == 200
    assert result.mean_width == 200
    assert result.median_width == 200

    assert result.min_height == 100
    assert result.max_height == 100
    assert result.mean_height == 100
    assert result.median_height == 100
    
    
def test_analyze_dimensions_handles_no_valid_images() -> None:
    inspections = {
        "cats": [
            ImageInspection(
                path=Path("/dataset/cats/broken.jpg"),
                extension=".jpg",
                format=None,
                width=None,
                height=None,
                status="invalid",
                error="cannot identify image file",
            ),
        ],
    }

    result = analyze_dimensions(inspections)

    assert result == DimensionStatistics(
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
    
    
def test_analyze_dimensions_handles_empty_input() -> None:
    result = analyze_dimensions({})

    assert result.image_count == 0
    assert result.min_width is None
    assert result.max_width is None
    assert result.mean_width is None
    assert result.median_width is None
    assert result.min_height is None
    assert result.max_height is None
    assert result.mean_height is None
    assert result.median_height is None
    