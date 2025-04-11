import requests

url = "http://127.0.0.1:8000/generate"

# Archivo que se enviará
files = {
    "file": open("news_el_economista.txt", "rb")
}

data = {"prompt": "Considera el siguiente artículo de noticias: {file}. Determina los 5 puntos más importantes y preséntalos en una lista con viñetas."}


response = (requests.post(url, files=files, data=data))
respuesta = response.json()["response"]
respuesta_limpia = respuesta.replace("\\n", "\n").replace("\\", "")
print(respuesta_limpia)
