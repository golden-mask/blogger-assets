---
layout: default
title: Welcome to techbaytk Blog
---

<section class="carousel-section">
  <h2>Latest Posts</h2>
  <div class="carousel-container">
    <button class="carousel-nav-btn prev">&lt;</button>
    <div class="carousel-track-container">
      <div class="carousel-track" id="post-carousel-track">
        <!-- Post cards will be dynamically loaded here by JavaScript -->
        <div class="loading-cards">Loading posts...</div>
      </div>
    </div>
    <button class="carousel-nav-btn next">&gt;</button>
  </div>
  <div class="show-all-posts">
    <a href="{{ '/archive' | relative_url }}" class="button">Show All Posts</a>
  </div>
</section>

<!-- The original post list loop from index.md is removed as posts are now in carousel -->
<!-- If you want a full list of all posts, you'd typically create a dedicated /archive.md or /posts.md page -->
<!-- For simplicity, the "Show All Posts" button points to '/archive', assuming you might create that later. -->