import logging
import os
from pathlib import Path

import pandas as pd
from flask import Flask, request, jsonify
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME")

if not API_KEY:
    logging.warning(
        "GEMINI_API_KEY no está configurada. El servicio funcionará solo para pruebas locales sin acceso a la API."
    )
else:
    genai.configure(api_key=API_KEY)

CSV_PATH = Path(__file__).resolve().parent / "data" / "FAQ_New_Valley_Decoracion.csv"


def read_faq():
    try:
        df = pd.read_csv(CSV_PATH)
        faqs = []
        for _, row in df.iterrows():
            faqs.append({
                "id": int(row["id"]) if "id" in row and not pd.isna(row["id"]) else None,
                "categoria": str(row.get("categoria", "")).strip(),
                "pregunta": str(row.get("pregunta", "")).strip(),
                "respuesta": str(row.get("respuesta", "")).strip(),
            })
        return faqs
    except FileNotFoundError:
        logging.error("No se encontró el archivo CSV de FAQ en %s", CSV_PATH)
        return []
    except Exception as exc:
        logging.exception("Error leyendo el CSV de FAQ")
        return []


def build_context(faqs):
    if not faqs:
        return "Base de conocimiento de New Valley:\nNo hay datos disponibles."

    lines = ["Base de conocimiento de New Valley:"]
    for faq in faqs:
        lines.append(f"P: {faq['pregunta']} -> R: {faq['respuesta']}")

    return "\n".join(lines)


faq_data = read_faq()
context_text = build_context(faq_data)

system_instruction = f"""Eres el asistente virtual oficial de New Valley.
Usa ÚNICAMENTE la siguiente información para responder:
{context_text}

REGLAS:
1. Responde de forma natural y clara basado en la información provista.
2. Si la respuesta no está en la base de conocimiento, indica que no tienes la información y sugiere contactar a soporte@newvalley.com o al WhatsApp +57 300 987 6543. Nunca inventes información.
"""

SAFE_MODEL_CANDIDATES = [
    "models/gemini-flash-latest",
    "models/gemini-3.5-flash",
    "models/gemini-3.6-flash",
    "models/gemini-2.5-flash-lite",
]


def list_supported_models():
    if not API_KEY:
        return []

    supported = []
    try:
        for model_info in genai.list_models():
            methods = getattr(model_info, "supported_generation_methods", None)
            if methods and "generateContent" in methods:
                supported.append(model_info.name)
    except Exception:
        logging.exception("No se pudo listar los modelos disponibles.")
    return supported


def normalize_model_name(name: str) -> str:
    if not name:
        return ""
    return name if name.startswith("models/") else f"models/{name}"


def choose_model(candidate: str, supported_models: list[str]) -> str:
    candidate = normalize_model_name(candidate)

    if supported_models and candidate not in supported_models:
        logging.warning(
            "El modelo solicitado %s no está disponible en la lista de modelos visibles."
            " Seleccionando un modelo compatible automáticamente.",
            candidate,
        )
        for fallback in SAFE_MODEL_CANDIDATES:
            if fallback in supported_models:
                return fallback
        for fallback in supported_models:
            if not fallback.startswith("models/gemini-2.5-"):
                return fallback
        return supported_models[0]

    if candidate.startswith("models/gemini-2.5-"):
        for fallback in SAFE_MODEL_CANDIDATES:
            if fallback in supported_models:
                logging.warning(
                    "El modelo solicitado %s puede no estar disponible para nuevos usuarios." \
                    " Cambiando a %s.",
                    candidate,
                    fallback,
                )
                return fallback
        for fallback in supported_models:
            if not fallback.startswith("models/gemini-2.5-"):
                logging.warning(
                    "El modelo solicitado %s puede no estar disponible para nuevos usuarios." \
                    " Cambiando a %s.",
                    candidate,
                    fallback,
                )
                return fallback

    return candidate


def create_model(model_name: str):
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config={"temperature": 0.1},
    )


supported_models = list_supported_models()
if MODEL_NAME:
    requested_model = MODEL_NAME
else:
    requested_model = "models/gemini-flash-latest"

candidate = choose_model(requested_model, supported_models)

if supported_models:
    logging.info("Modelo Gemini seleccionado: %s", candidate)
else:
    logging.info(
        "No se pudo determinar un modelo compatible automáticamente; usando %s."
        " Esto puede fallar si la API no acepta el nombre.",
        candidate,
    )

model = create_model(candidate)
CURRENT_MODEL_NAME = candidate


from flask import Flask, request, jsonify, render_template


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "ok",
            "message": "New Valley FAQ AI assistant",
            "faq_count": len(faq_data),
        }
    )


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "loaded_faqs": len(faq_data),
            "api_key_set": bool(API_KEY),
            "selected_model": CURRENT_MODEL_NAME,
            "available_models": len(supported_models),
        }
    )


@app.route("/api/faq", methods=["GET"])
def faq():
    return jsonify({"faqs": faq_data})


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Payload JSON inválido"}), 400

    user_message = payload.get("message")
    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "Mensaje vacío"}), 400

    if not API_KEY:
        return jsonify(
            {"error": "GEMINI_API_KEY no está configurada. Configure la variable de entorno y reinicie la app."}
        ), 500

    try:
        response = model.generate_content(user_message)
    except Exception as exc:
        fallback_message = str(exc)
        if (
            "no longer available to new users" in fallback_message
            or "is not found for API version v1beta" in fallback_message
            or "not found" in fallback_message
        ):
            logging.warning(
                "Modelo %s inválido o inaccesible: %s. Intentando con otro modelo seguro.",
                CURRENT_MODEL_NAME,
                fallback_message,
            )
            alternate = None
            for fallback in SAFE_MODEL_CANDIDATES:
                if fallback != CURRENT_MODEL_NAME:
                    alternate = fallback
                    break
            if alternate:
                try:
                    new_model = create_model(alternate)
                    response = new_model.generate_content(user_message)
                    globals()["model"] = new_model
                    globals()["CURRENT_MODEL_NAME"] = alternate
                except Exception as exc2:
                    logging.exception("Fallo el reintento con el modelo alternativo %s.", alternate)
                    return jsonify({"error": str(exc2)}), 500
            else:
                return jsonify({"error": fallback_message}), 500
        else:
            logging.exception("Error generando la respuesta")
            return jsonify({"error": fallback_message}), 500

    text = getattr(response, "text", None)
    if not text:
        candidates = getattr(response, "candidates", None)
        if candidates:
            candidate = candidates[0]
            content = getattr(candidate, "content", None)
            if content:
                text = getattr(content, "text", None)
                if not text:
                    parts = getattr(content, "parts", None)
                    if parts:
                        text = parts[0]

    return jsonify({"response": text or ""})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
