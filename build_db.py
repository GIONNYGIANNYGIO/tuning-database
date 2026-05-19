import os, json, time, google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_data(car_name):
    # Prompt potenziato: istruiamo Gemini a essere ultra-specifico
    prompt = f"""
    Create a detailed tuning profile for the '{car_name}'. 
    Return ONLY JSON with this structure:
    {{
      "brand": "{car_name.split()[0]}",
      "model": "{car_name}",
      "prestazioni": ["Specific Stage 1 part for this engine", "Specific Stage 2 part", "Specific Stage 3 part"],
      "estetica": ["Specific exterior upgrade for this model", "Specific suspension part", "Specific wheel/tire setup"]
    }}
    IMPORTANT: Do not use generic parts. If it's an Electric Car, focus on inverter/battery/software. If it's a Turbo car, focus on intercoolers/turbos.
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.replace('```json', '').replace('```', '').strip())

# Loop per processare le auto
with open('cars_to_scrape.txt', 'r') as f:
    all_cars = [l.strip() for l in f if l.strip()]

for car in all_cars:
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    filepath = f"brands/{brand}/{slug}.json"
    
    # FORZIAMO LA RISCRITTURA: 
    # Se vuoi cambiare TUTTE le auto vecchie, togli l'if os.path.exists
    # oppure elimina manualmente la cartella 'brands' su GitHub
    
    print(f"Generando dati REALI per: {car}...")
    data = get_ai_data(car)
    if data:
        os.makedirs(f"brands/{brand}", exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        time.sleep(4)
