import os
import json
import markdown
import shutil

CONTENT_DIR = 'content'
DOCS_DIR = 'docs'
TEMPLATE_FILE = 'templates/base.html'

# 1. Prepare the output directory
if os.path.exists(DOCS_DIR):
    shutil.rmtree(DOCS_DIR)
os.makedirs(DOCS_DIR)

# 2. Load the base HTML template
with open(TEMPLATE_FILE, 'r') as f:
    template = f.read()

# 3. Process all content files
for root, dirs, files in os.walk(CONTENT_DIR):
    for file in files:
        if file.endswith('.md'):
            md_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, CONTENT_DIR)
            
            # Determine output paths for clean URLs
            if rel_path == '.':
                out_dir = DOCS_DIR
                out_file = file.replace('.md', '.html')
            else:
                out_dir = os.path.join(DOCS_DIR, rel_path)
                out_file = 'index.html' if file == 'content.md' else file.replace('.md', '.html')
                    
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, out_file)
            
            # Read and convert Markdown
            with open(md_path, 'r', encoding='utf-8') as f:
                html_content = markdown.markdown(f.read())
                
            # Parse associated meta.json if it exists in the same folder
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
            
            # Inject data into template
            page_html = template.replace('{{title}}', title)
            page_html = page_html.replace('{{content}}', html_content)
            page_html = page_html.replace('{{tags}}', tags_html)
            
            # Write final HTML file
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(page_html)

print(f"Build complete. Files written to /{DOCS_DIR}")
