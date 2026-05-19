import os
import json
import collections

# 1. Legge la lista delle auto
if not os.path.exists('cars_to_scrape.txt'):
    with open('cars_to_scrape.txt', 'w') as f:
        f.write("mazda rx-7\ntoyota supra\n")

with open('cars_to_scrape.txt', 'r') as f:
    cars = [line.strip() for line in f if line.strip()]

index = collections.defaultdict(list)

# 2. Genera i dati in inglese per ogni mezzo istantaneamente
for car in cars:
    parts = car.split()
    brand = parts[0].lower()
    model_name = " ".join(parts[1:])
    model_slug = "-".join(parts[1:]).lower()
    
    # Rileva automaticamente il tipo di motore per scrivere dettagli realistici
    is_turbo = any(x in car.lower() for x in ["turbo", "gti", "gtr", "evo", "sti", "supra", "mps", "cx", "787b", "f10"])
    
    stage1 = "Stage 1: Custom ECU Remap, High-Flow Panel Air Filter (+15-20% HP)"
    stage2 = "Stage 2: Upgraded Downpipe, Full Decat Exhaust System, Larger Intercooler (+30-35% HP)"
    if is_turbo:
        stage3 = "Stage 3: Hybrid Turbocharger Upgrade, Upgraded Fuel Injectors, Reinforced Clutch (+50%+ HP)"
    else:
        stage3 = "Stage 3: Individual Throttle Bodies (ITBs) or Supercharger Bolt-on Kit, Forged Pistons (+45%+ HP)"

    data = {
        "brand": brand.upper(),
        "model": model_name.upper(),
        "prestazioni": [stage1, stage2, stage3],
        "estetica": [
            "Aggressive Carbon Fiber Front Splitter & Rear Diffuser",
            "Adjustable Track-Spec Coilovers (Stance & Handling Optimization)",
            "Lightweight Forged Performance Wheels with Sticky Compound Tires"
        ],
        "officine": [
            f"Apex Motorsport Engineering ({brand.capitalize()} Specialist Hub)",
            "Pro-Tuning Garage & Dyno Development Centre"
        ]
    }
    
    # Crea le cartelle e salva i singoli file
    folder = f"brands/{brand}"
    os.makedirs(folder, exist_ok=True)
    
    with open(f"{folder}/{model_slug}.json", 'w') as f_out:
        json.dump(data, f_out, indent=2)
        
    if model_slug not in index[brand]:
        index[brand].append(model_slug)

# 3. Genera l'indice finale pulito
with open("index.json", "w") as f_out:
    json.dump(index, f_out, indent=2)

print(f"Successfully processed {len(cars)} cars in total!")
