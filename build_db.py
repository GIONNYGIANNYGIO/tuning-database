import os
import json
import time
import requests

# Chiavi recuperate dai Secrets di GitHub
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

# URL diretto per le API di Gemini
API_URL_GEMINI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

# Alziamo a 20 auto a sessione
BATCH_SIZE = 20  

def chiedi_a_gemini_diretto(car_name, prompt):
    """Chiama Gemini 2.0 tramite richiesta HTTP diretta, evitando blocchi della libreria"""
    if not GEMINI_KEY:
        return None
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(API_URL_GEMINI, headers=headers, json=payload, timeout=20)
        if r.status_code == 429 or "ResourceExhausted" in r.text or "limit: 0" in r.text:
            print("-> [Gemini] Quota giornaliera o limite raggiunto. Attivo il paracadute Mistral AI...")
            return "DAILY_LIMIT"
        if r.status_code == 200:
            res = r.json()
            raw_text = res['candidates'][0]['content']['parts'][0]['text'].strip()
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
    except Exception:
        return None
    return None

def chiedi_a_mistral(car_name, prompt):
    """Paracadute: Chiama Mistral AI se Gemini ha esaurito la quota giornaliera"""
    if not MISTRAL_KEY:
        print("-> [Mistral] Chiave MISTRAL_API_KEY non configurata nei Secrets di GitHub.")
        return None
        
    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        if r.status_code == 429:
            print("-> [Mistral] Limite di quota raggiunto anche su Mistral.")
            return "DAILY_LIMIT"
        if r.status_code == 200:
            res = r.json()
            raw_text = res['choices'][0]['message']['content'].strip()
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
    except Exception:
        return None
    return None

def get_ai_data(car_name, forza_mistral=False):
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
    
    if forza_mistral:
        print(f"-> [Staffetta] Uso direttamente Mistral per {car_name}...")
        return chiedi_a_mistral(car_name, prompt), True

    # Tentativo diretto con Gemini
    res_g = chiedi_a_gemini_diretto(car_name, prompt)
    if res_g == "DAILY_LIMIT":
        return chiedi_a_mistral(car_name, prompt), True
    elif res_g:
        return res_g, False
        
    print(f"-> [Gemini] Errore di risposta. Tento il backup su Mistral per {car_name}...")
    return chiedi_a_mistral(car_name, prompt), False

try:
    with open('cars_to_scrape.txt', 'r') as f:
        all_cars = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print("Errore: 'cars_to_scrape.txt' non trovato.")
    all_cars = []

processed_count = 0
forza_mistral_flag = False

for car in all_cars:
    if processed_count >= BATCH_SIZE:
        print(f"Raggiunto il limite di {BATCH_SIZE} auto per questo turno.")
        break
        
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    filepath = f"brands/{brand}/{slug}.json"
    
    if os.path.exists(filepath):
        continue
    
    print(f"Generando dati per: {car}...")
    data, cambio_ai = get_ai_data(car, forza_mistral=forza_mistral_flag)
    
    if cambio_ai:
        forza_mistral_flag = True
    
    if data == "DAILY_LIMIT":
        print("Blocco di sicurezza: Anche la quota di Mistral è terminata. Arresto lo script.")
        break
        
    if data:
        os.makedirs(f"brands/{brand}", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Salvato: {filepath}")
        
        processed_count += 1
        time.sleep(35) 
    else:
        print(f"Saltata: {car} a causa di un errore di generazione.")
        time.sleep(5)

print(f"\nSessione completata. Auto elaborate in questo turno: {processed_count}")
