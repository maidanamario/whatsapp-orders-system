# WhatsApp Orders System
Sistema backend desarrollado con Flask que simula la automatización de pedidos por WhatsApp para pequeños negocios.



Permite:
- Recibir mensajes como si fueran de WhatsApp
- Guiar al usuario con un flujo tipo chatbot
- Registrar pedidos (producto + cantidad)
- Guardar datos en JSON
- Visualizar pedidos en una interfaz web

---

## Ejemplo de uso

Usuario:
hola

Bot:
1. Ver productos / 2. Hacer pedido

Usuario:
2

Bot:
Escribe el producto

Usuario:
pollo

Bot:
Escribe la cantidad

Usuario:
2kg

Bot:
Pedido registrado

---


## Tecnologías
- Python
- Flask


## Funcionalidades

- Endpoint `/mensaje` (chatbot)
- Guardado de pedidos en JSON
- Vista `/pedidos` para visualizar datos
- Validación de inputs (ej: cantidad correcta)
- Manejo de estado del usuario

---

## 📁 Estructura del proyecto

### 📁 `routes/`
Define los endpoints de la aplicación

### 📁 `services/`
Contiene la lógica de negocio

### 📁 `data/`
Almacenamiento de pedidos en JSON

### 📁 `templates/`
Vistas HTML renderizadas

### 📁 `static/`
Archivos estáticos (CSS, JS, imágenes)

---

## Cómo ejecutar

1. Crear entorno virtual
2. Instalar dependencias:
   pip install -r requirements.txt
3. Ejecutar:
   python app.py


## Vista del sistema
![Pedidos](2026-03-31.png)

## Objetivo
Proyecto práctico orientado a automatizar pedidos para negocios pequeños y servir como base para futuros desarrollos más complejos (chatbots, integraciones, etc).

## Posibles mejoras 
- Multiusuario
- Integración real con WhatsApp API
- Base de datos (PostgreSQL / MongoDB)
- Panel administrativo