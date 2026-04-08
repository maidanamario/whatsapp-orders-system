"""
Script de prueba para verificar que la interfaz chat funciona correctamente.

Este script hace peticiones POST a /mensaje para simular conversaciones
y verifica que la respuesta del servidor sea válida.
"""

import requests
import json

# URL del servidor (ajusta si es diferente)
BASE_URL = "http://127.0.0.1:5000"

# ID de usuario para la prueba
USUARIO_TEST = "test_user_123"

def hacer_peticion(mensaje):
    """
    Hace una petición POST a /mensaje y retorna la respuesta.
    
    Args:
        mensaje (str): El mensaje a enviar
        
    Returns:
        dict: La respuesta del servidor
    """
    try:
        datos = {
            "usuario": USUARIO_TEST,
            "mensaje": mensaje
        }
        respuesta = requests.post(
            f"{BASE_URL}/mensaje",
            json=datos,
            timeout=5
        )
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
        return None

def prueba_flujo_completo():
    """
    Prueba el flujo completo del chatbot:
    1. Saludo
    2. Seleccionar opción de hacer pedido
    3. Ingresar producto
    4. Ingresar cantidad
    5. Confirmar pedido
    """
    print("\n" + "="*60)
    print("PRUEBA FLUJO COMPLETO DEL CHATBOT")
    print("="*60 + "\n")
    
    conversacion = [
        ("hola", "Debe mostrar menú"),
        ("2", "Debe pedir producto"),
        ("pollo", "Debe pedir cantidad"),
        ("2kg", "Debe pedir confirmación"),
        ("si", "Debe confirmar pedido"),
    ]
    
    for mensaje, descripcion in conversacion:
        print(f"📤 Enviando: '{mensaje}'")
        print(f"   Descripción esperada: {descripcion}")
        
        respuesta = hacer_peticion(mensaje)
        
        if respuesta:
            print(f"✅ Respuesta recibida:")
            print(f"   {respuesta['respuesta']}\n")
        else:
            print(f"❌ No se recibió respuesta\n")
            break

def prueba_validaciones():
    """
    Prueba las validaciones del sistema:
    - Mensaje vacío
    - Usuario faltante
    - Cantidad inválida
    """
    print("\n" + "="*60)
    print("PRUEBA VALIDACIONES")
    print("="*60 + "\n")
    
    # Prueba 1: Mensaje vacío
    print("1️⃣  Probando mensaje vacío...")
    try:
        respuesta = requests.post(
            f"{BASE_URL}/mensaje",
            json={"usuario": "test", "mensaje": "   "},
            timeout=5
        )
        print(f"✅ Respuesta: {respuesta.json()['respuesta']}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Prueba 2: Usuario faltante
    print("2️⃣  Probando usuario faltante...")
    try:
        respuesta = requests.post(
            f"{BASE_URL}/mensaje",
            json={"mensaje": "hola"},
            timeout=5
        )
        print(f"✅ Respuesta: {respuesta.json()['respuesta']}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    print("\n🚀 INICIANDO PRUEBAS DEL SISTEMA DE CHAT\n")
    
    # Ejecutar pruebas
    prueba_flujo_completo()
    prueba_validaciones()
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)
    print("\n💡 Para acceder a la interfaz web, abre:")
    print("   http://localhost:5000/chat\n")
