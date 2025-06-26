import os
import requests
import json
import html2text
import yaml # For creating YAML front matter
from datetime import datetime

# --- Configuration ---
# Your Blogger Feed URL. This fetches posts in JSON format.
# max-results=500 is important to get a large number of posts per request.
BLOGGER_FEED_URL = 'https://techbaytk.blogspot.com/feeds/posts/default?alt=json-in-script&max-results=500'

# The directory where Markdown files will be saved.
# If you are using Obsidian, you might point this to a subfolder in your Obsidian vault.
# Example: If your vault is C:\Users\YourUser\Documents\ObsidianVault, and you want
# posts in a folder named 'Blogger Posts' inside it:
# OUTPUT_DIR = 'C:\\Users\\YourUser\\Documents\\ObsidianVault\\Blogger Posts'
# For a relative path within your project, keep it simple like:
OUTPUT_DIR = 'D:\\Obsidian\\blog post' # This will create a folder in the same directory as your script

# Initialize html2text for HTML to Markdown conversion
h = html2text.HTML2Text()
h.body_width = 0 
h.ignore_images = False 
h.bypass_tables = False 
h.ignore_links = False 
h.images_as_html = True # Keep images as <img> tags for better control
h.links_each_on_own_line = False 
h.strong_mark = '**' 
h.emphasis_mark = '*' 

def fetch_posts_from_feed(feed_url):
    """Fetches posts from the Blogger Atom feed as JSON."""
    posts_data = []
    # Blogger's JSON feed structure usually has a 'feed' object and 'entry' for posts.
    # It also handles pagination differently. For simplicity, we'll fetch the first 500.
    # If you have more than 500 posts, you'll need to implement pagination using 'start-index' parameter.
    
    # Example of pagination:
    # 'https://techbaytk.blogspot.com/feeds/posts/default?alt=json-in-script&max-results=500&start-index=501'
    # For now, let's assume max-results=500 is sufficient or adjust if needed.

    print(f"Fetching posts from: {feed_url}")
    try:
        # Blogger's 'json-in-script' format requires stripping the 'gdata.io.handleScriptLoaded' wrapper
        response = requests.get(feed_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        # Extract JSON from the JavaScript wrapper
        content = response.text
        start_index = content.find('(')
        end_index = content.rfind(')')
        if start_index == -1 or end_index == -1:
            raise ValueError("Could not find JSON data wrapper in response.")
        
        json_string = content[start_index + 1 : end_index]
        feed_json = json.loads(json_string)

        entries = feed_json.get('feed', {}).get('entry', [])
        
        # Process each entry to extract relevant data
        for entry in entries:
            post = {}
            post['title'] = entry.get('title', {}).get('$t', 'No Title')
            
            # The 'published' and 'updated' timestamps
            post['published'] = entry.get('published', {}).get('$t')
            post['updated'] = entry.get('updated', {}).get('$t')

            # The full HTML content
            post['content'] = entry.get('content', {}).get('$t', '')

            # Extract URL from 'link' array
            for link in entry.get('link', []):
                if link.get('rel') == 'alternate': # This is usually the permalink
                    post['url'] = link.get('href')
                    break
            else:
                post['url'] = None # No alternate link found

            # Author name
            post['author'] = entry.get('author', [{}])[0].get('name', {}).get('$t', 'Unknown')
            
            # Labels (tags)
            post['labels'] = [category.get('term') for category in entry.get('category', []) if category.get('scheme') == 'http://www.blogger.com/atom/ns#']
            
            posts_data.append(post)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON feed: {e}")
        print(f"Response content snippet: {content[:500]}...") # Print first 500 chars of content for debugging
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
        
    print(f"Successfully fetched {len(posts_data)} posts.")
    return posts_data

def convert_post_to_markdown(post):
    """Converts a Blogger post data to Markdown with YAML front matter."""
    title = post.get('title', 'No Title').replace(':', ' -') # Avoid colon in title for Jekyll/Obsidian filename
    
    # Use the published date for the filename and YAML front matter date
    published_date_str = post.get('published')
    if published_date_str:
        # Convert ISO format to datetime object, then format
        try:
            published_dt = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
            post_date_filename = published_dt.strftime('%Y-%m-%d') # YYYY-MM-DD for filename
            post_date_yaml = published_dt.isoformat() # ISO format for YAML date
        except ValueError:
            print(f"Warning: Could not parse published date '{published_date_str}' for post '{title}'. Using current date.")
            now = datetime.now()
            post_date_filename = now.strftime('%Y-%m-%d')
            post_date_yaml = now.isoformat()
    else:
        now = datetime.now()
        post_date_filename = now.strftime('%Y-%m-%d')
        post_date_yaml = now.isoformat()

    # Convert HTML content to Markdown
    html_content = post.get('content', '')
    markdown_content = h.handle(html_content)

    # Prepare YAML Front Matter
    front_matter = {
        'title': title,
        'date': post_date_yaml,
        'author': post.get('author', 'Unknown'),
        'tags': [tag.lower() for tag in post.get('labels', []) if tag],
        'url': post.get('url') # Keep original Blogger URL for reference
    }
    
    # Generate filename (YYYY-MM-DD-title-slug.md)
    # Simple slugification for filename
    slug = ''.join(c for c in title if c.isalnum() or c in [' ', '-']).lower().replace(' ', '-')
    slug = slug.encode('ascii', 'ignore').decode('ascii') # Remove non-ASCII characters
    slug = slug.replace('--', '-').strip('-') # Remove double hyphens and leading/trailing hyphens

    # Ensure slug is not empty
    if not slug:
        slug = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}" # Fallback slug if title results in empty

    filename = f"{post_date_filename}-{slug}.md"

    # Combine front matter and markdown content
    full_content = f"---\n{yaml.safe_dump(front_matter, allow_unicode=True, default_flow_style=False)}---\n\n{markdown_content}"
    return filename, full_content

def save_markdown_file(filename, content):
    """Saves the markdown content to the specified file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Create output directory if it doesn't exist
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {file_path}")

def main():
    print("Starting Blogger to Markdown sync...")
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
