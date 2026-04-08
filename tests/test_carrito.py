"""
Script de prueba para verificar el flujo del carrito.

Prueba los casos principales:
1. Detección automática de múltiples productos
2. Flujo paso a paso
3. Confirmación y guardado
"""

import json
import os
import sys

# Agregar la ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.main import parsear_pedido, validate_cantidad

def test_parsear_pedido():
    """Test de la función parsear_pedido"""
    print("=" * 60)
    print("TEST: parsear_pedido()")
    print("=" * 60)
    
    test_cases = [
        ("2kg carne, 1kg pollo", 2, "Múltiples productos"),
        ("pollo 2kg carne 2kg", 2, "Productos continuos sin coma"),
        ("pollo 3kg", 1, "Formato: producto cantidad"),
        ("1 kg carne", 1, "Formato con espacios"),
        ("2,5kg cerdo", 1, "Cantidad con coma decimal"),
        ("500g pollo, 1kg carne, 2kg cerdo", 3, "Tres productos"),
        ("nada interesante", None, "Sin productos"),
        ("quiero 2kg de carne", 1, "Contexto con palabras extra"),
    ]
    
    for mensaje, expected_count, descripcion in test_cases:
        result = parsear_pedido(mensaje)
        
        if expected_count is None:
            success = result is None
            result_str = "None"
        else:
            success = result is not None and len(result) == expected_count
            result_str = json.dumps(result, indent=2) if result else "None"
        
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"\n{status} - {descripcion}")
        print(f"    Entrada: '{mensaje}'")
        print(f"    Esperado: {expected_count} items")
        print(f"    Resultado: {result_str}")

def test_validate_cantidad():
    """Test de la función validate_cantidad"""
    print("\n" + "=" * 60)
    print("TEST: validate_cantidad()")
    print("=" * 60)
    
    test_cases = [
        ("1kg", True),
        ("2.5kg", True),
        ("500g", True),
        ("1.5kg", True),
        ("100g", True),
        ("1", False),
        ("kg", False),
        ("2,5kg", False),  # Coma, no punto
        ("1kilos", False),
        ("2 kg", False),  # Espacio
    ]
    
    for cantidad, expected in test_cases:
        result = validate_cantidad(cantidad)
        success = result == expected
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"{status} - validate_cantidad('{cantidad}') = {result} (esperado: {expected})")

def test_carrito_flow():
    """Test del flujo del carrito simulado"""
    print("\n" + "=" * 60)
    print("TEST: Simulación de flujo del carrito")
    print("=" * 60)
    
    # Simular un usuario
    user = {
        "state": "inicio",
        "producto": "",
        "cantidad": "",
        "carrito": []
    }
    
    print("\n1. Usuario envía: '2kg carne, 1kg pollo'")
    pedidos = parsear_pedido("2kg carne, 1kg pollo")
    if pedidos:
        for pedido in pedidos:
            user["carrito"].append(pedido)
        print(f"   ✅ Agregado al carrito: {len(pedidos)} items")
        print(f"   Carrito: {json.dumps(user['carrito'], indent=6)}")
    
    print("\n2. Usuario envía: 'no' (para confirmar el pedido)")
    print(f"   Carrito antes: {len(user['carrito'])} items")
    if user["carrito"]:
        # Simular guardado
        print("   ✅ Guardando pedidos...")
        for item in user["carrito"]:
            print(f"      - {item['producto']} {item['cantidad']}")
        
        # Resetear
        user["carrito"] = []
        user["state"] = "inicio"
        print("   ✅ Carrito limpiado, usuario en 'inicio'")

if __name__ == "__main__":
    test_parsear_pedido()
    test_validate_cantidad()
    test_carrito_flow()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("=" * 60)
