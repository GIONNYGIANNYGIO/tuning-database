import os
import json
import time
import requests
from google import genai

# Inizializzazione Client Gemini (Libreria Nuova)
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Chiave Mistral recuperata dai Secrets di GitHub
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

# Alziamo a 20 auto a sessione per finire in circa 2 mesi
BATCH_SIZE = 20  

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
        "model": "mistral-large-latest", # Modello avanzato per non perdere la qualità e i dettagli sui codici motore
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        if r.status_code == 429:
            print("-> [Mistral] Limite di quota raggiunto anche su Mistral.")
            return "DAILY_LIMIT"
        if r.status_code == 200:
            res = r.json()
            raw_text = res['choices'][0]['message']['content'].strip()
            # Pulizia rapida di eventuali blocchi markdown
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
    except Exception as e:
        print(f"-> Errore imprevisto su Mistral per {car_name}: {e}")
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
    
    # Se nei cicli precedenti abbiamo già rilevato il blocco definitivo di Gemini, andiamo diretti su Mistral
    if forza_mistral:
        print(f"-> [Staffetta] Uso direttamente Mistral per {car_name}...")
        return chiedi_a_mistral(car_name, prompt), True

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text), False
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                # Se dice 'limit: 0' significa che la quota giornaliera di Gemini è finita
                if "limit: 0" in error_msg:
                    print("-> [Gemini] Quota giornaliera di Google TERMINATA. Attivo il paracadute Mistral AI...")
                    # Passiamo immediatamente a Mistral per l'auto corrente
                    res_m = chiedi_a_mistral(car_name, prompt)
                    return res_m, True # True indica che da adesso in poi dobbiamo usare direttamente Mistral
                
                # Altrimenti è solo il limite al minuto (RPM): aspettiamo e ritentiamo con Gemini
                wait_time = 90
                print(f"-> [Gemini] Limite al minuto raggiunto per {car_name}. Pausa di {wait_time}s (Tentativo {attempt+1}/3)...")
                time.sleep(wait_time)
            else:
                print(f"-> Errore imprevisto su Gemini per {car_name}: {e}")
                return None, False
                
    return None, False

try:
    with open('cars_to_scrape.txt', 'r') as f:
        all_cars = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    print("Errore: 'cars_to_scrape.txt' non trovato.")
    all_cars = []

processed_count = 0
forza_mistral_flag = False  # Diventa True quando Gemini finisce i gettoni giornalieri

for car in all_cars:
    if processed_count >= BATCH_SIZE:
        print(f"Raggiunto il limite di {BATCH_SIZE} auto per questo turno.")
        break
        
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    filepath = f"brands/{brand}/{slug}.json"
    
    if os.path.exists(filepath):
        continue
    
    print(f"\nGenerando dati per: {car}...")
    data, cambio_ai = get_ai_data(car, forza_mistral=forza_mistral_flag)
    
    # Se get_ai_data ci dice che dobbiamo passare a Mistral stabilmente, aggiorniamo il flag
    if cambio_ai:
        forza_mistral_flag = True
    
    if data == "DAILY_LIMIT":
        print("Blocco di sicurezza: Anche la quota di Mistral è terminata. Arresto lo script.")
        break
        
    if data:
        os.makedirs(f"brands/{brand}", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f" Salvato: {filepath}")
        
        processed_count += 1
        # 35 secondi di pausa tra auto per rispettare i limiti di frequenza delle API
        time.sleep(35) 
    else:
        print(f"Saltata: {car} a causa di un errore di generazione.")
        time.sleep(5)

print(f"\nSessione completata. Auto elaborate in questo turno: {processed_count}")
