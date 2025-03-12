"""
This module provides functionality for generating AI responses using ChromaDB vector storage
and the DeepSeek-R1 8B model through Ollama. It handles context retrieval, response structuring,
and report generation based on user prompts.
"""

import os
import chromadb
from ollama import chat
from datetime import datetime
from lib.utils import convert_rag_to_string, write_to_file
from .prompts import STRUCTURE_PROMPT, CONTEXT_PROMPT, GENERATE_PROMPT 



class Generator:
    """
    A class to handle AI response generation using ChromaDB and Ollama.

    This class manages the process of retrieving relevant context from ChromaDB,
    structuring responses, and generating comprehensive reports based on user prompts.

    Attributes:
        client (chromadb.PersistentClient): ChromaDB client instance
        collection (chromadb.Collection): ChromaDB collection for context retrieval
        user_prompt (str): The user's input prompt for generation
    """

    def __init__(self, user_prompt: str, collection_name: str) -> None:
        """
        Initialize the Generator with a prompt and collection name.

        Args:
            user_prompt: The prompt to generate content for
            collection_name: Name of the ChromaDB collection to use
        """
        self.client = chromadb.PersistentClient()
        self.collection = self.client.get_collection(name=collection_name)
        self.user_prompt = user_prompt
    
    def get_even_context(self, results_per_file: int, query: str) -> str:
        processed_files = self.collection.metadata["processed_files"].split("###")
        all_contexts = []

        for filename in processed_files:
            file_context = self.collection.query(
                query_texts=[query],
                n_results=results_per_file,
                where={"source_file": filename.strip()}, 
                include=["documents", "metadatas"]
            )
            all_contexts.append(file_context)
        
        combined_context = {
            "ids": [sum([chunk["ids"][0] for chunk in all_contexts], [])],
            "documents": [sum([chunk["documents"][0] for chunk in all_contexts], [])]
        }
        
        context_string = convert_rag_to_string(combined_context)

        return context_string
    

    def generate(self) -> str:
        """
        Executes the steps to process the user's prompt and generate the final report,
        ensuring equal context from each source document.
        """

        processed_files = " ".join(self.collection.metadata["processed_files"].split("###"))
        
        context_string = self.get_even_context(2, self.user_prompt)

        structure = self.generate_template_response(context_string, processed_files) # overview of essay w/ some context
        
        context_response = self.generate_context_response(structure, processed_files)

        marker = "</think>"
        index = context_response.find(marker)
        if index != -1:
            context_response = context_response[index + len(marker):]

        more_context_string = self.get_even_context(1, context_response)

        report = self.generate_report(structure, context_response, context_string, more_context_string, processed_files)

        marker = "</think>"
        index = report.find(marker)
        if index != -1:
            report = report[index + len(marker):]
        
        write_to_file(report)
    
    def generate_template_response(self, user_context: str, files: str) -> str:
        """
        Generates a structural template/outline for the report.

        Args:
            user_context (str): The context retrieved from the user's prompt

        Returns:
            str: A structured outline for the report

        Note:
            Uses the DeepSeek-R1 8B model with a specific structure prompt
        """
        structure_prompt = STRUCTURE_PROMPT.replace("{USER_PROMPT}", self.user_prompt.strip())
        structure_prompt = structure_prompt.replace("{USER_CONTEXT}", user_context)
        structure_prompt = structure_prompt.replace("{FILENAMES}", files)

        stream = chat(
            model='deepseek-r1:8b',
            messages=[{'role': 'user', 'content': structure_prompt}],
            stream=True,
        )
        response = ""

        for chunk in stream:
            response += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)
        print("\n\n\n")
        
    
        return response


    def generate_context_response(self, structure: str, files: str) -> str:
        """
        Generates additional context based on the report structure.

        Args:
            structure (str): The outline/structure of the report

        Returns:
            str: Additional context for report generation

        Note:
            Uses the DeepSeek-R1 8B model to expand on the structural outline
        """
        context_prompt = CONTEXT_PROMPT.replace("{OUTLINE_TEXT}", structure)
        context_prompt = context_prompt.replace("{USER_PROMPT}", self.user_prompt.strip())
        context_prompt = context_prompt.replace("{FILENAMES}", files)

        stream = chat(
            model='deepseek-r1:8b',
            messages=[{'role': 'user', 'content': context_prompt}],
            stream=True,
        )

        response = ""

        for chunk in stream:
            response += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)
        print("\n\n\n")
        

        return response

    

    def generate_report(self, structure: str, context_response: str, user_context: str, more_context: str, files: str) -> str:
        """
        Generates the final report using the collected context and structure.

        Args:
            structure (str): The outline/structure for the report
            user_context (str): Initial context based on user prompt
            more_context (str): Additional context retrieved based on structure

        Returns:
            str: The complete generated report

        Note:
            Uses the DeepSeek-R1 8B model for generation with streaming output
        """
        final_prompt = GENERATE_PROMPT.replace("{USER_PROMPT}", self.user_prompt)
        final_prompt = final_prompt.replace("{STRUCTURE}", structure)
        final_prompt = final_prompt.replace("{USER_CONTEXT}", user_context)
        final_prompt = final_prompt.replace("{CONTEXT_RESPONSE}", context_response)
        final_prompt = final_prompt.replace("{MORE_CONTEXT}", more_context)
        final_prompt = final_prompt.replace("{FILENAMES}", files)

        stream = chat(
            model='deepseek-r1:8b',
            messages=[{'role': 'user', 'content': final_prompt}],
            stream=True,
        )

        response = ""

        for chunk in stream:
            response += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)

        print("\n\n\n")
        
    
        return response



