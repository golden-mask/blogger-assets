Alright, let's craft the perfect README.md file for your golden-mask.github.io repository. This README will be a comprehensive guide for anyone (including you!) visiting your repository, explaining its purpose, how it works, how to set it up, and how to maintain it.

🌟 Golden Mask Blog - Powered by Blogger, Jekyll, and GitHub Pages
Welcome to the Golden Mask Blog repository! This repository hosts the static blog published at golden-mask.github.io. Content is dynamically pulled from an original Blogger blog, converted to Markdown, and then built with Jekyll and deployed via GitHub Pages.

🎯 Project Purpose
The primary goals of this project are:

Automated Sync: Automatically pull blog posts from an existing Blogger blog into this GitHub repository.

Static Site Generation: Utilize Jekyll to transform Markdown posts into a fast and efficient static website.

Free & Reliable Hosting: Leverage GitHub Pages for cost-effective and robust blog hosting.

Local Content Management: Enable seamless editing and management of blog posts using Obsidian on your local machine via symbolic links.

✨ Features
Blogger Post Ingestion: A custom Python script fetches all blog posts from a specified Blogger Atom/RSS feed URL (no API key required).

Markdown Conversion: HTML content from Blogger posts is converted into clean, Jekyll-friendly Markdown format.

Organized Filenames: Markdown files are named using a clean, title-based slug prefixed with the post's publish date, adhering to Jekyll's requirements.

Jekyll-Powered: The site is built with Jekyll, offering a flexible templating system for layout and design.

Modern CSS Theme: Includes a custom assets/main.css file to provide a clean, modern aesthetic for the blog.

Obsidian Sync: Setup instructions for symbolic linking enable your Obsidian vault to directly access and manage the blog's Markdown files.

GitHub Pages Deployment: Automatic deployment of the static site via GitHub Pages on every push to the main branch.

🚀 Getting Started (For Developers)
Follow these steps to set up and manage the project on your local machine.

Prerequisites
Ensure you have the following installed:

Git: For version control and GitHub interaction.

Python 3.x: To run the synchronization script.

Ruby: Required for Jekyll (essential for GitHub Pages builds, also for local Jekyll preview).

Bundler (Ruby gem): A Ruby gem dependency manager. Install with: gem install bundler

Jekyll (Ruby gem): The static site generator. Install with: gem install jekyll

Obsidian: (Optional, but recommended for content management).

1. Clone the Repository
Clone this repository to your local machine:

```Bash

git clone https://github.com/golden-mask/golden-mask.github.io.git
cd golden-mask.github.io
```
2. Configure Jekyll Structure
The repository is already set up with a minimal Jekyll structure:

_config.yml: Main Jekyll configuration settings.

_layouts/: HTML templates for your site (e.g., default.html, post.html).

assets/: For static files like main.css.

_posts/: This is where your Markdown blog posts reside.

3. Configure the Blogger Sync Script (blogger_to_markdown_sync.py)
Open the blogger_to_markdown_sync.py file and verify the following:

BLOGGER_FEED_URL: This should be set to your Blogger feed URL. It's likely configured as:

Python

BLOGGER_FEED_URL = 'https://techbaytk.blogspot.com/feeds/posts/default?alt=json-in-script&max-results=500'
This URL does not require a Blogger API key.

OUTPUT_DIR: Ensure this points to your _posts folder within the repository. If the script is in the repository's root, it should be:

Python

OUTPUT_DIR = '_posts'
If the script is located elsewhere, you'll need to provide the full absolute path to your _posts folder.

4. Install Python Dependencies
In your terminal, navigate to your repository's root directory and run:

Bash

pip install requests html2text PyYAML
5. Set up Obsidian Symbolic Link (Optional)
To enable Obsidian to directly see and manage your posts from the _posts folder without duplicating files, create a symbolic link. You must run your Command Prompt or PowerShell as an "Administrator" on Windows for this step.

On Windows:

DOS

mklink /D "C:\Path\To\Your\ObsidianVault\Blog Posts" "C:\Path\To\Your\golden-mask.github.io\_posts"
(Replace paths with your actual directories. Ensure the target folder in your Obsidian Vault, e.g., Blog Posts, does not exist before creating the link.)

On macOS/Linux:

Bash

ln -s "/Path/To/Your/golden-mask.github.io/_posts" "/Path/To/Your/ObsidianVault/Blog Posts"
(Replace paths with your actual directories. Ensure the target folder in your Obsidian Vault, e.g., Blog Posts, does not exist before creating the link.)

💡 How to Use
Syncing Blogger Posts to Markdown
Open your terminal in the golden-mask.github.io repository directory.

Run the synchronization script:

Bash

python blogger_to_markdown_sync.py
This script will fetch the latest posts from Blogger and save/update them in your _posts/ folder. If you've set up the symbolic link, these posts will automatically appear in Obsidian.

Editing and Creating Posts
You can now open and edit any existing post in the _posts/ folder using your preferred text editor, or directly within Obsidian (if you set up the symbolic link).

To create a new post, create a new Markdown file in the _posts/ folder following the format: YYYY-MM-DD-your-post-title-slug.md and ensure it includes YAML front matter at the top.

Previewing Your Site Locally (Optional)
If you wish to preview your site using Jekyll before publishing:

Ensure you have Ruby, Jekyll, and Bundler installed.

In your repository's root directory, run:

Bash

bundle exec jekyll serve
Open your web browser and navigate to the address Jekyll provides (typically http://127.0.0.1:4000).

Publishing to GitHub Pages
After syncing posts or making any local edits:

In your terminal, ensure you're in the repository's root directory.

Add your changes, commit them, and push:

Bash

git add .
git commit -m "Sync latest Blogger posts and/or local edits"
git push origin main
GitHub Pages will automatically build and publish your site to golden-mask.github.io within a few minutes.

🎨 Customization
CSS Styling: Modify the assets/main.css file to entirely change the look and feel of your blog.

Jekyll Layouts: Adjust the .html files in the _layouts/ folder to alter the structure and layout of your pages and posts.

Jekyll Settings: Change _config.yml to configure global site settings, such as the site title, description, and plugins.

Python Slug Logic: If you want to fine-tune how your filenames (slugs) are generated, you can modify the create_slug function within blogger_to_markdown_sync.py.

⚠️ Troubleshooting
Posts Not Appearing on GitHub Pages:

Check Filenames: The most common reason. Ensure your Markdown files in _posts/ strictly follow the YYYY-MM-DD-your-post-title-slug.md format.

Check GitHub Actions: Go to the "Actions" tab in your GitHub repository and verify that the "Pages build and deployment" workflow (or similar) is running successfully without errors.

Clear Browser Cache: Sometimes, an old browser cache can prevent updates from showing immediately.

mklink or ln -s command fails:

On Windows, ensure you are running Command Prompt or PowerShell as an Administrator.

Double-check that the paths you entered are absolutely correct.

Make sure the target folder (in your Obsidian Vault) does not exist before attempting to create the symbolic link.

🤝 Contributing
This is a personal repository, but suggestions and improvements are always welcome! Feel free to open an "Issue" or a "Pull Request" if you have ideas for the script, CSS, or Jekyll setup.

📄 License
This project is licensed under the MIT License.

