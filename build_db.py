import os
import json
import time
from google import genai

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Alziamo a 20 auto a sessione per finire in circa 2 mesi
BATCH_SIZE = 20  

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
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                # Se dice 'limit: 0' è la quota giornaliera, inutile insistere
                if "limit: 0" in error_msg:
                    print("-> Quota giornaliera di Google TERMINATA. Inutile proseguire per oggi.")
                    return "DAILY_LIMIT"
                
                # Altrimenti è solo il limite al minuto: aspettiamo e ritentiamo
                wait_time = 90
                print(f"-> Limite al minuto raggiunto per {car_name}. Pausa di {wait_time}s (Tentativo {attempt+1}/3)...")
                time.sleep(wait_time)
            else:
                print(f"-> Errore imprevisto per {car_name}: {e}")
                return None
    return None

try:
    with open('cars_to_scrape.txt', 'r') as f:
        all_cars = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print("Errore: 'cars_to_scrape.txt' non trovato.")
    all_cars = []

processed_count = 0

for car in all_cars:
    if processed_count >= BATCH_SIZE:
        print(f"Raggiunto il limite di {BATCH_SIZE} auto per questo turno.戛")
        break
        
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    filepath = f"brands/{brand}/{slug}.json"
    
    if os.path.exists(filepath):
        continue
    
    print(f"Generando dati per: {car}...")
    data = get_ai_data(car)
    
    if data == "DAILY_LIMIT":
        print("Blocco di sicurezza: Arresto lo script per non mandare in loop GitHub Actions.")
        break
        
    if data and data != "DAILY_LIMIT":
        os.makedirs(f"brands/{brand}", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f" Salvato: {filepath}")
        
        processed_count += 1
        # 35 secondi di pausa tra auto di successo per NON attivare il blocco al minuto del piano free
        time.sleep(35) 
    else:
        print(f"Saltata: {car} a causa di un errore di generazione.")
        time.sleep(5)
