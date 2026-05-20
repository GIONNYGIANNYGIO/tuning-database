import os
import json
import time
from google import genai

# Inizializza il client con la nuova libreria
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def get_ai_data(car_name):
    # Separiamo il brand (es. "Nissan" da "Nissan GT-R R35")
    brand_name = car_name.split()[0]
    
    # Prompt potenziato: istruiamo Gemini a essere ultra-specifico e usare SOLO l'inglese
    prompt = f"""
    You are an expert JDM/Euro racing and tuning specialist.
    Generate an EXTREMELY SPECIFIC tuning profile for the following car: '{car_name}'.

    CRITICAL RULES: 
    1. The ENTIRE output MUST be in English.
    2. Do NOT use generic answers like "sports exhaust" or "ECU tune". 
    3. You MUST mention the actual engine code of this specific car (e.g., 2JZ, K20, B58, VR38DETT) and precise specifications.
    4. You MUST mention real brand-name components or chassis-specific parts (e.g., Garrett GTX turbo, Ohlins suspension, Rocket Bunny aero kit).
    5. The data must be 100% unique to this exact model and not copied from other cars.
    6. If it's an Electric Car, focus on inverter/battery/software. If it's a Turbo car, focus on intercoolers/turbos.

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
    
    try:
        # Chiamata API con la nuova libreria e il nuovo modello
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        
        # Pulizia dell'output nel caso l'IA aggiunga i backtick del markdown
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(raw_text)
        
    except Exception as e:
        print(f"Errore durante la generazione per {car_name}: {e}")
        return None

# Loop per processare le auto
try:
    with open('cars_to_scrape.txt', 'r') as f:
        all_cars = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print("Errore: Il file 'cars_to_scrape.txt' non è stato trovato.")
    all_cars = []

for car in all_cars:
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    filepath = f"brands/{brand}/{slug}.json"
    
    print(f"Generando dati REALI per: {car}...")
    data = get_ai_data(car)
    
    if data:
        os.makedirs(f"brands/{brand}", exist_ok=True)
        # ensure_ascii=False permette di salvare correttamente eventuali caratteri speciali
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f" Salvato: {filepath}")
    
    # Pausa di 4 secondi per non superare i limiti (rate limit) delle API gratuite di Google
    time.sleep(4)
