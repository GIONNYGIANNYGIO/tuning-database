import os, json, time, google.generativeai as genai

# CONFIGURA LA TUA CHIAVE API (Consiglio: usa GitHub Secrets)
API_KEY = os.getenv('GEMINI_API_KEY') 
genai.configure(api_key=API_KEY)
model = genai.generativeModel('gemini-1.5-flash')

def get_ai_data(car_name):
    prompt = f"Fornisci dati tecnici reali per il tuning di '{car_name}'. Rispondi SOLO in formato JSON: {{'prestazioni': ['Stage 1...', 'Stage 2...', 'Stage 3...'], 'estetica': ['Mod 1...', 'Mod 2...', 'Mod 3...'], 'officine': ['Nome officina specializzata']}}. Usa marchi reali."
    response = model.generate_content(prompt)
    try:
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except:
        return None

# Carica lista
with open('cars_to_scrape.txt', 'r') as f:
    all_cars = [l.strip() for l in f if l.strip()]

# Ciclo automatico
for car in all_cars:
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-')
    folder = f"brands/{brand}"
    filepath = f"{folder}/{slug}.json"
    
    # Se il file esiste già, salta (Risparmia API!)
    if os.path.exists(filepath):
        continue
        
    print(f"Generando dati per: {car}...")
    data = get_ai_data(car)
    if data:
        os.makedirs(folder, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        time.sleep(3) # Pausa di sicurezza per API
