import gradio as gr
import requests
import time 
import mimetypes
import traceback
import os
from typing import List, Tuple, Optional, Any, Generator, Union

url="http://127.0.0.1:8000/respuesta"

def add_text(
    history: List[Tuple[str, Optional[str]]],
    text: str
) -> Tuple[List[Tuple[str, Optional[str]]], Any]: 
    history = history+ [(text, None)]
    return history, gr.update(value="", interactive=True)

def bot(
    history: List[Tuple[str, Optional[str]]],
    _: Any,
    file: Optional[gr.File]
) -> Generator[List[Tuple[str, Optional[str]]], None, None]: 
    prompt: str = history[-1][0]
    response_content: str = ""
    current_question: str = history[-1][0]
    history[-1] = (current_question, "")

    try: 
        data: dict[str, str] = {"prompt": prompt}
        files: Optional[dict[str, Tuple[str, Any, str]]] = None

        if file and file.name:
            file_path: str = file.name
            file_name_only: str = os.path.basename(file_path)

            guessed_type, _ = mimetypes.guess_type(file_path)
            content_type: str = guessed_type if guessed_type else "application/octect-stream"
            print("Archivo detectado: {file_name_only} con tipo determinado: {content_type}")

            with open(file_path, "rb") as f:
                file_content_bytes = f.read()
                files = {"file" : (file_name_only, file_content_bytes, content_type)}
        else:
            print("No se detectó el archivo.")
        
        if files: 
            response: requests.Response = requests.post(url, data=data, files=files)
        else: 
            response: requests.Response = requests.post(url, data = data)
        if response.status_code == 200: 
            json_data: dict[str, Any] = response.json()
            print(f"Respuesta JSON de la API:{json_data}")
            response_content = json_data.get("response", "No hay respuesta.")
        else: 
            response_content = (
                f"Error {response.status_code}: {response.text}"
            )
    except requests.exceptions.ConnectionError:
        response_content = (
            "Error de conexión: Asegúrate de que la API está corriendo en"
            f"{url}. Revisa la consola de tu API para más detalles."
        )
    except Exception as e: 
        response_content = f"Error inesperado: {str(e)}"
        traceback.print_exc()
    
    for char in response_content: 
        current_question_for_loop: str = history[-1][0]
        current_answer_for_loop: Optional[str] = history[-1][1]

        new_answer_part: str = (current_answer_for_loop if current_answer_for_loop is not None else "") + char
        history[-1] = (current_question_for_loop, new_answer_part)

        time.sleep(0.01)

        yield history

# Interfaz Gradio
with gr.Blocks() as demo:
    chatbot: gr.Chatbot = gr.Chatbot([], elem_id="chatbot", height=600)

    with gr.Row():
        with gr.Column(scale=4):
            txt = gr.Textbox(
                placeholder="Escribe tu pregunta...", 
                show_label=False
            )

        with gr.Column(scale=1):
            archivo = gr.File(
                label="📁 Subir PDF",
                file_types=[".pdf", ".txt", ".html"]
            )

    txt.submit(
        add_text, 
        [chatbot, txt], 
        [chatbot, txt], 
        queue=False
        ).success(
        fn=bot,
        inputs=[chatbot, txt, archivo],
        outputs=chatbot
    )

    archivo.upload(
        fn=lambda h, f: h,  
        inputs=[chatbot, archivo],
        outputs=[chatbot],
        queue=False
    )

demo.queue()
if __name__ == "__main__":
    demo.launch(server_port=7860)