import os
import json
from duckduckgo_search import DDGS

def get_full_data(car_name):
    # Dati simulati "ricchi" (qui in futuro potresti aggiungere una chiamata a un'API)
    return {
        "brand": car_name.split()[0],
        "model": " ".join(car_name.split()[1:]),
        "image_url": f"https://source.unsplash.com/800x450/?{car_name.replace(' ', '+')}",
        "fitment": {"bolt": "5x114.3", "hub": "66.1mm"},
        "tuning": [
            {"stage": "Stage 1", "desc": "ECU Remap, +30hp, improved throttle response."},
            {"stage": "Stage 2", "desc": "Full Exhaust, High-flow Intake, +60hp."},
            {"stage": "Stage 3", "desc": "Big Turbo, Intercooler, Forged Internals, +150hp."}
        ],
        "shops": ["Street Tuner Lab", "Performance Garage Italy"]
    }

if os.path.exists('cars_to_scrape.txt'):
    with open('cars_to_scrape.txt', 'r') as f:
        for car in [line.strip() for line in f if line.strip()]:
            data = get_full_data(car)
            folder = f"brands/{data['brand'].lower()}"
            os.makedirs(folder, exist_ok=True)
            with open(f"{folder}/{data['model'].lower().replace(' ', '-')}.json", 'w') as f:
                json.dump(data, f, indent=2)
