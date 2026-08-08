from pathlib import Path

import pytest

from image_dataset_audit.analysis import (
    ClassDistribution,
    analyze_class_distribution,
)


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
    
    