# 🍃 New Valley - Agente Inteligente de Atención al Cliente

## 📌 Descripción General
**New Valley** es una iniciativa enfocada en la fabricación y venta de productos decorativos y materos 100% ecológicos hechos a partir de materia prima reciclada. Este proyecto implementa un agente de Inteligencia Artificial capaz de responder consultas de usuarios sobre nuestro catálogo, materiales, resistencia, envíos, métodos de pago y políticas de devolución utilizando una base de conocimiento estructurada en formato CSV.

---

## 🏗️ Arquitectura de la Solución
1. **Base de Conocimiento:** Archivo CSV (`FAQ_New_Valley_Decoracion.csv`) con las preguntas frecuentes, categorías y respuestas oficiales.
2. **Procesador de Datos / Carga:** Módulo en Python que lee y extrae la información del CSV.
3. **Agente IA (RAG / System Prompt):** Modelo de lenguaje con un Prompt de Sistema estructurado que restringe el rango de respuestas únicamente al contexto del CSV.
4. **Despliegue:** Aplicación alojada en infraestructura de nube (Oracle Cloud Infrastructure - OCI).

---

## 🛠️ Tecnologías y Herramientas
- **Lenguaje:** Python 3.x
- **Framework Web:** Flask
- **Procesamiento de Datos:** Pandas / módulo `csv`
- **Infraestructura Cloud:** Oracle Cloud Infrastructure (OCI)

---

## 🚀 Instrucciones para Ejecutar el Proyecto Localmente

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/new-valley-agent.git](https://github.com/TU_USUARIO/new-valley-agent.git)
   cd new-valley-agent
