import os
from datetime import datetime
import chromadb
from tqdm import tqdm
from ollama import chat
from ollama import ChatResponse
from .prompts import STRUCTURE_PROMPT, CONTEXT_PROMPT, GENERATE_PROMPT 
from lib.utils import convert_rag_to_string
class Generator:
    def __init__(self, user_prompt, collection_name):
        self.client = chromadb.PersistentClient()
        
        self.collection = self.client.get_collection(name=collection_name)
       
        self.user_prompt = user_prompt


    def generate(self) -> str:

        user_context = self.collection.query(
            query_texts=[self.user_prompt],
            n_results=20,
            include=["documents"]
        )
        user_context_string = convert_rag_to_string(user_context)

        structure = self.generate_template_response(user_context_string) # overview of essay w/ some context
        context_response = self.generate_context_response(structure)

        new_context = self.collection.query(
            query_texts=[context_response],
            n_results=20,
            include=["documents"]
        )

        new_context_string = convert_rag_to_string(new_context)

        report = self.generate_report(structure, user_context_string, new_context_string)

        marker = "</think>"
        index = report.find(marker)
        if index != -1:
            report = report[index + len(marker):]
        
        self.write_to_file(report)

    def write_to_file(self, report):
        os.makedirs("reports", exist_ok=True)

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{current_time}.txt"

        file_path = os.path.join("reports", filename)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(report)

        print(f"Report saved to: {file_path}")

    

        


    def generate_report(self, structure: str, user_context: str, more_context: str) -> str:
        temp_prompt1 = GENERATE_PROMPT.replace("{USER_PROMPT}", self.user_prompt)
        temp_prompt2 = temp_prompt1.replace("{STRUCTURE}", structure)
        temp_prompt3 = temp_prompt2.replace("{USER_CONTEXT}", user_context)
        final_prompt = temp_prompt3.replace("{MORE_CONTEXT}", more_context)

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


    



    def generate_template_response(self, user_context):

        temp_prompt = STRUCTURE_PROMPT.replace("{USER_PROMPT}", self.user_prompt.strip())
        structure_prompt = temp_prompt.replace("{USER_CONTEXT}", user_context)

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

    def generate_context_response(self, structure):
        context_prompt = CONTEXT_PROMPT.replace("{OUTLINE_TEXT}", structure)

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
    
    

    