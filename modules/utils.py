import pdfplumber
import ebooklib
from ebooklib import epub
from docx import Document
import os


def extract_text_from_pdf(filepath: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        return text

def extract_text_from_epub(filepath: str) -> str:
    """Extract text from an EPUB file."""
    book = epub.read_epub(filepath)
    text = ""
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        text += item.get_content().decode('utf-8')
    return text

def extract_text_from_docx(filepath: str) -> str:
    """Extract text from a DOCX file."""
    doc = Document(filepath)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])