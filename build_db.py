import os
import json
from duckduckgo_search import DDGS

def get_car_data(car_name):
    print(f"🤖 Ricerca dati per: {car_name}")
    # Qui usiamo la ricerca per simulare un database dinamico
    # In una versione avanzata chiameremo un'API, per ora creiamo la struttura
    return {
        "brand": car_name.split()[0],
        "model": " ".join(car_name.split()[1:]),
        "image_url": "https://image.pollinations.ai/prompt/professional-studio-photography-of-" + car_name.replace(" ", "-"),
        "fitment": {"bolt_pattern": "5x114.3", "hub_bore": "66.1mm"},
        "styling_tips": [{"part": "Front Lip", "desc": "Aerodynamic enhancement"}],
        "tuning_stages": [
            {"stage": "Stage 1", "desc": "ECU Remap + Air Filter"},
            {"stage": "Stage 2", "desc": "Full Exhaust + Downpipe"},
            {"stage": "Stage 3", "desc": "Big Turbo Upgrade"}
        ]
    }

# Legge il file .txt
if os.path.exists('cars_to_scrape.txt'):
    with open('cars_to_scrape.txt', 'r') as f:
        cars = [line.strip() for line in f if line.strip()]

    for car in cars:
        data = get_car_data(car)
        folder = f"brands/{data['brand'].lower()}"
        os.makedirs(folder, exist_ok=True)
        
        file_name = f"{data['model'].lower().replace(' ', '-')}.json"
        with open(os.path.join(folder, file_name), 'w') as f:
            json.dump(data, f, indent=2)
            
print("✅ Database aggiornato automaticamente!")
