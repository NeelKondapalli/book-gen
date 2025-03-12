import os
import time
import chromadb
from datetime import datetime
from lib.utils import extract_text_from_pdf, extract_text_from_epub, extract_text_from_docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
from tqdm import tqdm


class Ingestor:
    def __init__(self, dir_path, name):
        self.dir = dir_path
        self.client = chromadb.PersistentClient()
        self.name = name
        
        try:
            self.client.delete_collection(name=name)
            print(f"Deleted old collection by name {name}")
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=name, 
            metadata={
                "created": str(datetime.now())
            }
        )

    def process_directory(self):
        print(f"Going to process directory: {self.dir}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        
        for root, _, files in os.walk(self.dir):
            for file in files:
                filepath = os.path.join(root, file)
                text = self.convert_file_to_text(filepath)
                if text:

                    chunks = text_splitter.create_documents([text])
                    
                    
                    print(f"\nProcessing file: {os.path.basename(filepath)}")

        
                    with tqdm(total=len(chunks), desc="Chunks", unit="chunk") as pbar:
                        for i, chunk in enumerate(chunks):

                            chunk_id = f"{os.path.basename(filepath)}-chunk-{i}"
                            self.collection.add(documents=[chunk.page_content], ids=[chunk_id])
                            
                            pbar.update(1)
                    print(f"Finished processing: {os.path.basename(filepath)}")
                else:
                    raise Exception(f"No text found for {os.path.basename(filepath)}")

    def convert_file_to_text(self, filepath: str) -> str:
        """Convert various document formats to plain text."""
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
