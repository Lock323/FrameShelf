document.body.addEventListener('htmx:afterOnLoad', function() {
    setupScrollLeftHandlers();
    setupScrollRightHandlers();
});

function setupScrollLeftHandlers() {
    const buttonToContentMapRight = {
        'scroll_left_watchlist': 'watchlist_content',
        'scroll_left_watched_movies': 'watched_movies_content',
        'scroll_left_watched_tv': 'watched_tv_content'
    };

    document.addEventListener('click', function(event) {
        const targetButton = event.target.closest('[id]');
        if (targetButton && targetButton.id in buttonToContentMapRight) {
            const contentId = buttonToContentMapRight[targetButton.id];
            const contentDiv = document.getElementById(contentId);

            if (contentDiv) {
                const scrollDistance = 1050;
                const currentScroll = contentDiv.scrollLeft;
                const newScroll = currentScroll - scrollDistance;
                const minScroll = 0;

                contentDiv.scrollLeft = Math.max(newScroll, minScroll);

                console.log('Скролл:', {
                    buttonId: targetButton.id,
                    contentId: contentId,
                    currentScroll: currentScroll,
                    newScroll: newScroll
                });
            }
        }
    });
}


setupScrollLeftHandlers();


function setupScrollRightHandlers() {
    const buttonToContentMapLeft = {
        'scroll_right_watchlist': 'watchlist_content',
        'scroll_right_watched_movies': 'watched_movies_content',
        'scroll_right_watched_tv': 'watched_tv_content'
    };

    document.addEventListener('click', function(event) {
        const targetButton = event.target.closest('[id]');

        if (targetButton && targetButton.id in buttonToContentMapLeft) {
            const contentId = buttonToContentMapLeft[targetButton.id];
            const contentDiv = document.getElementById(contentId);

            if (contentDiv) {
                const scrollDistance = 1050;
                const currentScroll = contentDiv.scrollLeft;
                const newScroll = currentScroll + scrollDistance;
                const maxScroll = contentDiv.scrollWidth - contentDiv.clientWidth;

                contentDiv.scrollLeft = Math.min(newScroll, maxScroll);

                console.log('Скролл вправо:', {
                    buttonId: targetButton.id,
                    contentId: contentId,
                    currentScroll: currentScroll,
                    newScroll: newScroll,
                    maxScroll: maxScroll
                });
            }
        }
    });
    }


setupScrollRightHandlers();