import os
import json

# Lista per memorizzare le auto trovate
index = {}

# Percorso principale
base_dir = "brands"

if os.path.exists(base_dir):
    for brand in os.listdir(base_dir):
        brand_path = os.path.join(base_dir, brand)
        if os.path.isdir(brand_path):
            index[brand] = []
            for car_file in os.listdir(brand_path):
                if car_file.endswith(".json"):
                    index[brand].append(car_file.replace(".json", ""))

    # Crea il file indice
    with open("index.json", "w") as f:
        json.dump(index, f)
