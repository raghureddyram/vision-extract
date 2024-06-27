import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from django.test.utils import override_settings
from utils import ImageConverter

os.environ['DJANGO_SETTINGS_MODULE'] = 'vision.settings'

# Define a temporary BASE_DIR for tests
TEST_BASE_DIR = Path(__file__).resolve().parent

@pytest.fixture
@override_settings(BASE_DIR=TEST_BASE_DIR)
def setup_image_converter(tmp_path):
    pdf_folder = tmp_path / "source_pdfs"
    output_folder = tmp_path / "media"
    pdf_folder.mkdir()
    output_folder.mkdir()
    # Create a dummy PDF file
    pdf_path = pdf_folder / "test.pdf"
    pdf_path.write_text("dummy content")
    return ImageConverter(pdf_folder=pdf_folder, output_folder=output_folder, stop_phrases=["stop phrase"])

def test_initialization(setup_image_converter):
    image_converter = setup_image_converter
    assert image_converter.pdf_folder.exists()
    assert image_converter.output_folder.exists()
    assert image_converter.stop_phrases == ["stop phrase"]

def test_find_pdfs(setup_image_converter):
    image_converter = setup_image_converter
    pdfs = image_converter.find_pdfs()
    assert len(pdfs) == 1
    assert pdfs[0].name == "test.pdf"

@patch("fitz.open")
def test_contains_stop_phrases(mock_fitz_open, setup_image_converter):
    image_converter = setup_image_converter
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "This is a test content with stop phrase."
    mock_doc

if __name__ == "__main__":
    pytest.main()
