from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        # In a real app, you might want to try OCR here as a fallback
        return ""
