import os
import json
import time
from google import genai

# Inizializza il client con la nuova libreria
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def get_ai_data(car_name):
    brand_name = car_name.split()[0]
    
    prompt = f"""
    You are an expert JDM/Euro racing and tuning specialist.
    Generate an EXTREMELY SPECIFIC tuning profile for the following car: '{car_name}'.

    CRITICAL RULES: 
    1. The ENTIRE output MUST be in English.
    2. Do NOT use generic answers like "sports exhaust" or "ECU tune". 
    3. You MUST mention the actual engine code of this specific car (e.g., 2JZ, K20, B58, VR38DETT) and precise specifications.
    4. You MUST mention real brand-name components or chassis-specific parts (e.g., Garrett GTX turbo, Ohlins suspension, Rocket Bunny aero kit).
    5. The data must be 100% unique to this exact model and not copied from other cars.

    Respond EXCLUSIVELY with a valid JSON file in this exact format, with no Markdown, no formatting blocks, and no extra text:
    {{
        "brand": "{brand_name.upper()}",
        "model": "{car_name}",
        "prestazioni": [
            "Specific tuning part 1 (mention engine code/specifics)",
            "Specific tuning part 2",
            "Specific tuning part 3"
        ],
        "estetica": [
            "Specific visual mod 1",
            "Specific visual mod 2",
            "Specific visual mod 3"
        ]
    }}
    """
    
    # Sistema di Retry intelligente: se Google blocca, aspetta progressivamente di più
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
            
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                wait_time = (attempt + 1) * 60 # Aspetta 60s, poi 120s, ecc.
                print(f"Quota esaurita. Attesa di {wait_time}s prima di riprovare...")
                time.sleep(wait_time)
            else:
                print(f"Errore critico per {car_name}: {e}")
                return None
    return None

# Caricamento lista auto
try:
    with open('cars_to_scrape.txt', 'r') as f:
        all_cars = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print("Errore: 'cars_to_scrape.txt' non trovato.")
    all_cars = []

# Loop principale
for car in all_cars:
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    filepath = f"brands/{brand}/{slug}.json"
    
    # Controllo se il file esiste già: se sì, salta per risparmiare quota
    if os.path.exists(filepath):
        print(f"File già esistente per {car}, salto...")
        continue
    
    print(f"Generando dati REALI per: {car}...")
    data = get_ai_data(car)
    
    if data:
        os.makedirs(f"brands/{brand}", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f" Salvato correttamente: {filepath}")
        # Pausa standard tra richieste fortunate
        time.sleep(10)
    else:
        print(f"Impossibile generare dati per {car}")
