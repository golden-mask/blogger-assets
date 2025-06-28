---
layout: default
title: Welcome to techbaytk Blog
---

<section class="latest-posts-grid-section">
  <h2>Latest Posts</h2>
  <div class="posts-grid-container">
    {% assign posts_to_display = site.posts | sort: "date" | reverse | limit: 5 %} {# Get latest 5 posts #}
    {% if posts_to_display.size > 0 %}
      {% for post in posts_to_display %}
        <div class="post-card">
          <div class="card-image-bg" style="background-image: url('{{ post.featured_image | default: 'https://placehold.co/400x250/e0e0e0/333333?text=No+Image' }}');"></div>
          <div class="card-content">
            <div class="card-date-bookmark">
              {{ post.date | date: "%b %d, %Y" }} {# e.g., Jun 28, 2025 #}
            </div>
            <h3 class="card-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
            <p class="card-description">{{ post.excerpt | strip_html | strip_newlines | truncatewords: 25 }}</p> {# Truncate description #}
            <div class="card-tags">
              {% if post.tags.size > 0 %}
                {% for tag in post.tags limit: 3 %} {# Limit tags to 3 for brevity #}
                  <span class="card-tag-item">{{ tag }}</span>
                {% endfor %}
              {% else %}
                <span class="card-tag-item">No Tags</span>
              {% endif %}
            </div>
          </div>
        </div>
      {% endfor %}
    {% else %}
      <p style="text-align: center; width: 100%;">No posts found.</p>
    {% endif %}
  </div>
  <div class="show-all-posts">
    <a href="{{ '/archive' | relative_url }}" class="button">Show All Posts</a>
  </div>
</section>