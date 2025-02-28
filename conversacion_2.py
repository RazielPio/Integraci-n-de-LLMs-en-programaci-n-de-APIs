import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from PyPDF2 import PdfReader

# Cargar la clave API de una variable de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCrU9pyxy5EVyc8t8M39qwFTOKY5MpfSbA") 

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
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7 
)

# Ejecutar la tarea de completar texto
result = model.invoke(messages)
# Imprimir el resultado del LLM
print(result)