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

def convert_rag_to_string(context_dict: dict) -> str:
    all_ids = context_dict["ids"][0]
    all_docs = context_dict["documents"][0]
    
    context_string = ""
    for idx, chunk_doc in zip(all_ids, all_docs):
        formatted = f"---\nChunk ID: {idx}\nChunk Text:\n{chunk_doc}\n"
        context_string += formatted

    return context_string
