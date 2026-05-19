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
