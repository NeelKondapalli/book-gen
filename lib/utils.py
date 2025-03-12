"""
Utility functions for text extraction from various document formats and data conversion.
This module provides helper functions for handling PDF, EPUB, DOCX files and ChromaDB data formatting.
"""
import os
import pdfplumber
from datetime import datetime
import ebooklib
from ebooklib import epub
from docx import Document
from typing import Dict, List, Any


def extract_text_from_pdf(filepath: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        filepath (str): Path to the PDF file

    Returns:
        str: Extracted text content from all pages concatenated together

    Note:
        Uses pdfplumber for extraction, handling empty pages by returning empty string
    """
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    return text


def extract_text_from_epub(filepath: str) -> str:
    """
    Extract text content from an EPUB file.

    Args:
        filepath (str): Path to the EPUB file

    Returns:
        str: Extracted text content from all document items

    Note:
        Processes only ITEM_DOCUMENT type content from the EPUB file
        Decodes content using UTF-8 encoding
    """
    book = epub.read_epub(filepath)
    text = ""
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        text += item.get_content().decode('utf-8')
    return text


def extract_text_from_docx(filepath: str) -> str:
    """
    Extract text content from a Microsoft Word (DOCX) file.

    Args:
        filepath (str): Path to the DOCX file

    Returns:
        str: Extracted text content with paragraphs joined by newlines

    Note:
        Preserves paragraph structure with newline separators
    """
    doc = Document(filepath)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def convert_rag_to_string(context_dict: Dict[str, List[List[str]]]) -> str:
    """
    Convert ChromaDB RAG (Retrieval-Augmented Generation) results to a formatted string.

    Args:
        context_dict (dict): Dictionary containing ChromaDB query results with 'ids' and 'documents' keys

    Returns:
        str: Formatted string containing chunk IDs and their corresponding text content

    Format:
        The output string follows the format:
        ---
        Chunk ID: {id}
        Chunk Text:
        {document_text}
        ---
        ...
    """
    all_ids = context_dict["ids"]
    all_docs = context_dict["documents"]
    
    context_string = ""
    for idx, chunk_doc in zip(all_ids, all_docs):
        formatted = f"---\nChunk ID: {idx}\nChunk Text:\n{chunk_doc}\n"
        context_string += formatted

    return context_string


def write_to_file(report: str) -> None:
    """
    Writes the generated report to a timestamped text file.

    Args:
        report (str): The generated report content to save

    Note:
        Files are saved in the 'reports' directory with timestamp-based names
        Format: YYYYMMDD_HHMMSS.txt
    """
    os.makedirs("reports", exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_time}.txt"

    file_path = os.path.join("reports", filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"Report saved to: {file_path}")