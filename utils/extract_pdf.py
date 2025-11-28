import pdfplumber
import re

def extract_text_from_pdf(path: str) -> str:
    content = []
    allowed_pattern = r"[^a-zA-Z0-9,\.\-\_\/\(\) \n]"  
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            cleaned = re.sub(allowed_pattern, "", text)
            content.append(cleaned)
    return "\n".join(content)

