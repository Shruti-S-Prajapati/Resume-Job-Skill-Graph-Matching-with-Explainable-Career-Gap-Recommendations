import pytest
from src.parsing.resume_parser import parse_resume


def test_unsupported_file_type(tmp_path):
    # file must actually exist, so we hit the extension-check branch, not file-not-found
    unsupported_file = tmp_path / "sample.txt"
    unsupported_file.write_text("dummy content")

    with pytest.raises(ValueError):
        parse_resume(str(unsupported_file))


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_resume("data/raw/does_not_exist.pdf")