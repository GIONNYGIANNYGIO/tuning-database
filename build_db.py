import os
import json
import collections
import re

# Crea un file finto se non esiste
if not os.path.exists('cars_to_scrape.txt'):
    with open('cars_to_scrape.txt', 'w') as f:
        f.write("mazda rx-7\ntoyota supra\n")

# Legge la tua lista
with open('cars_to_scrape.txt', 'r') as f:
    cars = [line.strip() for line in f if line.strip()]

index = collections.defaultdict(list)

# LA PIALLA: distrugge qualsiasi carattere speciale (come la barra / della Dodge)
def clean_filename(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

for car in cars:
    # Rimuove i vari incollati per sbaglio
    car = re.sub(r'\\s*', '', car).strip()
    if not car:
        continue

    parts = car.split()
    if len(parts) < 2:
        continue
        
    brand_raw = parts[0]
    model_raw = " ".join(parts[1:])
    
    # Applica la pialla per creare cartelle e file perfetti
    brand_clean = clean_filename(brand_raw)
    model_slug = clean_filename(model_raw)
    
    # Rileva il tipo di motore
    is_turbo = any(x in car.lower() for x in ["turbo", "gti", "gtr", "evo", "sti", "supra", "mps", "cx", "787b", "f10"])
    
    stage1 = "Stage 1: Custom ECU Remap, High-Flow Panel Air Filter (+15-20% HP)"
    stage2 = "Stage 2: Upgraded Downpipe, Full Decat Exhaust System, Larger Intercooler (+30-35% HP)"
    if is_turbo:
        stage3 = "Stage 3: Hybrid Turbocharger Upgrade, Upgraded Fuel Injectors, Reinforced Clutch (+50%+ HP)"
    else:
        stage3 = "Stage 3: Individual Throttle Bodies (ITBs) or Supercharger Bolt-on Kit, Forged Pistons (+45%+ HP)"

    # Crea il file JSON (sempre tutto in inglese per il sito internazionale)
    data = {
        "brand": brand_raw.upper(),
        "model": model_raw.upper(),
        "prestazioni": [stage1, stage2, stage3],
        "estetica": [
            "Aggressive Carbon Fiber Front Splitter & Rear Diffuser",
            "Adjustable Track-Spec Coilovers (Stance & Handling Optimization)",
            "Lightweight Forged Performance Wheels with Sticky Compound Tires"
        ],
        "officine": [
            f"Apex Motorsport Engineering ({brand_raw.capitalize()} Specialist Hub)",
            "Pro-Tuning Garage & Dyno Development Centre"
        ]
    }
    
    # Crea cartella e salva
    folder = f"brands/{brand_clean}"
    os.makedirs(folder, exist_ok=True)
    
    filepath = f"{folder}/{model_slug}.json"
    with open(filepath, 'w') as f_out:
        json.dump(data, f_out, indent=2)
        
    if model_slug not in index[brand_clean]:
        index[brand_clean].append(model_slug)

# Salva l'indice
with open("index.json", "w") as f_out:
    json.dump(index, f_out, indent=2)

print(f"Successfully processed {len(cars)} cars in total!")
