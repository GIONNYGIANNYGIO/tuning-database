import os
import json
import google.generativeai as genai

# Configura Gemini (la chiave va messa in GitHub Secrets come GEMINI_API_KEY)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def get_tuning_data(car_name):
    prompt = f"""
    Genera un JSON per l'auto {car_name} con queste esatte chiavi:
    {
      "estetica": ["Pezzo 1", "Pezzo 2"],
      "prestazioni": ["Stage 1: ...", "Stage 2: ...", "Stage 3: ..."],
      "officine": ["Officina A (Città)", "Officina B (Città)"]
    }
    Rispondi solo con il codice JSON.
    """
    response = model.generate_content(prompt)
    return json.loads(response.text)

# ... resto dello script che salva il file JSON ...
