import os, json, time, google.generativeai as genai

# Configurazione API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_data(car_name):
    prompt = f"Fornisci dati tuning reali per '{car_name}'. Rispondi SOLO in formato JSON con chiavi: 'prestazioni', 'estetica', 'officine'. Ogni lista deve avere 3 elementi tecnici reali (es. marche, modelli di componenti). Non aggiungere altro testo."
    try:
        response = model.generate_content(prompt)
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except:
        return None

# Caricamento lista
with open('cars_to_scrape.txt', 'r') as f:
    all_cars = [l.strip() for l in f if l.strip()]

# Processo batch: 30 auto ogni 6 ore
processed_count = 0
for car in all_cars:
    if processed_count >= 30: break 
    
    brand = car.split()[0].lower()
    slug = car.lower().replace(' ', '-').replace('/', '-')
    folder = f"brands/{brand}"
    filepath = f"{folder}/{slug}.json"
    
    if os.path.exists(filepath): continue
        
    print(f"Generando dati per: {car}...")
    data = get_ai_data(car)
    if data:
        os.makedirs(folder, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Aggiorna anche index.json (fondamentale per il sito)
        index_file = "index.json"
        index = {}
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index = json.load(f)
        
        if brand not in index: index[brand] = []
        if slug not in index[brand]: index[brand].append(slug)
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
            
        processed_count += 1
        time.sleep(5)
