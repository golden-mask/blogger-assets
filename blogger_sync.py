import os
import json
from googleapiclient.discovery import build
import html2text
import yaml # For creating YAML front matter

# --- Configuration ---
BLOGGER_API_KEY =os.environ.get('BLOGGER_API_KEY') # Get from GitHub Secrets

# !!! IMPORTANT: Replace 'YOUR_BLOG_ID' with your actual Blogger Blog ID !!!
# You can find your Blog ID in your Blogger dashboard URL.
# For example, if your blog is at 'https://www.blogger.com/blog/posts/1234567890', then 1234567890 is your BLOG_ID.
BLOG_ID = '8740371480799149020' 

# The directory where Markdown files will be saved for Jekyll
# Jekyll looks for posts in the _posts/ directory
OUTPUT_DIR = '_posts' 

# Initialize html2text for HTML to Markdown conversion
# Added customization for img, a tags for better Jekyll compatibility
h = html2text.HTML2Text()
h.body_width = 0 
h.ignore_images = False 
h.bypass_tables = False 
h.ignore_links = False 
h.images_as_html = True # Keep images as <img> tags for better control in Jekyll layouts
h.links_each_on_own_line = False # Avoid extra newlines for links
h.strong_mark = '**' # Use ** for bold
h.emphasis_mark = '*' # Use * for italic

def get_blogger_service():
    """Builds and returns the Blogger API service."""
    return build('blogger', 'v3', developerKey=BLOGGER_API_KEY)

def fetch_all_posts(service, blog_id):
    """Fetches all published posts from Blogger."""
    posts = []
    page_token = None
    while True:
        try:
            results = service.posts().list(
                blogId=blog_id,
                maxResults=500, # Max results per page
                fetchBodies=True, # Fetch full content
                fetchImages=True, # Fetch image data
                status='LIVE', # Only published posts
                pageToken=page_token
            ).execute()

            posts.extend(results.get('items', []))
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            print(f"Error fetching posts: {e}")
            break # Exit loop on error
    return posts

def convert_post_to_markdown(post):
    """Converts a Blogger post (HTML) to Markdown with Jekyll-compatible front matter."""
    title = post.get('title', 'No Title').replace(':', ' -') # Avoid colon in title for Jekyll
    published_at = post.get('published')
    
    # Format date for Jekyll filename: YYYY-MM-DD
    # Example filename: 2023-10-27-my-post-title.md
    post_date_iso = published_at # Keep full ISO format for Jekyll 'date' in front matter
    post_date_filename = published_at[:10] # YYYY-MM-DD for filename

    # Convert HTML content to Markdown
    html_content = post.get('content', '')
    markdown_content = h.handle(html_content)

    # Prepare YAML Front Matter
    front_matter = {
        'layout': 'post', # Use the 'post.html' layout we created
        'title': title,
        'date': post_date_iso, # Full date for Jekyll
        'author': post.get('author', {}).get('displayName', 'Unknown'),
        'tags': [tag.lower() for tag in post.get('labels', []) if tag], # Convert labels to tags, filter empty
        'permalink': post.get('url').split('.com')[1] if post.get('url') else None # Create permalink relative to domain
    }
    
    # Clean permalink for Jekyll: ensure it starts with / and remove query params
    if front_matter['permalink']:
        front_matter['permalink'] = front_matter['permalink'].split('?')[0] # Remove query params
        if not front_matter['permalink'].startswith('/'):
            front_matter['permalink'] = '/' + front_matter['permalink']

    # Generate filename slug
    # Remove characters that can cause issues in file names
    slug = ''.join(c for c in title if c.isalnum() or c in [' ', '-']).lower().replace(' ', '-')
    slug = slug.encode('ascii', 'ignore').decode('ascii') # Remove non-ASCII
    slug = slug.replace('--', '-').strip('-') # Remove double hyphens and leading/trailing hyphens

    filename = f"{post_date_filename}-{slug}.md"
    if not slug: # Fallback if slug becomes empty
        filename = f"{post_date_filename}-post-{post.get('id')}.md"


    # Combine front matter and markdown content
    # yaml.safe_dump is generally safer for untrusted input
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
    if not BLOGGER_API_KEY:
        print("Error: BLOGGER_API_KEY environment variable not set.")
        print("Please add it to your GitHub Repository Secrets.")
        return
    
    if BLOG_ID == 'YOUR_BLOG_ID':
        print("Error: BLOG_ID not set. Please replace 'YOUR_BLOG_ID' in the script with your actual Blogger Blog ID.")
        return

    service = get_blogger_service()
    posts = fetch_all_posts(service, BLOG_ID)

    if not posts:
        print("No posts found or an error occurred during fetching.")
        return

    for post in posts:
        filename, content = convert_post_to_markdown(post)
        save_markdown_file(filename, content)
    print("Blogger posts synced successfully!")

if __name__ == '__main__':
    main()