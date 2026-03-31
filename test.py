import requests

url = "http://127.0.0.1:5000/mensaje"
data = {"mensaje": "pollo 2kg"}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Respuesta:", response.text)