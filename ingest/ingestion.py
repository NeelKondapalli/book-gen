"""
This module provides functionality for ingesting various document formats into a ChromaDB vector database.
It supports PDF, EPUB, DOCX, TXT, and XML files with automatic text chunking and progress tracking.
Documents are processed and stored in a vector database for efficient retrieval and searching.
"""

import os
import time
import chromadb
from datetime import datetime
from lib.utils import extract_text_from_pdf, extract_text_from_epub, extract_text_from_docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Set, List, Any


class Ingestor:
    """
    A class to handle document ingestion and storage in ChromaDB.

    This class manages the process of reading various document formats,
    converting them to text, splitting them into appropriate chunks,
    and storing them in a ChromaDB collection with progress tracking.

    Attributes:
        dir (str): Directory path containing documents to process
        client (chromadb.PersistentClient): ChromaDB client instance
        name (str): Name of the ChromaDB collection
        collection (chromadb.Collection): ChromaDB collection for storing documents
        processed_files (set): Set of unique filenames that have been processed
    """

    def __init__(self, dir_path, name):
        """
        Initialize the Ingestor with a directory path and collection name.

        Args:
            dir_path (str): Path to directory containing documents to process
            name (str): Name for the ChromaDB collection

        Note:
            If a collection with the given name exists, it will be deleted and recreated
            with current timestamp metadata
        """
        self.dir = dir_path
        self.client = chromadb.PersistentClient()
        self.name = name
        
        try:
            self.client.delete_collection(name=name)
            print(f"Deleted old collection by name {name}")
        except Exception:
            pass

    def process_directory(self) -> None:
        """
        Process all supported documents in the specified directory.

        This method:
        1. Walks through the directory tree
        2. Identifies supported documents
        3. Converts them to text
        4. Splits text into chunks (700 chars with 100 char overlap)
        5. Stores chunks in ChromaDB with unique IDs
        6. Displays progress with tqdm progress bars

        Raises:
            Exception: If no text could be extracted from a file
        """
        print(f"Processing directory: {self.dir}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        processed_files = set()

        for root, _, files in os.walk(self.dir):
            for file in files:
                filepath = os.path.join(root, file)
                filename = os.path.basename(filepath)
                processed_files.add(filename.strip())

        collection = self.client.create_collection(
            name=self.name, 
            metadata={
                "created": str(datetime.now()),
                "processed_files": "###".join(list(processed_files))
            }
        )
        
        for root, _, files in os.walk(self.dir):
            for file in files:
                filepath = os.path.join(root, file)
                text = self.convert_file_to_text(filepath)
                if text:
                    chunks = text_splitter.create_documents([text])
                    filename = os.path.basename(filepath)
                    
                    print(f"\nProcessing file: {filename}")
        
                    with tqdm(total=len(chunks), desc="Chunks", unit="chunk") as pbar:
                        for i, chunk in enumerate(chunks):
                            chunk_id = f"{filename}-chunk-{i}"
                            # Add metadata about source file for each chunk
                            collection.add(
                                documents=[chunk.page_content],
                                ids=[chunk_id],
                                metadatas=[{"source_file": filename.strip()}]
                            )
                            pbar.update(1)
                    print(f"Finished processing: {filename}")
                else:
                    raise Exception(f"No text found for {filename}")
        
        
        collection.metadata["processed_files"] = "###".join(list(processed_files))
        print(f"\nProcessed files: {', '.join(processed_files)}")

    def convert_file_to_text(self, filepath: str) -> str:
        """
        Convert various document formats to plain text.

        Args:
            filepath (str): Path to the file to be converted

        Returns:
            str: Extracted text from the document

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            ValueError: If the file format is not supported
            Exception: For any other processing errors

        Supported formats:
            - PDF (.pdf)
            - EPUB (.epub)
            - Microsoft Word (.docx)
            - Text files (.txt)
            - XML files (.xml)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return extract_text_from_pdf(filepath)
            elif file_ext == '.epub':
                return extract_text_from_epub(filepath)
            elif file_ext == '.docx':
                return extract_text_from_docx(filepath)
            elif file_ext == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_ext == '.xml':
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'xml')
                    return soup.get_text(separator=' ', strip=True)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            print(f"Error processing {filepath}: {str(e)}")
            return ""
