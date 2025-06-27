---
layout: default
title: All Posts
permalink: /archive/
---
<h1>All Posts</h1>
{% for post in site.posts %}
  <div class="post-preview">
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <p><time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %d, %Y" }}</time></p>
    {{ post.excerpt }}
    <p><a href="{{ post.url | relative_url }}">Read more &rarr;</a></p>
  </div>
{% endfor %}