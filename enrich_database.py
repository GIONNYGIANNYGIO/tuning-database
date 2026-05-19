import os
import json
import re
import time
from urllib.parse import quote
import urllib.request

# Librerie stabili esterne per traduzione e ricerca immagini reali
try:
    from deep_translator import GoogleTranslator
except ImportError:
    os.system('pip install deep-translator')
    from deep_translator import GoogleTranslator

try:
    from duckduckgo_search import DDGS
except ImportError:
    os.system('pip install duckduckgo-search')
    from duckduckgo_search import DDGS

def get_real_car_image(brand, model):
    query = f"{brand} {model} car stock wallpaper high resolution"
    print(f"🔍 Cerco foto reale per: {brand} {model}...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=3))
            if results:
                # Prende la prima immagine reale trovata su internet
                return results[0]['image']
    except Exception as e:
        print(f"⚠️ Errore ricerca immagine per {brand} {model}: {e}")
    # Fallback di sicurezza ad alta precisione se i server di ricerca sono sovraccarichi
    clean_b = re.sub(r'[^a-zA-Z0-9]', ' ', brand)
    clean_m = re.sub(r'[^a-zA-Z0-9]', ' ', model)
    return f"https://image.pollinations.ai/prompt/professional-automotive-photography-of-{quote(clean_b)}-{quote(clean_m)}-clear-background?width=1200&height=600&nologo=true"

def translate_it_to_en(text):
    if not text or text.strip() == "":
        return ""
    if re.match(r'^[0-9A-Za-z\s\-\.\,\/\#\+\:]+$', text) and len(text) < 5:
        return text # Non tradurre codici o sigle corte
    try:
        return GoogleTranslator(source='it', target='en').translate(text)
    except Exception as e:
        print(f"⚠️ Errore traduzione testo '{text}': {e}")
        return text

# 1. PROCESSA I VEICOLI (BRANDS)
brands_dir = 'brands'
if os.path.exists(brands_dir):
    for brand_name in os.listdir(brands_dir):
        brand_path = os.path.join(brands_dir, brand_name)
        if os.path.isdir(brand_path):
            for file_name in os.listdir(brand_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(brand_path, file_name)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"📦 Elaborazione veicolo: {data.get('brand')} {data.get('model')}")
                    
                    # Genera l'immagine REALE solo se non è già presente nel JSON
                    if not data.get('image_url'):
                        data['image_url'] = get_real_car_image(data.get('brand', brand_name), data.get('model', file_name.replace('.json','')))
                    
                    # Traduzione parti estetiche
                    if 'styling_tips' in data:
                        for item in data['styling_tips']:
                            if 'part' in item and not item.get('part_en'):
                                item['part_en'] = translate_it_to_en(item['part'])
                            if 'desc' in item and not item.get('desc_en'):
                                item['desc_en'] = translate_it_to_en(item['desc'])
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

# 2. PROCESSA I MOTORI (ENGINES)
engines_dir = 'engines'
if os.path.exists(engines_dir):
    for file_name in os.listdir(engines_dir):
        if file_name.endswith('.json'):
            file_path = os.path.join(engines_dir, file_name)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"⚙️ Elaborazione motore: {file_name}")
            
            if 'tuning_tips' in data:
                for step in data['tuning_tips']:
                    if 'stage' in step and not step.get('stage_en'):
                        step['stage_en'] = translate_it_to_en(step['stage'])
                    if 'part' in step and not step.get('part_en'):
                        step['part_en'] = translate_it_to_en(step['part'])
                    if 'desc' in step and not step.get('desc_en'):
                        step['desc_en'] = translate_it_to_en(step['desc'])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ DATABASE AGGIORNATO E TRADOTTO CON SUCCESSO!")
