import os
import requests
import json
import html2text
import yaml
from datetime import datetime
import re
from bs4 import BeautifulSoup # NEW: Import BeautifulSoup for HTML parsing

# --- Configuration ---
BLOGGER_FEED_URL = 'https://techbaytk.blogspot.com/feeds/posts/default?alt=json-in-script&max-results=500'
OUTPUT_DIR = '_posts' 

# Initialize html2text for HTML to Markdown conversion
h = html2text.HTML2Text()
h.body_width = 0 
h.ignore_images = False 
h.bypass_tables = False 
h.ignore_links = False 
h.images_as_html = True 
h.links_each_on_own_line = False 
h.strong_mark = '**' 
h.emphasis_mark = '*' 

# --- NEW HELPER FUNCTION TO EXTRACT FIRST IMAGE URL ---
def extract_first_image_url(html_content):
    """
    Parses HTML content to find the source URL of the first <img> tag.
    Returns a placeholder image URL if no image is found.
    """
    if not html_content:
        return 'https://placehold.co/400x250/e0e0e0/333333?text=No+Image'

    soup = BeautifulSoup(html_content, 'html.parser')
    first_img = soup.find('img')
    if first_img and first_img.get('src'):
        return first_img['src']
    
    return 'https://placehold.co/400x250/e0e0e0/333333?text=No+Image' # Placeholder if no image

# --- NEW HELPER FUNCTION FOR SLUGIFICATION ---
def create_slug(text, max_length=60):
    """
    Generates a filename-safe slug from a given text.
    Allows alphanumeric, spaces, hyphens, and underscores.
    Replaces spaces/problematic chars with hyphens.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = text.replace(' ', '-')
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')

    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]
        if not text:
            text = text[:max_length]
    
    if not text:
        text = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return text

# --- REST OF THE SCRIPT ---

def fetch_posts_from_feed(feed_url):
    """Fetches posts from the Blogger Atom feed as JSON."""
    posts_data = []
    print(f"Fetching posts from: {feed_url}")
    try:
        response = requests.get(feed_url)
        response.raise_for_status()
        
        content = response.text
        start_index = content.find('(')
        end_index = content.rfind(')')
        if start_index == -1 or end_index == -1:
            raise ValueError("Could not find JSON data wrapper in response.")
        
        json_string = content[start_index + 1 : end_index]
        feed_json = json.loads(json_string)

        entries = feed_json.get('feed', {}).get('entry', [])
        
        for entry in entries:
            post = {}
            post['title'] = entry.get('title', {}).get('$t', 'No Title')
            
            post['published'] = entry.get('published', {}).get('$t')
            post['updated'] = entry.get('updated', {}).get('$t')

            post['content'] = entry.get('content', {}).get('$t', '') # Keep full HTML content here

            for link in entry.get('link', []):
                if link.get('rel') == 'alternate':
                    post['url'] = link.get('href')
                    break
            else:
                post['url'] = None

            post['author'] = entry.get('author', [{}])[0].get('name', {}).get('$t', 'Unknown')
            
            post['labels'] = [category.get('term') for category in entry.get('category', []) if category.get('scheme') == 'http://www.blogger.com/atom/ns#']
            
            posts_data.append(post)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON feed: {e}")
        print(f"Response content snippet: {content[:500]}...")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
        
    print(f"Successfully fetched {len(posts_data)} posts.")
    return posts_data

def convert_post_to_markdown(post):
    """Converts a Blogger post data to Markdown with YAML front matter."""
    title = post.get('title', 'No Title')

    published_date_str = post.get('published')
    if published_date_str:
        try:
            published_dt = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
            post_date_filename = published_dt.strftime('%Y-%m-%d')
            post_date_yaml = published_dt.isoformat()
        except ValueError:
            print(f"Warning: Could not parse published date '{published_date_str}' for post '{title}'. Using current date.")
            now = datetime.now()
            post_date_filename = now.strftime('%Y-%m-%d')
            post_date_yaml = now.isoformat()
    else:
        now = datetime.now()
        post_date_filename = now.strftime('%Y-%m-%d')
        post_date_yaml = now.isoformat()

    # Extract featured image URL
    featured_image_url = extract_first_image_url(post.get('content', ''))

    html_content = post.get('content', '')
    # Use only a part of the content for excerpt if it's not explicitly defined by <!-- more -->
    # For full control, ensure you define <!-- more --> in your Blogger posts.
    # Otherwise, Liquid's post.excerpt will grab the first paragraph.
    markdown_content = h.handle(html_content)


    front_matter = {
        'layout': 'post', # Ensure this is 'post' for your post layout
        'title': title,
        'date': post_date_yaml,
        'author': post.get('author', 'Unknown'),
        'tags': [tag.lower() for tag in post.get('labels', []) if tag],
        'url': post.get('url'),
        'featured_image': featured_image_url # NEW: Add featured image to front matter
    }
    
    slug = create_slug(title) 

    # Keep Jekyll's required date prefix for filenames
    filename = f"{post_date_filename}-{slug}.md" 

    full_content = f"---\n{yaml.safe_dump(front_matter, allow_unicode=True, default_flow_style=False)}---\n\n{markdown_content}"
    return filename, full_content

def save_markdown_file(filename, content):
    """Saves the markdown content to the specified file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {file_path}")

def main():
    print("Starting Blogger to Markdown sync...")
    if not os.path.isabs(OUTPUT_DIR) and not os.path.exists(OUTPUT_DIR):
        print(f"Warning: Relative OUTPUT_DIR '{OUTPUT_DIR}' does not exist. It will be created.")
    elif os.path.isabs(OUTPUT_DIR) and not os.path.exists(OUTPUT_DIR):
        print(f"Error: Absolute OUTPUT_DIR '{OUTPUT_DIR}' does not exist. Please check the path and create it if necessary.")
        return

    posts = fetch_posts_from_feed(BLOGGER_FEED_URL)

    if not posts:
        print("No posts found or an error occurred during fetching the feed.")
        return

    for post in posts:
        filename, content = convert_post_to_markdown(post)
        save_markdown_file(filename, content)
    print("Blogger posts synced successfully to Markdown!")

if __name__ == '__main__':
    # Make sure to pip install beautifulsoup4
    # pip install beautifulsoup4
    main()
