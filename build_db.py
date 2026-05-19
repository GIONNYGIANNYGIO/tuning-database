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
# Aggiungi questo alla fine del tuo script Python su GitHub
import json

def update_map():
    db_map = {}
    for brand in os.listdir('brands'):
        if os.path.isdir(os.path.join('brands', brand)):
            db_map[brand] = [f.replace('.json', '') for f in os.listdir(os.path.join('brands', brand)) if f.endswith('.json')]
    
    with open('database_map.json', 'w') as f:
        json.dump(db_map, f)

update_map()
