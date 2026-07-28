# 🍃 New Valley - Agente Inteligente de Atención al Cliente

## 📌 Descripción General
**New Valley** es una iniciativa enfocada en la fabricación y venta de productos decorativos y materos 100% ecológicos hechos a partir de materia prima reciclada. Este proyecto implementa un agente de Inteligencia Artificial que responde consultas usando una base de conocimiento estructurada en un archivo CSV.

---

## 🏗️ Arquitectura de la Solución
1. **Base de Conocimiento:** archivo CSV (`data/FAQ_New_Valley_Decoracion.csv`) con preguntas frecuentes y respuestas oficiales.
2. **Procesador de Datos:** módulo en Python que lee y convierte el CSV en una lista de FAQ.
3. **Agente IA:** Flask expone una API que envía la consulta al modelo de Gemini usando `google-generativeai`.
4. **Despliegue:** aplicación ejecutable localmente o en un servicio que soporte Flask.

---

## 🛠️ Tecnologías y Herramientas
- **Lenguaje:** Python 3.x
- **Framework Web:** Flask
- **Procesamiento de Datos:** Pandas
- **Modelo IA:** `google-generativeai`

---

## 🚀 Instrucciones para Ejecutar el Proyecto Localmente

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/heynerdm/New-valley.git
   cd New-valley
   ```

2. **Crear y activar un entorno virtual (recomendado):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la API Key:**
   ```bash
   export GEMINI_API_KEY="tu_api_key_aqui"
   ```

5. (Opcional) **Configurar el modelo:**
   ```bash
   export GEMINI_MODEL_NAME="gemini-flash-latest"
   ```

   Si `GEMINI_MODEL_NAME` no está configurado o no está disponible, la app seleccionará automáticamente el primer modelo compatible con `generateContent` que encuentre.

6. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

6. **Probar la API:**
   - Verificar estado:
     ```bash
     curl http://127.0.0.1:5000/
     ```
   - Verificar salud:
     ```bash
     curl http://127.0.0.1:5000/api/health
     ```
   - Obtener la lista de FAQs:
     ```bash
     curl http://127.0.0.1:5000/api/faq
     ```
   - Enviar una pregunta al asistente:
     ```bash
     curl -X POST http://127.0.0.1:5000/api/chat \
       -H "Content-Type: application/json" \
       -d '{"message": "¿Qué métodos de pago aceptan?"}'
     ```

---

## 🧪 Endpoints disponibles

- `GET /` — verifica que el servicio está activo.
- `GET /api/health` — retorna información de salud y carga de datos.
- `GET /api/faq` — retorna el listado de preguntas frecuentes cargadas desde el CSV.
- `POST /api/chat` — recibe JSON con `message` y responde usando el modelo.

---

## 📌 Notas

- Asegúrate de que el archivo `data/FAQ_New_Valley_Decoracion.csv` existe y contiene las columnas `id`, `categoria`, `pregunta`, `respuesta`.
- Si `GEMINI_API_KEY` no está configurada, la ruta `/api/chat` devolverá un error explicando que falta la clave.
- Para producción, usa un servicio que exponga el puerto `5000` o configura un servidor WSGI como `gunicorn`.

---

## 🚀 Despliegue rápido en Render

1. Crea una cuenta en https://render.com.
2. Selecciona "New Web Service" y conecta tu repositorio de GitHub `heynerdm/New-valley`.
3. Elige el branch `main`.
4. Usa estos valores:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Environment: `Python 3`
5. Añade la variable de entorno `GEMINI_API_KEY` con tu clave.
6. (Opcional) Añade `GEMINI_MODEL_NAME=gemini-flash-latest`.

Render detectará `Procfile` y `render.yaml` para desplegar la app.

> Al finalizar, Render te dará un enlace público que puedes compartir para que la app esté disponible desde cualquier lugar.

## 📁 Carpeta de evidencia

Se ha creado la carpeta `evidence/` para subir las capturas de pantalla y la evidencia de funcionamiento.

Incluye en `evidence/`:

- `screenshot-home.png` — pantalla principal de la app cargando.
- `screenshot-chat.png` — prueba de envío de mensaje y respuesta.
- `screenshot-url.png` — URL pública visible en el navegador.

Puedes agregar más archivos de evidencia similares según lo requiera la entrega.
