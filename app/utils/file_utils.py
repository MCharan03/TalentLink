from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage


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
    Extracts text from a PDF file. Focuses on direct extraction for speed.
    OCR is disabled to prevent hangs on Windows systems without Tesseract.
    """
    print(f"DEBUG: Starting text extraction for {pdf_path}...", flush=True)
    try:
        # Try direct text extraction
        print("DEBUG: Trying direct text extraction...", flush=True)
        direct_text = extract_text(pdf_path)
        
        if direct_text and len(direct_text.strip()) > 50:
            print(f"DEBUG: Extraction successful ({len(direct_text)} chars).", flush=True)
            return direct_text
        
        print("DEBUG: PDF appears to be an image or has no selectable text.", flush=True)
        return "Error: This PDF appears to be a scanned image. Please upload a text-based PDF."

    except Exception as e:
        print(f"DEBUG: Error during extraction: {e}", flush=True)
        return ""
