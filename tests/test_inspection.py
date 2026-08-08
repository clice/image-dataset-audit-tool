from pathlib import Path

from PIL import Image

from image_dataset_audit.inspection import (
    ImageInspection,
    inspect_image,
)


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
    
    
def test_inspect_image_extracts_jpeg_metadata(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "image.jpg"

    Image.new(
        "RGB",
        (640, 480),
    ).save(
        image_path,
        format="JPEG",
    )

    result = inspect_image(image_path)

    assert result.path == image_path.resolve()
    assert result.extension == ".jpg"
    assert result.format == "JPEG"
    assert result.width == 640
    assert result.height == 480
    assert result.status == "valid"
    assert result.error is None
    
    
def test_inspect_image_extracts_png_metadata(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "image.PNG"

    Image.new(
        "RGB",
        (320, 240),
    ).save(
        image_path,
        format="PNG",
    )

    result = inspect_image(image_path)

    assert result.extension == ".png"
    assert result.format == "PNG"
    assert result.width == 320
    assert result.height == 240
    
    
def test_inspect_image_detects_format_independently_from_extension(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "misnamed.jpg"

    Image.new(
        "RGB",
        (100, 50),
    ).save(
        image_path,
        format="PNG",
    )

    result = inspect_image(image_path)

    assert result.extension == ".jpg"
    assert result.format == "PNG"
    
    
def test_inspect_image_returns_invalid_result_for_unidentified_image(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "broken.jpg"
    image_path.touch()

    result = inspect_image(image_path)

    assert result.path == image_path.resolve()
    assert result.extension == ".jpg"
    assert result.format is None
    assert result.width is None
    assert result.height is None
    assert result.status == "invalid"
    assert result.error is not None
    assert "cannot identify image file" in result.error
    
    
def test_inspect_image_returns_invalid_result_for_corrupted_image(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "corrupted.png"

    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\ninvalid-image-data"
    )

    result = inspect_image(image_path)

    assert result.extension == ".png"
    assert result.format is None
    assert result.width is None
    assert result.height is None
    assert result.status == "invalid"
    assert result.error is not None
    