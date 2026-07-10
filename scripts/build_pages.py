import os
import json
import markdown
import shutil

CONTENT_DIR = 'content'
DOCS_DIR = 'docs'
TEMPLATE_FILE = 'templates/base.html'
# Hardcoded to match your project subdirectory context seamlessly
BASE_URL = '/YK' 

if os.path.exists(DOCS_DIR):
    shutil.rmtree(DOCS_DIR)
os.makedirs(DOCS_DIR)

with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
    template = f.read()

for root, dirs, files in os.walk(CONTENT_DIR):
    for file in files:
        if file.endswith('.md'):
            md_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, CONTENT_DIR)
            
            if rel_path == '.':
                out_dir = DOCS_DIR
                out_file = file.replace('.md', '.html')
            else:
                out_dir = os.path.join(DOCS_DIR, rel_path)
                out_file = 'index.html' if file == 'content.md' else file.replace('.md', '.html')
                    
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, out_file)
            
            with open(md_path, 'r', encoding='utf-8') as f:
                raw_markdown = f.read()
                
            # Convert markdown syntax
            html_content = markdown.markdown(raw_markdown)
            
            # Post-process links starting with "/" to include our BASE_URL context subfolder
            html_content = html_content.replace('href="/', f'href="{BASE_URL}/')
                
            meta_path = os.path.join(root, 'meta.json')
            title = "Yard Keepers"
            tags_html = ""
            
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as mf:
                    meta = json.load(mf)
                    title = meta.get('title', title)
                    tags = meta.get('tags', [])
                    if tags:
                        tags_html = "<ul class='tags'>" + "".join([f"<li>{t}</li>" for t in tags]) + "</ul>"
            
            # Context-aware injection engine
            page_html = template.replace('{{base_url}}', BASE_URL)
            page_html = page_html.replace('{{title}}', title)
            page_html = page_html.replace('{{content}}', html_content)
            page_html = page_html.replace('{{tags}}', tags_html)
            
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(page_html)

print(f"Build complete. Application contexts mapped cleanly across /{DOCS_DIR}")
