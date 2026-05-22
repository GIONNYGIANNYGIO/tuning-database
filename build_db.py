import os
import json
import time
import requests

# Chiave Mistral recuperata dai Secrets di GitHub
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

# Alziamo a 20 auto a sessione
BATCH_SIZE = 20  

def chiedi_a_mistral(car_name, prompt):
    """Chiama Mistral AI per la generazione del profilo di tuning"""
    if not MISTRAL_KEY:
        print("-> [Mistral] Chiave MISTRAL_API_KEY non configurata nei Secrets di GitHub.")
        return None
        
    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-large-latest", # Modello avanzato per la qualità dei codici motore e dettagli
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=25)
        if r.status_code == 429:
            print("-> [Mistral] Limite di quota (Rate Limit) raggiunto su Mistral.")
            return "DAILY_LIMIT"
        if r.status_code == 200:
            res = r.json()
            raw_text = res['choices'][0]['message']['content'].strip()
            # Pulizia rapida di eventuali blocchi markdown json
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
        else:
            print(f"-> [Mistral] Errore API (Status: {r.status_code}): {r.text}")
            return None
    except Exception as e:
        print(f"-> Errore imprevisto su Mistral per {car_name}: {e}")
        return None

def get_ai_data(car_name):
    brand_name = car_name.split()[0]
    
    # Puliamo il nome per il file interno eliminando il brand duplicato nel campo model
    clean_model_name = car_name.replace(brand_name, "", 1).strip()
    
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
        "model": "{clean_model_name.upper()}",
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
    
    return chiedi_a_mistral(car_name, prompt)

# Carica l'indice esistente o ne crea uno nuovo vuoto
index_filepath = "index.json"
if os.path.exists(index_filepath):
    try:
        with open(index_filepath, 'r', encoding='utf-8') as f:
            index_db = json.load(f)
    except Exception:
        index_db = {}
else:
    index_db = {}

try:
    with open('cars_to_scrape.txt', 'r') as f:
        all_cars = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print("Errore: 'cars_to_scrape.txt' non trovato.")
    all_cars = []

processed_count = 0
indice_modificato = False

for car in all_cars:
    if processed_count >= BATCH_SIZE:
        print(f"Raggiunto il limite di {BATCH_SIZE} auto per questo turno.")
        break
        
    brand = car.split()[0].lower()
    
    # Generiamo lo slug del modello senza ripetere il brand (es: "supra-mk4")
    model_part = car.replace(car.split()[0], "", 1).strip()
    slug = model_part.lower().replace(' ', '-').replace('/', '-')
    
    filepath = f"brands/{brand}/{slug}.json"
    
    # Se il file esiste già sul repository, verifichiamo che sia indicizzato e saltiamo la generazione
    if os.path.exists(filepath):
        if brand not in index_db:
            index_db[brand] = []
        if slug not in index_db[brand]:
            index_db[brand].append(slug)
            indice_modificato = True
        continue
    
    print(f"Generando dati (via Mistral) per: {car}...")
    data = get_ai_data(car)
    
    if data == "DAILY_LIMIT":
        print("Blocco di sicurezza: La quota di Mistral è terminata. Arresto lo script.")
        break
        
    if data:
        os.makedirs(f"brands/{brand}", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Salvato: {filepath}")
        
        # Aggiorna la struttura dell'index.json
        if brand not in index_db:
            index_db[brand] = []
        if slug not in index_db[brand]:
            index_db[brand].append(slug)
        
        indice_modificato = True
        processed_count += 1
        # Pausa di 35 secondi per rispettare i limiti di frequenza gratuiti di Mistral
        time.sleep(35) 
    else:
        print(f"Saltata: {car} a causa di un errore di generazione.")
        time.sleep(5)

# Salva l'index.json aggiornato se sono state aggiunte nuove auto
if indice_modificato:
    with open(index_filepath, 'w', encoding='utf-8') as f:
        json.dump(index_db, f, indent=2, ensure_ascii=False)
    print("Indice index.json aggiornato e sincronizzato con il widget!")

print(f"\nSessione completata. Auto elaborate in questo turno: {processed_count}")
