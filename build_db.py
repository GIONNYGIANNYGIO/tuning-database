import os
import json
from duckduckgo_search import DDGS

# Funzione per cercare immagine
def get_image(brand, model):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(f"{brand} {model} car", max_results=1))
            return results[0]['image'] if results else ""
    except:
        return ""

# Leggi la lista
if os.path.exists('cars_to_scrape.txt'):
    with open('cars_to_scrape.txt', 'r') as f:
        cars = [line.strip() for line in f if line.strip()]

    for car in cars:
        parts = car.split()
        brand = parts[0].lower()
        model = "-".join(parts[1:]).lower()
        
        data = {
            "brand": parts[0],
            "model": " ".join(parts[1:]),
            "image_url": get_image(parts[0], " ".join(parts[1:])),
            "tuning_stages": [{"stage": "Stage 1", "desc": "Remap"}]
        }
        
        folder = f"brands/{brand}"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/{model}.json", 'w') as f:
            json.dump(data, f, indent=2)
