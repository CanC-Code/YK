import os
import json
import markdown
import shutil
import urllib.request
import urllib.error
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

# Fetch Facebook Posts dynamically if the token secret is available in the environment
def fetch_facebook_feed_html():
    token = os.environ.get('FB_PAGE_ACCESS_TOKEN')
    if not token:
        return "<p><em>Facebook feed is currently unavailable (Token not configured).</em></p>"
    
    # Graph API endpoint for page posts (fetching message, created_time, full_picture, attachments)
    api_url = f"https://graph.facebook.com/v19.0/me/posts?fields=message,created_time,full_picture,permalink_url&access_token={token}"
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'YardKeepers-Compiler/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            posts = data.get('data', [])
            
            if not posts:
                return "<p>No recent posts found on Facebook.</p>"
            
            feed_html = '<div class="native-fb-feed">\n'
            for post in posts:
                message = post.get('message', '')
                created_time = post.get('created_time', '')
                picture = post.get('full_picture', '')
                permalink = post.get('permalink_url', '#')
                
                # Format date nicely
                try:
                    dt = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
                    formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
                except Exception:
                    formatted_date = "Recent Update"

                feed_html += '  <div class="native-fb-post">\n'
                feed_html += '    <div class="fb-post-header">\n'
                feed_html += f'      <img src="{BASE_URL}/assets/Yard_Keepers.png" alt="Yard Keepers Logo" class="fb-post-avatar">\n'
                feed_html += '      <div class="fb-post-meta">\n'
                feed_html += '        <span class="fb-post-author">Yard Keepers</span>\n'
                feed_html += f'        <span class="fb-post-date"><a href="{permalink}" target="_blank" rel="noopener">{formatted_date}</a></span>\n'
                feed_html += '      </div>\n'
                feed_html += '    </div>\n'
                
                if message:
                    feed_html += f'    <div class="fb-post-content">{message}</div>\n'
                
                if picture:
                    feed_html += '    <div class="fb-post-media">\n'
                    feed_html += f'      <img src="{picture}" alt="Facebook post media" loading="lazy">\n'
                    feed_html += '    </div>\n'
                
                feed_html += '  </div>\n'
            
            feed_html += '</div>\n'
            return feed_html
            
    except Exception as e:
        return f"<p><em>Unable to load live Facebook feed at the moment. Please visit our <a href='https://www.facebook.com/YardKeepers/' target='_blank'>Facebook Page</a> directly.</em></p>"

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
            
            # If compiling the facebook page content, inject the dynamic native feed
            if rel_path == 'facebook':
                live_feed = fetch_facebook_feed_html()
                html_content = html_content.replace('[INSERT_FB_FEED]', live_feed)

            html_content = html_content.replace('href="/', f'href="{BASE_URL}/')
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

            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(page_html)

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

# Generate robots.txt
robots_path = os.path.join(DOCS_DIR, 'robots.txt')
robots_content = (
    f"User-agent: *\n"
    f"Allow: /\n\n"
    f"Sitemap: {DOMAIN}/sitemap.xml\n"
)

with open(robots_path, 'w', encoding='utf-8') as rf:
    rf.write(robots_content)

print(f"Build complete. Companion Markdown files created. Sitemap and robots.txt updated with canonical indexing parameters.")
