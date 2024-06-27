from pathlib import Path
from pdf2image import convert_from_path, pdfinfo_from_path
from django.conf import settings
import fitz  # PyMuPDF

class ImageConverter:
    def __init__(self, pdf_folder='source_pdfs', output_folder='media', stop_phrases=None):
        self.pdf_folder = Path(settings.BASE_DIR) / pdf_folder
        self.output_folder = Path(settings.BASE_DIR) / output_folder
        self.stop_phrases = stop_phrases if stop_phrases is not None else []

    def find_pdfs(self):
        # List all PDF files in the specified folder
        return list(self.pdf_folder.glob('*.pdf'))

    def contains_stop_phrases(self, doc):
        for page in doc:
            text = page.get_text()
            for phrase in self.stop_phrases:
                if phrase in text:
                    return True
        return False

    def convert_pdf_to_images(self):
        pdf_files = self.find_pdfs()
        if not pdf_files:
            print("No PDF files found.")
            return

        for pdf_path in pdf_files:
            # Extract the base name without the .pdf extension to create a subfolder
            output_subfolder = self.output_folder / pdf_path.stem

            # Ensure the output subfolder exists
            output_subfolder.mkdir(parents=True, exist_ok=True)
            print(f"Output folder path: {output_subfolder.resolve()}")

            # Attempt to convert PDF to images
            try:
                pdf_info = pdfinfo_from_path(str(pdf_path))
                total_pages = pdf_info['Pages']
                doc = fitz.open(pdf_path)
            except Exception as e:
                print(f"Failed to open {pdf_path.name}: {e}")
                continue

            for page_number in range(total_pages):
                try:
                    page = doc.load_page(page_number)
                    text = page.get_text()

                    if self.contains_stop_phrases([page]):
                        print(f"Skipping page {page_number + 1} of {pdf_path.name} due to stop phrases.")
                        continue

                    images = convert_from_path(str(pdf_path), first_page=page_number + 1, last_page=page_number + 1)

                    for i, image in enumerate(images):
                        img_path = output_subfolder / f"page_{page_number + 1}.png"
                        try:
                            image.save(str(img_path), 'PNG')
                            print(f"Saved page {page_number + 1} of {pdf_path.name} as {img_path}")
                        except Exception as e:
                            print(f"Failed to save {img_path}: {e}")

                except Exception as e:
                    print(f"Failed to process page {page_number + 1} of {pdf_path.name}: {e}")