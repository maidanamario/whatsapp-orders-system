# WhatsApp Orders System

Sistema backend desarrollado con Flask que simula la automatización de pedidos por WhatsApp para pequeños negocios.

## Características

Permite:
- Recibir mensajes como si fueran de WhatsApp
- Guiar al usuario con un flujo tipo chatbot
- Registrar pedidos (producto + cantidad)
- Guardar datos en JSON
- Visualizar pedidos en una interfaz web
- **NUEVO:** Interfaz web tipo chat para interactuar con el sistema

---

## Tecnologías

- Python
- Flask
- JavaScript (Vanilla)
- HTML5 & CSS3

---

## Estructura del Proyecto

```
WhatsAppOrdersProject/
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias
├── README.md                       # Este archivo
│
├── routes/
│   ├── __init__.py
│   ├── main.py                     # Rutas principales (incluyendo /chat)
│   └── orders.py                   # Rutas de órdenes
│
├── services/
│   ├── __init__.py
│   └── order_service.py            # Lógica de negocio
│
├── templates/
│   ├── base.html                   # Template base (si existe)
│   ├── chat.html                   # ✨ NUEVO: Interfaz chat web
│   └── pedidos.html                # Listado de órdenes
│
├── static/
│   ├── style.css                   # ✨ NUEVO: Estilos del chat
│   └── chat.js                     # ✨ NUEVO: Lógica del chat
│
└── data/
    ├── pedidos.json                # Órdenes guardadas
    └── usuarios.json               # Estados de usuarios
```

---

## Rutas Disponibles

### GET `/`
- Retorna mensaje de status del sistema

### GET `/pedidos`
- Muestra tabla con todos los pedidos registrados

### **GET `/chat`** ✨ NUEVO
- Renderiza la interfaz web del chatbot
- Acceder en navegador: `http://localhost:5000/chat`

### POST `/mensaje`
- Endpoint principal del chatbot
- Acepta JSON: `{ "usuario": "id_usuario", "mensaje": "texto" }`
- Retorna: `{ "respuesta": "respuesta_del_bot" }`

---

## Flujo de Chatbot

### Estados del Usuario

1. **inicio**: Estado inicial
2. **esperando_opcion**: Esperando opción de menú (1 o 2)
3. **esperando_producto**: Esperando nombre del producto
4. **esperando_cantidad**: Esperando cantidad (ej: 2kg)
5. **confirmando_pedido**: Pidiendo confirmación del pedido

### Comandos Globales

- `hola`, `menu`, `inicio`: Reinicia el chat y muestra menú
- `0`: Cancela el proceso actual y vuelve al menú

### Ejemplo de Conversación

```
Usuario: hola
Bot: 1. Ver productos / 2. Hacer pedido (0 para cancelar)

Usuario: 2
Bot: Escribe el producto (0 para cancelar)

Usuario: pollo
Bot: Escribe la cantidad (0 para cancelar)

Usuario: 2kg
Bot: Producto: pollo
     Cantidad: 2kg
     
     ¿Confirmar pedido? (si/no)

Usuario: si
Bot: Pedido registrado. ¿Querés hacer otro pedido?
```

---

## Interfaz Web del Chat ✨ NUEVO

### Acceso
```
http://localhost:5000/chat
```

### Características

- **Diseño tipo WhatsApp**: Interfaz limpia y amigable
- **Usuario único**: Se genera automáticamente `web_user_XXXXX`
- **Mensajes en tiempo real**: Fetch POST a `/mensaje`
- **Scroll automático**: Desplazamiento automático al nuevo mensaje
- **Validación**: No permite enviar mensajes vacíos
- **Responsive**: Funciona en móviles y desktop

### Archivos

1. **chat.html** - Estructura HTML
   - Contenedor de chat
   - Área de mensajes (scrollable)
   - Input de texto y botón enviar

2. **chat.js** - Lógica JavaScript
   - `usuarioId`: Genera ID único `web_user_XXXXX`
   - `enviarMensaje()`: Envía mensaje al servidor
   - `mostrarMensajeUsuario()`: Muestra mensaje del usuario (derecha)
   - `mostrarMensajeBot()`: Muestra mensaje del bot (izquierda)
   - `hacerScrollAlFinal()`: Auto-scroll al final

3. **style.css** - Estilos CSS
   - Tema oscuro con acentos verdes
   - Burbujas de chat tipo WhatsApp
   - Animaciones suaves
   - Responsive design
   - Scroll personalizado

---

## 🛒 Sistema de Carrito v1.0 ⭐ NUEVO

### Características Principales

**Detección Automática Inteligente**
- Detecta múltiples productos en un solo mensaje
- Ejemplo: `"2kg carne, 1kg pollo, 500g cerdo"`
- Asigna correctamente cada cantidad a su producto

**Carrito Visual**
- Muestra todos los items agregados
- Opciones: agregar más (`"3"`), confirmar (`"confirmar"`), cancelar (`"cancelar"`)
- Interfaz intuitiva y clara

**3 Flujos de Entrada**
1. **Detección Automática** (Rápido): `"2kg carne, 1kg pollo"` → confirmar
2. **Paso a Paso** (Tradicional): `"2"` → `"pollo"` → `"2kg"` → `"si"`
3. **Híbrido** (Flexible): Mezcla automático y paso a paso

### Documentación del Carrito

Para información detallada sobre el sistema de carrito:

- 📖 **`INICIO_RAPIDO.md`** - Guía rápida (5 min)
- 📚 **`CARRITO_SISTEMA.md`** - Documentación técnica completa
- 🔄 **`FLUJO_ESTADOS.md`** - Diagrama visual de estados
- 📋 **`CAMBIOS_CARRITO.md`** - Resumen de cambios implementados
- ✅ **`IMPLEMENTACION_COMPLETA.md`** - Resumen ejecutivo

### Testing

Ejecutar suite de pruebas:
```bash
python test_carrito.py
```

Resultado esperado: **✅ 17/17 PASS (100%)**

---

## Validaciones

### Entrada de Mensajes
- ✅ Mensaje no vacío
- ✅ Payload JSON válido
- ✅ Campo "usuario" requerido
- ✅ Campo "mensaje" requerido

### Cantidad de Pedido
- ✅ Formato: `número + unidad` (1kg, 2kg, 500g, 1.5kg, etc.)
- ✅ Regex: `^\d+(?:\.\d+)?(kg|g)$`
- ✅ Rechaza: `1`, `kg`, `1 kg`, `abc`

---

## Almacenamiento de Datos

### `/data/usuarios.json`
Almacena el estado de cada usuario

```json
{
  "web_user_12345": {
    "state": "confirmando_pedido",
    "producto": "pollo",
    "cantidad": "2kg"
  },
  "web_user_67890": {
    "state": "inicio",
    "producto": "",
    "cantidad": ""
  }
}
```

### `/data/pedidos.json`
Almacena todos los pedidos confirmados

```json
[
  {
    "producto": "pollo",
    "cantidad": "2kg",
    "timestamp": "2026-04-05T10:30:45.123456"
  }
]
```

---

## Instalación y Uso

### 1. Clonar/Descargar el proyecto
```bash
cd WhatsAppOrdersProject
```

### 2. Crear entorno virtual
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python app.py
```

### 5. Acceder

- **API Chatbot**: `http://localhost:5000/mensaje` (POST)
- **Interfaz Web**: `http://localhost:5000/chat` (GET)
- **Listado Pedidos**: `http://localhost:5000/pedidos` (GET)
- **Status**: `http://localhost:5000/` (GET)

---

## Documentación del Código

### Comentarios en Español

Todos los archivos incluyen comentarios descriptivos:
- **main.py**: Documentación de funciones y rutas
- **chat.html**: Comentarios en elementos HTML
- **chat.js**: Comentarios en cada función y bloque
- **style.css**: Explicación de cada sección de estilos

---

## Ejemplo de Petición API

### cURL
```bash
curl -X POST http://localhost:5000/mensaje \
  -H "Content-Type: application/json" \
  -d '{"usuario": "web_user_123", "mensaje": "hola"}'
```

### JavaScript/Fetch
```javascript
fetch('/mensaje', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    usuario: 'web_user_123',
    mensaje: 'hola'
  })
})
.then(r => r.json())
.then(data => console.log(data.respuesta));
```

---

## Notas de Desarrollo

- ✅ No se modifica lógica del backend existente
- ✅ No se rompen rutas actuales
- ✅ Mantiene estructura del proyecto
- ✅ Código claro, ordenado y profesional
- ✅ Comentarios en español descriptivos
- ✅ Validación de inputs
- ✅ Manejo de errores
- ✅ Soporte para múltiples usuarios simultáneos
- ✅ Responsive design (móvil y desktop)

---

## Próximos Pasos

- [ ] Integración con WhatsApp Business API
- [ ] Base de datos real (MongoDB/PostgreSQL)
- [ ] Autenticación de usuarios
- [ ] Historial de pedidos por usuario
- [ ] Notificaciones en tiempo real
- [ ] Panel de administración

---

## Autor

Sistema desarrollado como ejemplo educativo de Flask + JavaScript

## Licencia

MIT


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
- Multiusuario -echo
- Integración real con WhatsApp API
- Base de datos (PostgreSQL / MongoDB)
- Panel administrativo

## 🚀 Deploy online

El sistema se encuentra desplegado en Render y disponible en:

👉 https://whatsapp-orders-api-ruex.onrender.com

### Endpoints disponibles

- POST `/mensaje` → interacción con el chatbot
- GET `/pedidos` → visualización de pedidos

### Ejemplo de uso (POST /mensaje)

```json
{
  "usuario": "user1",
  "mensaje": "hola"
}