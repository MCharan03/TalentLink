from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


def get_pdf_page_count(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            return len(list(PDFPage.create_pages(document)))
    except:
        return 0


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file. First, it tries a direct text extraction.
    If that yields little or no text, it falls back to OCR.
    """
    try:
        # 1. Try direct text extraction
        direct_text = extract_text(pdf_path)
        # Simple check to see if text extraction was successful (e.g., more than 100 characters)
        if direct_text and len(direct_text.strip()) > 100:
            return direct_text
    except Exception as e:
        print(f"Error during direct text extraction from {pdf_path}: {e}")
        # Proceed to OCR if direct extraction fails
        pass

    # 2. Fallback to OCR if direct extraction yields no/little text
    print(f"Falling back to OCR for {pdf_path}")
    try:
        # Convert PDF to a list of PIL images
        # You might need to provide the poppler path on Windows
        # images = convert_from_path(pdf_path, poppler_path=r'C:\path\to\poppler\bin')
        images = convert_from_path(pdf_path)

        ocr_text = ""
        for image in images:
            # Use Tesseract to do OCR on the image
            ocr_text += pytesseract.image_to_string(image)

        return ocr_text
    except Exception as e:
        print(f"Error during OCR processing for {pdf_path}: {e}")
        # This could be due to Tesseract not being installed or other issues
        return ""
