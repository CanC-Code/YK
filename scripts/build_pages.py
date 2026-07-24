import os
import glob
import json
import urllib.request
from datetime import datetime
import markdown

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def fetch_facebook_feed():
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID', 'me')

    if not access_token:
        print("Warning: FB_ACCESS_TOKEN not found in environment.")
        return "<p><em>Facebook feed is currently unavailable (Token not configured).</em></p>"

    try:
        # Expanded fields to properly capture shared posts, stories, and nested attachments
        url = f"https://graph.facebook.com/v19.0/{page_id}/posts?fields=message,story,created_time,permalink_url,from{{name,picture}},attachments{{media,subattachments,title,description,type}}&access_token={access_token}&limit=20"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        posts = data.get('data', [])
        if not posts:
            return "<p><em>No recent updates found on our Facebook page.</em></p>"

        html = '<div class="native-fb-feed">\n'
        for post in posts:
            # Fallback text logic for shared posts or status updates stored in 'story'
            message = post.get('message', '') or post.get('story', '')
            created_time = post.get('created_time', '')
            link = post.get('permalink_url', '#')
            
            author_data = post.get('from', {})
            author = author_data.get('name', 'Yard Keepers')
            author_pic = author_data.get('picture', {}).get('data', {}).get('url', '/assets/Yard_Keepers.png')
            
            try:
                date_obj = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S%z")
                formatted_date = date_obj.strftime("%B %d, %Y")
            except ValueError:
                formatted_date = created_time

            html += '  <div class="native-fb-post">\n'
            html += '    <div class="fb-post-header">\n'
            html += f'      <a href="{link}" target="_blank" rel="noopener noreferrer" class="fb-author-link-avatar">\n'
            html += f'        <img class="fb-post-avatar" src="{author_pic}" alt="{author} Profile">\n'
            html += '      </a>\n'
            html += '      <div class="fb-post-meta">\n'
            html += f'        <span class="fb-post-author"><a href="{link}" target="_blank" rel="noopener noreferrer" class="fb-author-link">{author}</a></span>\n'
            html += f'        <span class="fb-post-date"><a href="{link}" target="_blank" rel="noopener noreferrer">{formatted_date}</a></span>\n'
            html += '      </div>\n'
            html += '    </div>\n'
            
            if message:
                safe_msg = message.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                html += f'    <div class="fb-post-content">{safe_msg}</div>\n'
            
            # Robust Attachment & Shared Post Media Extraction
            attachments = post.get('attachments', {}).get('data', [])
            media_items = []
            
            for attachment in attachments:
                # Check for subattachments (albums/multi-photo posts)
                subattachments = attachment.get('subattachments', {}).get('data', [])
                if subattachments:
                    for sub in subattachments:
                        media = sub.get('media', {})
                        item = parse_media_item(media)
                        if item:
                            media_items.append(item)
                else:
                    # Check main attachment media or shared link media
                    media = attachment.get('media', {})
                    item = parse_media_item(media)
                    if item:
                        media_items.append(item)
                    
                    # Target shares that embed external image previews inside target structures
                    target = attachment.get('target', {})
                    if 'media' in target:
                        target_item = parse_media_item(target.get('media', {}))
                        if target_item:
                            media_items.append(target_item)

            if media_items:
                safe_cap = f"{author} - {formatted_date}"
                html += '    <div class="fb-carousel">\n'
                html += '      <div class="fb-carousel-inner">\n'
                
                for i, item in enumerate(media_items):
                    html += '        <div class="fb-carousel-item">\n'
                    html += f'          <div class="fb-post-media fb-media-trigger" data-type="{item["type"]}" data-src="{item["src"]}" data-caption="{safe_cap}">\n'
                    html += f'            <img src="{item["thumb"]}" alt="Facebook Media {i+1}">\n'
                    if item["type"] == 'video':
                        html += '            <div class="video-play-icon"><i class="fa-solid fa-play"></i></div>\n'
                    html += '          </div>\n'
                    html += '        </div>\n'
                    
                html += '      </div>\n'
                
                if len(media_items) > 1:
                    html += '      <div class="fb-carousel-indicators">\n'
                    for i in range(len(media_items)):
                        active_class = 'active' if i == 0 else ''
                        html += f'        <span class="fb-dot {active_class}"></span>\n'
                    html += '      </div>\n'
                    
                html += '    </div>\n'
                        
            html += '  </div>\n'
        html += '</div>\n'
        
        return html

    except Exception as e:
        print(f"Error fetching Facebook feed: {e}")
        return "<p><em>Facebook feed is currently unavailable (Error fetching data).</em></p>"

def parse_media_item(media):
    if not media:
        return None
    
    if 'source' in media:
        return {
            'type': 'video',
            'src': media['source'],
            'thumb': media.get('image', {}).get('src', '')
        }
    elif 'image' in media:
        return {
            'type': 'image',
            'src': media['image']['src'],
            'thumb': media['image']['src']
        }
    return None

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

        if '[INSERT_FB_FEED]' in content:
            fb_html = fetch_facebook_feed()
            content = content.replace('[INSERT_FB_FEED]', fb_html)

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
