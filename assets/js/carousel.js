document.addEventListener('DOMContentLoaded', function() {
    const carouselTrack = document.getElementById('post-carousel-track');
    const prevBtn = document.querySelector('.carousel-nav-btn.prev');
    const nextBtn = document.querySelector('.carousel-nav-btn.next');
    let currentIndex = 0;
    let cardsPerView = 1; // Default for mobile
    const cardMargin = 20; // Margin between cards in CSS

    // Function to extract the first image URL from HTML content
    function getFirstImageUrl(htmlString) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlString;
        const img = tempDiv.querySelector('img');
        return img ? img.src : 'https://placehold.co/400x250/cccccc/333333?text=No+Image'; // Placeholder if no image
    }

    // Function to create a single post card element
    function createPostCard(post) {
        const card = document.createElement('div');
        card.classList.add('post-card');

        const imageUrl = getFirstImageUrl(post.content_html);

        // Bookmark date element
        const dateBookmark = document.createElement('div');
        dateBookmark.classList.add('card-date-bookmark');
        dateBookmark.textContent = new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });

        // Tags element
        const tagsContainer = document.createElement('div');
        tagsContainer.classList.add('card-tags');
        if (post.tags && post.tags.length > 0) {
            post.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.classList.add('card-tag-item');
                tagSpan.textContent = tag;
                tagsContainer.appendChild(tagSpan);
            });
        } else {
            tagsContainer.innerHTML = '<span class="card-tag-item">No Tags</span>';
        }

        card.innerHTML = `
            <div class="card-image-bg" style="background-image: url('${imageUrl}');"></div>
            <div class="card-content">
                <h3 class="card-title"><a href="${post.url}">${post.title}</a></h3>
                <p class="card-description">${post.excerpt}</p>
            </div>
        `;
        card.querySelector('.card-content').prepend(dateBookmark); // Add date bookmark to content
        card.querySelector('.card-content').appendChild(tagsContainer); // Add tags to content

        return card;
    }

    // Function to update carousel position
    function updateCarousel() {
        const cardWidth = carouselTrack.children[0].offsetWidth; // Width of one card including margin
        const offset = -(currentIndex * (cardWidth + cardMargin));
        carouselTrack.style.transform = `translateX(${offset}px)`;

        // Disable/enable buttons based on current index
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= carouselTrack.children.length - cardsPerView;
    }

    // Handle navigation clicks
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentIndex < carouselTrack.children.length - cardsPerView) {
            currentIndex++;
            updateCarousel();
        }
    });

    // Responsive adjustments for cards per view
    function setCardsPerView() {
        if (window.innerWidth >= 1024) { // Desktop
            cardsPerView = 3;
        } else if (window.innerWidth >= 768) { // Tablet
            cardsPerView = 2;
        } else { // Mobile
            cardsPerView = 1;
        }
        // Reset index to ensure it's within bounds after resize
        if (currentIndex > carouselTrack.children.length - cardsPerView) {
            currentIndex = carouselTrack.children.length - cardsPerView;
            if (currentIndex < 0) currentIndex = 0; // Prevent negative index if few posts
        }
        updateCarousel(); // Update carousel position after resize
    }

    // Fetch posts data and populate carousel
    fetch('{{ "/carousel_posts.json" | relative_url }}') // Use Jekyll's relative_url filter
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(posts => {
            carouselTrack.innerHTML = ''; // Clear loading message
            if (posts.length === 0) {
                carouselTrack.innerHTML = '<div style="text-align: center; width: 100%;">No posts found.</div>';
                prevBtn.style.display = 'none';
                nextBtn.style.display = 'none';
                return;
            }
            posts.forEach(post => {
                const card = createPostCard(post);
                carouselTrack.appendChild(card);
            });
            setCardsPerView(); // Initial setup
            window.addEventListener('resize', setCardsPerView); // Update on resize
        })
        .catch(error => {
            console.error('Error fetching carousel posts:', error);
            carouselTrack.innerHTML = '<div style="text-align: center; width: 100%;">Failed to load posts.</div>';
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        });
});