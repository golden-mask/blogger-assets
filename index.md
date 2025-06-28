---
layout: default
title: Welcome to techbaytk Blog
---

<section class="posts-list-section">
  <h2>Latest Posts</h2>
  <div class="posts-list-container">
    {% assign latest_posts = site.posts | sort: "date" | reverse | limit: 5 %} {# Get latest 5 posts #}
    {% if latest_posts.size > 0 %}
      {% for post in latest_posts %}
        <div class="post-item-card">
          <div class="post-item-header">
            <h3 class="post-item-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
            <div class="post-item-date-bookmark">
            <div class="year">
              {{ post.date | date: "%Y" }}
            </div>
            <div class="day">
              {{ post.date | date: "%d" }}
            </div>
            <div class="month">
              {{ post.date | date: "%b" }}
            </div>
          </div>
         </div> 
          <div class="post-item-body">
            <div class="post-item-image" style="background-image: url('{{ post.featured_image | default: 'https://placehold.co/400x250/e0e0e0/333333?text=No+Image' }}');"></div>
            <p class="post-item-description">{{ post.excerpt | strip_html | strip_newlines | truncatewords: 30 }}</p> 
          </div>
          <div class="post-item-footer">
            <div class="post-item-tags">
              {% if post.tags.size > 0 %}
                {% for tag in post.tags limit: 3 %} 
                  <span class="post-item-tag-item">{{ tag }}</span>
                {% endfor %}
              {% else %}
                <span class="post-item-tag-item">No Tags</span>
              {% endif %}
            </div>
            <a href="{{ post.url | relative_url }}" class="read-more-button">Read More &rarr;</a>
          </div>
        </div>
      {% endfor %}
    {% else %}
      <p style="text-align: center; width: 100%;">No posts found. Check `_posts` folder and Jekyll build.</p>
    {% endif %}
  </div>
  <div class="show-all-posts">
    <a href="{{ '/archive' | relative_url }}" class="button">Show All Posts</a>
  </div>
</section>
