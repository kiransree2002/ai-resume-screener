from pypdf import PdfReader


def parse_pdf(file) -> str:
    """Read a PDF file and extract its text using pypdf."""
    print("Parsing PDF file...")
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text.strip()