import os
import json
import markdown
import shutil
from datetime import datetime

CONTENT_DIR = 'content'
DOCS_DIR = 'docs'
TEMPLATE_FILE = 'templates/base.html'
ASSETS_DIR = 'assets'
BASE_URL = ''
DOMAIN = 'https://yardkeepers.ca'

if os.path.exists(DOCS_DIR):
    shutil.rmtree(DOCS_DIR)
os.makedirs(DOCS_DIR, exist_ok=True)

if os.path.exists(ASSETS_DIR):
    shutil.copytree(ASSETS_DIR, os.path.join(DOCS_DIR, 'assets'))

with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
    template_html = f.read()

sitemap_urls = []

for root, dirs, files in os.walk(CONTENT_DIR):
    for file in files:
        if file.endswith('.md'):
            md_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, CONTENT_DIR)

            if rel_path == '.':
                out_dir = DOCS_DIR
                out_file = file.replace('.md', '.html')
                url_path = '/'
            else:
                out_dir = os.path.join(DOCS_DIR, rel_path)
                out_file = 'index.html' if file == 'content.md' else file.replace('.md', '.html')
                url_path = f"/{rel_path}/"

            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, out_file)

            with open(md_path, 'r', encoding='utf-8') as f:
                raw_markdown = f.read()

            html_content = markdown.markdown(raw_markdown)
            html_content = html_content.replace('href="/', f'href="{BASE_URL}/')

            # Auto-route local image links inside HTML to use base URL and compiled webp path extension
            html_content = html_content.replace('src="/media/', f'src="{BASE_URL}/media/')

            meta_path = os.path.join(root, 'meta.json')
            title = "Yard Keepers"
            description = "Professional property maintenance and seasonal yard operations across Central Alberta."
            tags_html = ""

            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as mf:
                    meta = json.load(mf)
                    title = meta.get('title', title)
                    description = meta.get('description', description)
                    tags = meta.get('tags', [])
                    if tags:
                        tags_html = "<ul class='tags'>" + "".join([f"<li>{t}</li>" for t in tags]) + "</ul>"
            else:
                if rel_path != '.':
                    title = rel_path.replace('-', ' ').title()

            full_url = f"{DOMAIN}{BASE_URL}{url_path}"

            page_html = template_html.replace('{{base_url}}', BASE_URL)
            page_html = page_html.replace('{{title}}', title)
            page_html = page_html.replace('{{description}}', description)
            page_html = page_html.replace('{{content}}', html_content)
            page_html = page_html.replace('{{tags}}', tags_html)
            page_html = page_html.replace('{{canonical_url}}', full_url)

            # Write out the standard production HTML page
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(page_html)

            # Write out a parallel raw Markdown companion file for AI agent content negotiation
            md_out_file = out_file.replace('.html', '.md')
            md_out_path = os.path.join(out_dir, md_out_file)
            with open(md_out_path, 'w', encoding='utf-8') as f:
                f.write(raw_markdown)

            sitemap_urls.append(full_url)

# Generate XML Sitemap
sitemap_path = os.path.join(DOCS_DIR, 'sitemap.xml')
today = datetime.now().strftime('%Y-%m-%d')

xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for url in sitemap_urls:
    xml_content += '  <url>\n'
    xml_content += f'    <loc>{url}</loc>\n'
    xml_content += f'    <lastmod>{today}</lastmod>\n'
    xml_content += '    <changefreq>weekly</changefreq>\n'
    xml_content += '    <priority>0.8</priority>\n'
    xml_content += '  </url>\n'
xml_content += '</urlset>\n'

with open(sitemap_path, 'w', encoding='utf-8') as sf:
    sf.write(xml_content)

# Generate robots.txt with standard indexing directives to ensure strict compliance
robots_path = os.path.join(DOCS_DIR, 'robots.txt')
robots_content = (
    f"User-agent: *\n"
    f"Allow: /\n\n"
    f"Sitemap: {DOMAIN}/sitemap.xml\n"
)

with open(robots_path, 'w', encoding='utf-8') as rf:
    rf.write(robots_content)

print(f"Build complete. Companion Markdown files created. Sitemap and robots.txt updated with canonical indexing parameters.")
