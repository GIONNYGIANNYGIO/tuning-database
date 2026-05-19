import os
import json
import google.generativeai as genai

# Configurazione AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_tuning_data(car_name):
    prompt = f"""
    Sei un esperto di tuning automobilistico. Fornisci i dati per: {car_name}.
    Rispondi SOLO con un oggetto JSON valido (senza testo extra) con questa struttura:
    {{
      "brand": "{car_name.split()[0]}",
      "model": "{" ".join(car_name.split()[1:])}",
      "estetica": ["Elenco di 3 modifiche estetiche comuni"],
      "prestazioni": ["Stage 1: dettagli", "Stage 2: dettagli", "Stage 3: dettagli"],
      "officine": ["Nome officina 1 (Città)", "Nome officina 2 (Città)"]
    }}
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.replace("```json", "").replace("```", ""))

# Lettura file e generazione
with open('cars_to_scrape.txt', 'r') as f:
    for line in f:
        car = line.strip()
        if car:
            data = get_tuning_data(car)
            folder = f"brands/{data['brand'].lower()}"
            os.makedirs(folder, exist_ok=True)
            with open(f"{folder}/{data['model'].lower().replace(' ', '-')}.json", 'w') as f:
                json.dump(data, f, indent=2)

# AGGIORNAMENTO AUTOMATICO INDICE (LASCIA SOLO QUESTO)
import collections
index = collections.defaultdict(list)
# Scansioniamo la cartella brands
for brand in os.listdir('brands'):
    brand_path = os.path.join('brands', brand)
    if os.path.isdir(brand_path):
        for car_file in os.listdir(brand_path):
            if car_file.endswith(".json"):
                # Aggiungiamo il modello all'indice
                index[brand].append(car_file.replace(".json", ""))

# Salviamo solo index.json
with open("index.json", "w") as f:
    json.dump(index, f, indent=2)
