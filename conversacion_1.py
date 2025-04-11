import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from fastapi import Form
from dotenv import dotenv_values
from dotenv import load_dotenv

load_dotenv()

config = dotenv_values(".env") 

# Cargar la clave API de una variable de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCrU9pyxy5EVyc8t8M39qwFTOKY5MpfSbA")

# Extraer el texto del archivo txt
archivo=open("news_digital_bank.txt", "r", encoding="utf8")
text=archivo.read()
##print(text)

# Definir los mensajes a enviar al modelo
messages = [
    HumanMessage(content=f"Dame un resumen de dos párrafos del texto que te proveo a continuación; después, en un tercer párrafor indica cuál es el diario del que proviene el texto y el título correspondiente de la noticia.  ```{text}```")
]

# Configurar el modelo
model = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    google_api_key=(os.getenv("GOOGLE_API_KEY")),
    temperature=0.9 
)

# Ejecutar la tarea de completar texto
result = model.invoke(messages)
# Imprimir el resultado del LLM
print(result)