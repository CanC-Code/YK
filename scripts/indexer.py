import os
import json

CONTENT_DIR = 'content'
DOCS_DIR = 'docs'
INDEX_FILE = os.path.join(DOCS_DIR, 'search_index.json')

index_data = []

for root, dirs, files in os.walk(CONTENT_DIR):
    if 'meta.json' in files:
        rel_path = os.path.relpath(root, CONTENT_DIR)
        url_path = f"/{rel_path}/" # Assumes content.md compiles to index.html
        
        with open(os.path.join(root, 'meta.json'), 'r', encoding='utf-8') as f:
            meta = json.load(f)
            
        index_data.append({
            "url": url_path,
            "title": meta.get('title', 'Untitled'),
            "tags": meta.get('tags', []),
            "description": meta.get('description', '')
        })

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, indent=2)
    
print(f"Index generated at {INDEX_FILE}")
