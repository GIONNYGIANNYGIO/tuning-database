import os
import json
import time
from duckduckgo_search import DDGS

def get_real_car_image(brand, model):
    query = f"{brand} {model} car stock photography high resolution"
    print(f"🔍 Searching real photo for: {brand} {model}...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=2))
            if results:
                return results[0]['image']
    except Exception as e:
        print(f"⚠️ Error fetching image for {brand} {model}: {e}")
    
    # Fallback if image is not found
    return "https://via.placeholder.com/800x450.png?text=Image+Not+Found"

# 1. Open the master list
with open('master_list.json', 'r', encoding='utf-8') as f:
    car_list = json.load(f)

# 2. Process each car
for car in car_list:
    folder = car['folder']
    filename = car['filename']
    data = car['data']
    
    # Create directory if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    
    file_path = os.path.join(folder, filename)
    
    # Get image
    data['image_url'] = get_real_car_image(data['brand'], data['model'])
    time.sleep(1) # Small pause to not block the search engine
    
    # Write the individual JSON file
    with open(file_path, 'w', encoding='utf-8') as out_file:
        json.dump(data, out_file, indent=2, ensure_ascii=False)
        
    print(f"✅ Created: {file_path}")

print("🚀 ALL DONE! Database built successfully.")
