import requests

url = "http://127.0.0.1:5000/mensaje"

mensajes = ["hola", "2", "pollo", "abc", "2kg"]
for m in mensajes:
    response = requests.post(url, json={"mensaje": m})
    print("Enviado:", m)
    print("Respuesta:", response.json())
    print("------")