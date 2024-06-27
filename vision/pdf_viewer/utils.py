from pathlib import Path
from pdf2image import convert_from_path
from django.conf import settings

class ImageConverter:
    def __init__(self, pdf_folder='source_pdfs', output_folder='media'):
        self.pdf_folder = Path(settings.BASE_DIR) / pdf_folder
        self.output_folder = Path(settings.BASE_DIR) / output_folder

    def find_pdfs(self):
        # List all PDF files in the specified folder
        return list(self.pdf_folder.glob('*.pdf'))

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

            # Check if the PDF file exists (redundant check because glob only lists existing files)
            if not pdf_path.exists():
                print(f"PDF file not found: {pdf_path}")
                continue

            # Attempt to convert PDF to images
            try:
                images = convert_from_path(str(pdf_path))
            except Exception as e:
                print(f"Failed to convert {pdf_path.name}: {e}")
                continue

            # Save each image
            for i, image in enumerate(images):
                img_path = output_subfolder / f"page_{i + 1}.png"
                try:
                    image.save(str(img_path), 'PNG')
                    print(f"Saved page {i + 1} of {pdf_path.name} as {img_path}")
                except Exception as e:
                    print(f"Failed to save {img_path}: {e}")