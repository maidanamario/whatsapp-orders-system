import requests

url = "http://127.0.0.1:5000/mensaje"

# Flujo: pedido, si (agregar más), agregar cerdo 3kg, no (confirmar)
mensajes = [
    {"usuario": "user2", "mensaje": "pollo 2kg"},
    {"usuario": "user2", "mensaje": "si"},
    {"usuario": "user2", "mensaje": "cerdo 3kg"},
    {"usuario": "user2", "mensaje": "no"}
]

for m in mensajes:
    response = requests.post(url, json=m)
    print("Enviado:", m["mensaje"])
    print("Respuesta:", response.json()["respuesta"])
    print("Estado:", response.json()["estado"])
    print("------")