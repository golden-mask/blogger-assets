import os
import requests
import json
import html2text
import yaml
from datetime import datetime
import re # Add this import for regular expressions

# --- Configuration ---
BLOGGER_FEED_URL = 'https://techbaytk.blogspot.com/feeds/posts/default?alt=json-in-script&max-results=500'

# Set OUTPUT_DIR to the actual path of your _posts folder inside your Git repository.
# Example: If your script is in the root of golden-mask.github.io, you can use:
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

# --- NEW HELPER FUNCTION FOR SLUGIFICATION ---
def create_slug(text, max_length=60):
    """
    Generates a filename-safe slug from a given text.
    Allows alphanumeric, spaces, hyphens, and underscores.
    Replaces spaces/problematic chars with hyphens.
    """
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Replace non-alphanumeric characters (except spaces, hyphens, underscores) with empty string
    # This keeps letters, numbers, spaces, hyphens, and underscores.
    # If you want to allow more characters, modify this regex.
    # For example, to allow periods, add \. to the character set: r'[^\w\s-.]'
    text = re.sub(r'[^\w\s-]', '', text) # \w includes alphanumeric and underscore

    # 3. Replace spaces with hyphens
    text = text.replace(' ', '-')
    
    # 4. Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # 5. Strip leading/trailing hyphens
    text = text.strip('-')

    # 6. Truncate to max_length if specified, to avoid extremely long filenames
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0] # Cut at last hyphen before max_length
        if not text: # Fallback if truncation makes it empty
            text = text[:max_length]
    
    # Ensure it's not empty, fallback to a timestamp slug
    if not text:
        text = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return text

# --- REST OF THE SCRIPT (Mostly unchanged) ---

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

            post['content'] = entry.get('content', {}).get('$t', '')

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
    title = post.get('title', 'No Title') # Keep original title for slugging

    # Use the published date for the filename and YAML front matter date
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

    html_content = post.get('content', '')
    markdown_content = h.handle(html_content)

    front_matter = {
        'title': title, # Use original title here for display
        'date': post_date_yaml,
        'author': post.get('author', 'Unknown'),
        'tags': [tag.lower() for tag in post.get('labels', []) if tag],
        'url': post.get('url')
    }
    
    # !!! USE THE NEW create_slug FUNCTION HERE !!!
    slug = create_slug(title) 

    filename = f"{post_date_filename}-{slug}.md" # Filename is now just the cleaned title

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
    main()
