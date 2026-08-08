from pathlib import Path

from image_dataset_audit.inspection import ImageInspection


def test_image_inspection_stores_valid_image_metadata() -> None:
    result = ImageInspection(
        path=Path("/dataset/cats/cat.jpg"),
        extension=".jpg",
        format="JPEG",
        width=640,
        height=480,
        status="valid",
    )

    assert result.path == Path("/dataset/cats/cat.jpg")
    assert result.extension == ".jpg"
    assert result.format == "JPEG"
    assert result.width == 640
    assert result.height == 480
    assert result.status == "valid"
    assert result.error is None


def test_image_inspection_supports_invalid_image_result() -> None:
    result = ImageInspection(
        path=Path("/dataset/cats/broken.jpg"),
        extension=".jpg",
        format=None,
        width=None,
        height=None,
        status="invalid",
        error="cannot identify image file",
    )

    assert result.format is None
    assert result.width is None
    assert result.height is None
    assert result.status == "invalid"
    assert result.error == "cannot identify image file"
    