import pytest
from src.parsing.resume_parser import parse_resume


def test_unsupported_file_type():
    with pytest.raises(ValueError):
        parse_resume("data/raw/sample.txt")


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_resume("data/raw/does_not_exist.pdf")