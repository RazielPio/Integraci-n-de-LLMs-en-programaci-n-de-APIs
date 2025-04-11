from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
from pathlib import Path
from bs4 import BeautifulSoup
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from fastapi import Form

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Cargar la API Key desde una variable de entorno
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY no está definido en las variables de entorno")

app = FastAPI()
    
def extract_text_from_file(file_path: str) -> str:
    """Extrae texto de archivos .txt, .pdf y .html."""
    ext = Path(file_path).suffix.lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    elif ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif ext == ".html":
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            return soup.get_text()
    else:
        raise ValueError("Formato de archivo no soportado")
    
from fastapi import Form

@app.post("/generate")
def generate_response(prompt: str = Form(...), file: UploadFile = File(...)):
    """Recibe instrucciones y un archivo de texto, y obtiene una respuesta del LLM usando LangChain."""
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        text = extract_text_from_file(file_path)
        
        # Configurar el modelo de LangChain con Gemini
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=(os.getenv("GOOGLE_API_KEY")))
        messages = [
            SystemMessage("Eres un asistente virtual que responde únicamente en inglés"),
            HumanMessage(content=f"{prompt} El texto que deberás analizar es el siguiente: {text}")
        ]
        response = model(messages)
        result = response.content
        
        # Guardar la conversación en un archivo
        #with open("conversacion_1.txt", "a", encoding="utf-8") as log_file:
        #    log_file.write(f"Usuario: {data.prompt} El texto que deberás analizar es el siguiente: {text}\n")
        #    log_file.write(f"LLM: {result}\n\n")
        
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))