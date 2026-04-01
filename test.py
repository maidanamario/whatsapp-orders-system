import requests

url = "http://127.0.0.1:5000/mensaje"


mensajes = [
 {"usuario": "user1", "mensaje": "hola"},
 {"usuario": "user1", "mensaje": "2"},
 {"usuario": "user1", "mensaje": "pollo"},
 {"usuario": "user1", "mensaje": "2kg"},
 {"usuario": "user1", "mensaje": "no"}
]


for m in mensajes:
    response = requests.post(url, json=m)
    print("Enviado:", m)
    print("Respuesta:", response.json())
    print("------")