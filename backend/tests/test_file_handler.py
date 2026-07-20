from io import BytesIO

from werkzeug.datastructures import FileStorage

from app.utils.exceptions import ValidationFailedError
from app.utils.file_handler import validate_and_save_image


def test_validate_and_save_image_rejects_missing_file(tmp_path):
    try:
        validate_and_save_image(
            None, upload_folder=str(tmp_path), allowed_extensions={"png"}, max_bytes=1024
        )
        assert False, "expected ValidationFailedError"
    except ValidationFailedError as exc:
        assert "No file was uploaded" in exc.message


def test_validate_and_save_image_rejects_empty_filename(tmp_path):
    file = FileStorage(stream=BytesIO(b"data"), filename="")
    try:
        validate_and_save_image(
            file, upload_folder=str(tmp_path), allowed_extensions={"png"}, max_bytes=1024
        )
        assert False, "expected ValidationFailedError"
    except ValidationFailedError as exc:
        assert "No file was uploaded" in exc.message


def test_validate_and_save_image_rejects_filename_with_no_extension(tmp_path):
    file = FileStorage(stream=BytesIO(b"data"), filename="photo")
    try:
        validate_and_save_image(
            file, upload_folder=str(tmp_path), allowed_extensions={"png"}, max_bytes=1024
        )
        assert False, "expected ValidationFailedError"
    except ValidationFailedError as exc:
        assert "Unsupported file type" in exc.message
