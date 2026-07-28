import os
import pandas as pd
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuración de IA - En producción usar os.environ.get("GEMINI_API_KEY")
API_KEY = os.environ.get("GEMINI_API_KEY", "TU_API_KEY") 
genai.configure(api_key=API_KEY)

def load_context():
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'FAQ_New_Valley_Decoracion.csv')
    try:
        df = pd.read_csv(csv_path)
        context = "Base de conocimiento de New Valley:\n"
        for _, row in df.iterrows():
            context += f"P: {row['pregunta']} -> R: {row['respuesta']}\n"
        return context
    except Exception as e:
        return f"Error leyendo base de datos: {e}"

system_instruction = f'''Eres el asistente virtual oficial de New Valley. 
Usa ÚNICAMENTE la siguiente información para responder:
{load_context()}

REGLAS:
1. Responde de forma natural y clara basado en la información provista.
2. Si la respuesta no está en la base de conocimiento, indica que no tienes la información y sugiere contactar a soporte@newvalley.com o al WhatsApp +57 300 987 6543. Nunca inventes información.
'''

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction,
    generation_config={"temperature": 0.1}
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400
    try:
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
