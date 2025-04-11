import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from PyPDF2 import PdfReader
from dotenv import dotenv_values
from dotenv import load_dotenv

load_dotenv()

config = dotenv_values(".env") 

# Extraer el texto del PDF
pdf_path = "cuento.pdf" 
reader = PdfReader(pdf_path)
text = reader.pages[0].extract_text()

# Definir los mensajes a enviar al modelo
messages = [
    HumanMessage(content=f"Crea 5 viñetas que presenten los elementos más importantes de la historia contenida en el archivo a continuación.```{text}```")
]

# Configurar el modelo
model = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    google_api_key=(os.getenv("GOOGLE_API_KEY")),
    temperature=0.7 
)

# Ejecutar la tarea de completar texto
result = model.invoke(messages)
# Imprimir el resultado del LLM
print(result)