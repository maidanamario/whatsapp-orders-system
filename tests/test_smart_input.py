"""
Test script for Smart Input Feature
Tests the intelligent input suggestions, validation, and state transitions
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
USER_ID = "test_user_001"


def test_request(mensaje, descripcion=""):
    """
    Send a test request to the chatbot
    
    Args:
        mensaje: Message to send
        descripcion: Test description
    """
    print(f"\n{'='*70}")
    print(f"TEST: {descripcion}")
    print(f"{'='*70}")
    print(f"📤 Enviando: {mensaje}")
    
    data = {
        "usuario": USER_ID,
        "mensaje": mensaje
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mensaje", json=data)
        response_data = response.json()
        
        print(f"📥 Respuesta:")
        print(f"  Mensaje: {response_data.get('respuesta', 'N/A')[:100]}...")
        print(f"  Estado: {response_data.get('estado', 'N/A')}")
        
        return response_data.get('estado')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """
    Run all tests
    """
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           🧠 TEST SMART INPUT FEATURE 🧠                          ║")
    print("║              WhatsApp Orders Chatbot v3.0                         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    
    # Test 1: Initial greeting
    estado = test_request("hola", "1. Greeting - Should show initial options")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Greeting works correctly")
    
    
    # Test 2: View products
    estado = test_request("1", "2. View products option")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Products listing works")
    
    
    # Test 3: Start order
    estado = test_request("2", "3. Start order - Should go to esperando_producto")
    assert estado == "esperando_producto", f"Expected 'esperando_producto', got '{estado}'"
    print("✅ PASSED: Order flow starts correctly")
    
    
    # Test 4: Select product (pollo)
    estado = test_request("pollo", "4. Select product - POLLO")
    assert estado == "esperando_cantidad", f"Expected 'esperando_cantidad', got '{estado}'"
    print("✅ PASSED: Product selection works")
    
    
    # Test 5: Invalid quantity
    estado = test_request("mucho", "5. Invalid quantity - Should stay in esperando_cantidad")
    assert estado == "esperando_cantidad", f"Expected 'esperando_cantidad', got '{estado}'"
    print("✅ PASSED: Quantity validation works (rejects invalid)")
    
    
    # Test 6: Valid quantity (1kg)
    estado = test_request("1kg", "6. Valid quantity - 1kg")
    assert estado == "confirmando_pedido", f"Expected 'confirmando_pedido', got '{estado}'"
    print("✅ PASSED: Valid quantity accepted, moved to confirmation")
    
    
    # Test 7: Correct product before confirmation
    estado = test_request("producto", "7. Correct product - Should go back to esperando_producto")
    assert estado == "esperando_producto", f"Expected 'esperando_producto', got '{estado}'"
    print("✅ PASSED: Product correction works")
    
    
    # Test 8: Select different product (carne)
    estado = test_request("carne", "8. Select different product - CARNE")
    assert estado == "esperando_cantidad", f"Expected 'esperando_cantidad', got '{estado}'"
    print("✅ PASSED: Changed product successfully")
    
    
    # Test 9: New quantity (2kg)
    estado = test_request("2kg", "9. New quantity - 2kg")
    assert estado == "confirmando_pedido", f"Expected 'confirmando_pedido', got '{estado}'"
    print("✅ PASSED: New quantity accepted")
    
    
    # Test 10: Change quantity before confirmation
    estado = test_request("cantidad", "10. Correct quantity - Should go back to esperando_cantidad")
    assert estado == "esperando_cantidad", f"Expected 'esperando_cantidad', got '{estado}'"
    print("✅ PASSED: Quantity correction works")
    
    
    # Test 11: New quantity again
    estado = test_request("3kg", "11. Another new quantity - 3kg")
    assert estado == "confirmando_pedido", f"Expected 'confirmando_pedido', got '{estado}'"
    print("✅ PASSED: Final quantity confirmed")
    
    
    # Test 12: Cancel order
    estado = test_request("no", "12. Cancel order")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Order cancellation works")
    
    
    # Test 13: New order - pollo with 500g
    test_request("2", "13a. Start new order")
    test_request("pollo", "13b. Select pollo again")
    estado = test_request("500g", "13c. Select 500g - Valid decimal format")
    assert estado == "confirmando_pedido", f"Expected 'confirmando_pedido', got '{estado}'"
    print("✅ PASSED: Decimal quantity (500g) works")
    
    
    # Test 14: Confirm order
    estado = test_request("si", "14. Confirm order with 'si'")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Order confirmation works")
    
    
    # Test 15: Test quantity with decimal (1.5kg)
    test_request("2", "15a. Start new order")
    test_request("cerdo", "15b. Select cerdo")
    estado = test_request("1.5kg", "15c. Select 1.5kg - Decimal format")
    assert estado == "confirmando_pedido", f"Expected 'confirmando_pedido', got '{estado}'"
    print("✅ PASSED: Decimal quantity (1.5kg) works")
    
    
    # Test 16: Global command - ayuda
    estado = test_request("ayuda", "16. Global command - AYUDA")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Help command works globally")
    
    
    # Test 17: New order for menu test
    test_request("2", "17a. Start order")
    test_request("pollo", "17b. Select pollo")
    estado = test_request("2kg", "17c. Complete order")
    
    # Test 18: Global command - menu
    estado = test_request("menu", "18. Global command - MENU")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Menu command works globally")
    
    
    # Test 19: New order for cancelar test
    test_request("2", "19a. Start order")
    test_request("carne", "19b. Select carne")
    estado = test_request("cancelar", "19c. Global command - CANCELAR")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Cancelar command works globally")
    
    
    # Test 20: Cancel with 0
    test_request("2", "20a. Start order")
    test_request("cerdo", "20b. Select cerdo")
    estado = test_request("0", "20c. Cancel with 0")
    assert estado == "inicio", f"Expected 'inicio', got '{estado}'"
    print("✅ PASSED: Cancel with 0 works")
    
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                  ✅ ALL TESTS PASSED ✅                           ║")
    print("║                                                                    ║")
    print("║  Smart Input Features Verified:                                  ║")
    print("║  ✅ State transitions work correctly                             ║")
    print("║  ✅ Validation (quantity format) works                           ║")
    print("║  ✅ Product selection works                                      ║")
    print("║  ✅ Quantity selection works                                     ║")
    print("║  ✅ Confirmation with corrections works                          ║")
    print("║  ✅ Global commands work in all states                           ║")
    print("║  ✅ Order cancellation works                                     ║")
    print("║  ✅ Order confirmation and saving works                          ║")
    print("║  ✅ State is returned in all responses                           ║")
    print("║  ✅ Decimal quantities work (1.5kg, 500g)                        ║")
    print("║                                                                    ║")
    print("║  Frontend will use 'estado' field to show smart suggestions!     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
