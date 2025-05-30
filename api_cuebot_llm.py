from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,  SystemMessage
from dotenv import load_dotenv
from fastapi import FastAPI,  HTTPException, UploadFile, File, Form
import pdfplumber
from pathlib import Path
from bs4 import BeautifulSoup
import os
from typing import Optional

load_dotenv()

app = FastAPI()

def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """Extrae texto de archivos .txt, .pdf y .html"""
    ext = file_extension.lower()
    print(f"DEBUG: Ruta del archivo para extracción: {file_path}") # Debug
    print(f"DEBUG: Extensión detectada: '{ext}'") # Debug - fíjate en las comillas

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    elif ext == ".pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(
                    page.extract_text() for page in pdf.pages if page.extract_text()
                )
        except Exception as e:
            print(f"Error al extraer texto del PDF '{file_path}: {str(e)}")
            raise ValueError(f"No se pudo abrir el PDF: {str(e)}")
    elif ext == ".html":
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            return soup.get_text()
    else:
        raise ValueError("Formato de archivo no soportado")


@app.post("/respuesta")
async def generate_response(
    prompt: str = Form(...), 
    file: Optional[UploadFile] = File(None)
):

    print(os.getenv("GOOGLE_API_KEY"))
    print(f"Prompt recibido: {prompt}, Archivo recibido: {file}")
    text = ""

    try:
        if file:
            print(f"Nombre del archivo: {file.filename}, Tipo de archivo: {file.content_type}")
            temp_file_path = f"temp_{file.filename}_{os.urandom(8).hex()}"
            contents: bytes = await file.read()

            # Configurar el modelo de LangChain con Gemini
            with open(temp_file_path, "wb") as buffer: 
                buffer.write(contents)
            original_file_extension = Path(file.filename).suffix
            text = extract_text_from_file(temp_file_path, original_file_extension)
            os.remove(temp_file_path)
            print(f"Archivo temporal {temp_file_path} eliminado.")
        else: 
            print("No se recibió archivo, solo prompt.")
    
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        user_message_content: str

        if text: 
            user_message_content = f"{prompt}\n\nEl texto que deberás analizar es el siguiente: {text}"
        else: 
            user_message_content = prompt

        messages = [
            SystemMessage("Eres un asistente virtual que responde únicamente en español"),
            HumanMessage(content=f"{prompt} El texto que deberás analizar es el siguiente: {user_message_content}")
        ]


        response = model.invoke(messages)
        result = response.content

        return{"response": result}


    except Exception as e:
        import traceback
        traceback.print_exc()  # Esto imprime todo el stack del error en consola
        raise HTTPException(status_code=500, detail=str(e))