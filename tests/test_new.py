import requests

# Test existing functionality
url = "http://127.0.0.1:5000/mensaje"

# Test message "1"
data1 = {"mensaje": "1"}
response1 = requests.post(url, json=data1)
print("Test 1 - Status:", response1.status_code)
print("Test 1 - Respuesta:", response1.text)

# Test new order
data2 = {"mensaje": "pollo 2kg"}
response2 = requests.post(url, json=data2)
print("Test 2 - Status:", response2.status_code)
print("Test 2 - Respuesta:", response2.text)

# Check if file was created
import os
if os.path.exists("data/pedidos.json"):
    with open("data/pedidos.json", 'r') as f:
        import json
        orders = json.load(f)
        print("Orders in file:", orders)
else:
    print("File not created")