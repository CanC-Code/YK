import os
import glob
import json
import urllib.request
from datetime import datetime
import markdown
import shutil

# Load environment variables for local testing (requires python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def fetch_facebook_feed():
    # The tokens must be present in the environment or a local .env file
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID', 'me')

    if not access_token:
        print("Warning: FB_ACCESS_TOKEN not found in environment.")
        return "<p><em>Facebook feed is currently unavailable (Token not configured).</em></p>"

    try:
        # Fetch the feed using the provided tokens
        url = f"https://graph.facebook.com/v19.0/{page_id}/posts?fields=message,created_time,full_picture,permalink_url,from&access_token={access_token}&limit=10"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        posts = data.get('data', [])
        if not posts:
            return "<p><em>No recent updates found on our Facebook page.</em></p>"

        html = '<div class="native-fb-feed">\n'
        for post in posts:
            message = post.get('message', '')
            created_time = post.get('created_time', '')
            picture = post.get('full_picture', '')
            link = post.get('permalink_url', '#')
            author = post.get('from', {}).get('name', 'Yard Keepers')
            
            try:
                date_obj = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S%z")
                formatted_date = date_obj.strftime("%B %d, %Y")
            except ValueError:
                formatted_date = created_time

            html += '  <div class="native-fb-post">\n'
            html += '    <div class="fb-post-header">\n'
            html += '      <img class="fb-post-avatar" src="/assets/Yard_Keepers.png" alt="Profile">\n'
            html += '      <div class="fb-post-meta">\n'
            html += f'        <span class="fb-post-author">{author}</span>\n'
            html += f'        <span class="fb-post-date"><a href="{link}" target="_blank" rel="noopener noreferrer">{formatted_date}</a></span>\n'
            html += '      </div>\n'
            html += '    </div>\n'
            
            if message:
                safe_msg = message.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                html += f'    <div class="fb-post-content">{safe_msg}</div>\n'
            
            if picture:
                html += f'    <div class="fb-post-media"><img src="{picture}" alt="Post image"></div>\n'
                
            html += '  </div>\n'
        html += '</div>\n'
        
        return html

    except Exception as e:
        print(f"Error fetching Facebook feed: {e}")
        return "<p><em>Facebook feed is currently unavailable (Error fetching data).</em></p>"

def compile_pages():
    content_dir = './content'
    template_path = './templates/base.html'
    output_dir = './docs'

    if not os.path.exists(template_path):
        print(f"Template not found at {template_path}")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    md_files = []
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Frontmatter parsing
        title = "Yard Keepers"
        description = ""
        tags_html = ""
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                content = parts[2]
                for line in frontmatter.split('\n'):
                    if line.startswith('title:'):
                        title = line.replace('title:', '').strip()
                    elif line.startswith('description:'):
                        description = line.replace('description:', '').strip()
                    elif line.startswith('tags:'):
                        tags = [t.strip() for t in line.replace('tags:', '').split(',')]
                        tags_html = '<ul class="tags">' + ''.join([f'<li>{t}</li>' for t in tags]) + '</ul>'

        # Process Facebook Feed Placeholder
        if '[INSERT_FB_FEED]' in content:
            fb_html = fetch_facebook_feed()
            content = content.replace('[INSERT_FB_FEED]', fb_html)

        # Convert Markdown to HTML
        html_body = markdown.markdown(content, extensions=['tables', 'fenced_code'])

        rel_path = os.path.relpath(md_file, content_dir)
        html_path = os.path.join(output_dir, rel_path.replace('.md', '.html'))
        
        if os.path.basename(html_path) == 'content.html':
            html_path = os.path.join(os.path.dirname(html_path), 'index.html')
        elif os.path.basename(html_path) != 'index.html':
            name_without_ext = os.path.splitext(os.path.basename(html_path))[0]
            html_path = os.path.join(os.path.dirname(html_path), name_without_ext, 'index.html')

        os.makedirs(os.path.dirname(html_path), exist_ok=True)

        canonical_url = f"https://yardkeepers.ca/{os.path.dirname(rel_path)}/" if os.path.dirname(rel_path) else "https://yardkeepers.ca/"
        
        final_html = template.replace('{{title}}', title)
        final_html = final_html.replace('{{description}}', description)
        final_html = final_html.replace('{{canonical_url}}', canonical_url)
        final_html = final_html.replace('{{base_url}}', '')
        final_html = final_html.replace('{{tags}}', tags_html)
        final_html = final_html.replace('{{content}}', html_body)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

    print("Pages compiled successfully.")

if __name__ == "__main__":
    compile_pages()
