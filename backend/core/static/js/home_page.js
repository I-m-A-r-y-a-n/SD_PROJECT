// ── ELEMENTS ──
const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");
const sidebarClose = document.getElementById("sidebarClose");
const overlay = document.getElementById("overlay");
const mainContent = document.getElementById("mainContent");
const askBtn = document.getElementById("askBtn");
const searchInput = document.getElementById("searchInput");
const resultsArea = document.getElementById("resultsArea");
const hero = document.getElementById("hero");
const searchWrapper = document.getElementById("searchWrapper");
const suggestions = document.getElementById("suggestions");
const newChatBtn = document.getElementById("newChatBtn");
const historyList = document.getElementById("historyList");

let hasSearched = false;

// ── INITIAL HERO MODE ──
mainContent.classList.add("hero-mode");

// ── LOAD RECOMMENDATIONS (only shows in hero mode) ──
function loadRecommendations() {
    // Only load recommendations if we haven't searched yet
    if (hasSearched) return;
    
    fetch("/api/recommendations/")
        .then(res => res.json())
        .then(data => {
            const suggestionsDiv = document.getElementById("suggestions");
            suggestionsDiv.innerHTML = "";
            
            if (data.recommendations && data.recommendations.length > 0) {
                data.recommendations.forEach(rec => {
                    const chip = document.createElement("div");
                    chip.classList.add("chip");
                    chip.innerText = rec.query;
                    chip.addEventListener("click", () => {
                        searchInput.value = rec.query;
                        sendSearch();
                    });
                    suggestionsDiv.appendChild(chip);
                });
            } else {
                // Default suggestions if no history
                const defaultQueries = ["Python tutorial", "SQL queries", "DSA problems", "React interview", "System design", "AI tools"];
                defaultQueries.forEach(query => {
                    const chip = document.createElement("div");
                    chip.classList.add("chip");
                    chip.innerText = query;
                    chip.addEventListener("click", () => {
                        searchInput.value = query;
                        sendSearch();
                    });
                    suggestionsDiv.appendChild(chip);
                });
            }
        })
        .catch(() => {
            const suggestionsDiv = document.getElementById("suggestions");
            suggestionsDiv.innerHTML = "";
            const defaultQueries = ["Python tutorial", "SQL queries", "DSA problems", "React interview"];
            defaultQueries.forEach(query => {
                const chip = document.createElement("div");
                chip.classList.add("chip");
                chip.innerText = query;
                chip.addEventListener("click", () => {
                    searchInput.value = query;
                    sendSearch();
                });
                suggestionsDiv.appendChild(chip);
            });
        });
}

// ── SIDEBAR ──
function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("show");
    if (window.innerWidth > 600) mainContent.classList.add("shifted");
    loadHistorySidebar();
}

function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("show");
    mainContent.classList.remove("shifted");
}

menuBtn.onclick = openSidebar;
sidebarClose.onclick = closeSidebar;
overlay.onclick = closeSidebar;

// ── NEW CHAT ──
newChatBtn.onclick = () => {
    hasSearched = false;
    resultsArea.innerHTML = "";
    searchInput.value = "";
    hero.classList.remove("hidden");
    mainContent.classList.add("hero-mode");
    searchWrapper.classList.remove("bottom-mode");
    suggestions.style.display = "flex";
    closeSidebar();
    document.querySelectorAll(".history-entry").forEach(e => e.classList.remove("active"));
    loadRecommendations();
};

// ── SIDEBAR ITEMS (Redirect to separate pages) ──
document.querySelectorAll(".sidebar-item").forEach(item => {
    const action = item.dataset.action;
    item.addEventListener("click", function () {
        if (action === "logout") {
            fetch("/api/logout/").then(() => { window.location.href = "/login/"; });
        } else if (action === "bookmarks") {
            window.location.href = "/bookmarks/";
        } else if (action === "profile") {
            window.location.href = "/profile/";
        } else if (action === "feedback") {
            window.location.href = "/feedback/";
        } else {
            alert(action.charAt(0).toUpperCase() + action.slice(1) + " — Coming Soon!");
        }
    });
});

// ── SEARCH TRIGGERS ──
askBtn.addEventListener("click", sendSearch);
searchInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendSearch();
});

// ── SWITCH TO BOTTOM MODE (with animation) ──
function switchToBottomMode() {
    if (hasSearched) return;
    hasSearched = true;
    // smooth: fade hero, move search to bottom
    hero.style.transition = "opacity 0.3s ease";
    hero.style.opacity = "0";
    setTimeout(() => {
        hero.classList.add("hidden");
        hero.style.opacity = "";
        mainContent.classList.remove("hero-mode");
        searchWrapper.classList.add("bottom-mode");
        suggestions.style.display = "none";  // Hide recommendations after search
    }, 300);
}

// ── LOADING STATE ──
function setLoading(on) {
    if (on) {
        askBtn.classList.add("loading");
        searchInput.disabled = true;
        document.body.style.cursor = "wait";
    } else {
        askBtn.classList.remove("loading");
        searchInput.disabled = false;
        document.body.style.cursor = "";
    }
}

// ── SKELETON ──
function showSkeleton() {
    const skeleton = document.createElement("div");
    skeleton.classList.add("skeleton-block");
    skeleton.id = "skeletonLoader";
    skeleton.innerHTML = `
        <div class="skeleton user"></div>
        <div class="skeleton video-row"></div>
        <div class="skeleton ai"></div>
        <div class="skeleton link"></div>
        <div class="skeleton link"></div>
    `;
    resultsArea.insertBefore(skeleton, resultsArea.firstChild);
}

function removeSkeleton() {
    const s = document.getElementById("skeletonLoader");
    if (s) s.remove();
}

// ── RENDER MARKDOWN ──
function renderMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^### (.+)$/gm, '<h4 style="margin:0.5rem 0 0.2rem;font-size:0.95rem">$1</h4>')
        .replace(/^## (.+)$/gm, '<h3 style="margin:0.6rem 0 0.3rem">$1</h3>')
        .replace(/^# (.+)$/gm, '<h2 style="margin:0.7rem 0 0.3rem">$1</h2>')
        .replace(/^- (.+)$/gm, '<li style="margin-left:1.2rem;margin-bottom:0.2rem">$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/```([\s\S]*?)```/g, '<pre style="background:#f3f4f6;padding:0.8rem;border-radius:8px;overflow-x:auto;font-size:0.82rem;margin:0.5rem 0"><code>$1</code></pre>');
}

// ── MAIN SEARCH ──
function sendSearch() {
    const query = searchInput.value.trim();
    if (query === "") return;

    switchToBottomMode();
    setLoading(true);
    setTimeout(showSkeleton, 200);
    searchInput.value = "";

    fetch("/api/search/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
        removeSkeleton();
        setLoading(false);
        renderResult(data);
        resultsArea.scrollTop = 0;
        // Don't reload recommendations after search
    })
    .catch(() => {
        removeSkeleton();
        setLoading(false);
        alert("Something went wrong. Please try again.");
    });
}

// ── RENDER RESULT ──
function renderResult(data) {
    const block = document.createElement("div");
    block.classList.add("result-block");

    const userMsg = document.createElement("div");
    userMsg.classList.add("user-message");
    userMsg.innerText = data.query;
    block.appendChild(userMsg);

    // VIDEOS - Modern layout (ONLY THIS ONE)
    if (data.videos && data.videos.length > 0) {
        const videoSection = document.createElement("div");
        videoSection.classList.add("video-section");
        
        const sectionHeader = document.createElement("div");
        sectionHeader.classList.add("section-header");
        sectionHeader.innerHTML = `
            <span class="section-header-icon">📹</span>
            <span class="section-header-title">Recommended Videos</span>
        `;
        videoSection.appendChild(sectionHeader);
        
        const videoContainer = document.createElement("div");
        videoContainer.classList.add("video-container");

        data.videos.forEach(video => {
            const videoCard = document.createElement("a");
            videoCard.href = "https://www.youtube.com/watch?v=" + video.video_id;
            videoCard.target = "_blank";
            videoCard.classList.add("video-card");
            videoCard.innerHTML = `
                <div class="video-thumb-wrapper">
                    <img src="https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg" 
                        alt="${video.title}" class="video-thumb">
                    <div class="video-play-btn">
                        <svg viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z"/>
                        </svg>
                    </div>
                </div>
                <div class="video-title">${video.title}</div>
                <div class="video-meta">
                    <span>YouTube</span>
                    <span class="video-duration">Watch</span>
                </div>
            `;
            videoContainer.appendChild(videoCard);
        });
        
        videoSection.appendChild(videoContainer);
        block.appendChild(videoSection);
    }

    // AI ANSWER
    const aiLabel = document.createElement("div");
    aiLabel.classList.add("section-label");
    aiLabel.innerText = "🤖 AI Answer";
    block.appendChild(aiLabel);

    const aiReply = document.createElement("div");
    aiReply.classList.add("ai-message");
    aiReply.innerHTML = renderMarkdown(data.answer);
    block.appendChild(aiReply);

    // FEEDBACK BUTTONS
    const feedbackDiv = document.createElement("div");
    feedbackDiv.classList.add("feedback-container");

    const thumbsUp = document.createElement("button");
    thumbsUp.classList.add("feedback-btn", "up");
    thumbsUp.innerHTML = `<svg viewBox="0 0 24 24"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>`;

    const thumbsDown = document.createElement("button");
    thumbsDown.classList.add("feedback-btn", "down");
    thumbsDown.innerHTML = `<svg viewBox="0 0 24 24"><path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L10.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/></svg>`;

    thumbsUp.onclick = () => sendFeedback(data.query_id, 1, feedbackDiv);
    thumbsDown.onclick = () => sendFeedback(data.query_id, -1, feedbackDiv);

    feedbackDiv.appendChild(thumbsUp);
    feedbackDiv.appendChild(thumbsDown);
    block.appendChild(feedbackDiv);

    // LINKS
    if (data.links && data.links.length > 0) {
        const linksLabel = document.createElement("div");
        linksLabel.classList.add("section-label");
        linksLabel.innerText = "🔗 Related Links";
        block.appendChild(linksLabel);

        const linksContainer = document.createElement("div");
        linksContainer.classList.add("links-container");
        data.links.forEach(link => {
            const card = document.createElement("div");
            card.classList.add("link-card");

            const cardTop = document.createElement("div");
            cardTop.style.cssText = "display:flex;justify-content:space-between;align-items:start";

            const title = document.createElement("a");
            title.href = link.url;
            title.target = "_blank";
            title.classList.add("link-title");
            title.innerText = link.title;

            const bookmarkBtn = document.createElement("button");
            bookmarkBtn.classList.add("bookmark-btn");
            bookmarkBtn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16"><path d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>`;
            bookmarkBtn.onclick = (e) => {
                e.preventDefault();
                toggleBookmark(link, bookmarkBtn);
            };

            cardTop.appendChild(title);
            cardTop.appendChild(bookmarkBtn);

            const snippet = document.createElement("p");
            snippet.classList.add("link-snippet");
            snippet.innerText = link.snippet;

            const url = document.createElement("span");
            url.classList.add("link-url");
            url.innerText = link.url;

            card.appendChild(cardTop);
            card.appendChild(snippet);
            card.appendChild(url);
            linksContainer.appendChild(card);
        });
        block.appendChild(linksContainer);
    }

    resultsArea.insertBefore(block, resultsArea.firstChild);
}

// ── HISTORY SIDEBAR ──
function loadHistorySidebar() {
    historyList.innerHTML = '<div class="history-loading">Loading...</div>';
    fetch("/api/history/")
    .then(res => res.json())
    .then(data => {
        historyList.innerHTML = "";
        if (data.history.length === 0) {
            historyList.innerHTML = '<div class="history-loading">No history yet.</div>';
            return;
        }
        const groups = {};
        data.history.forEach(item => {
            const date = item.created_at.split(",")[0];
            if (!groups[date]) groups[date] = [];
            groups[date].push(item);
        });
        Object.entries(groups).forEach(([date, items]) => {
            const dateLabel = document.createElement("div");
            dateLabel.classList.add("history-date");
            dateLabel.innerText = date;
            historyList.appendChild(dateLabel);
            items.forEach(item => {
                const entry = document.createElement("div");
                entry.classList.add("history-entry");
                entry.innerText = item.query;
                entry.title = item.query;
                entry.addEventListener("click", () => {
                    document.querySelectorAll(".history-entry").forEach(e => e.classList.remove("active"));
                    entry.classList.add("active");
                    showHistoryItem(item);
                    closeSidebar();
                });
                historyList.appendChild(entry);
            });
        });
    });
}

function showHistoryItem(item) {
    if (!hasSearched) {
        hasSearched = true;
        hero.classList.add("hidden");
        mainContent.classList.remove("hero-mode");
        searchWrapper.classList.add("bottom-mode");
        suggestions.style.display = "none";
    }
    resultsArea.innerHTML = "";
    renderResult({
        query: item.query,
        answer: item.answer,
        videos: item.videos || [],
        links: item.links || []
    });
    const timeDiv = document.createElement("div");
    timeDiv.style.cssText = "font-size:0.72rem;color:#9ca3af;text-align:right;padding:0 1.5rem 1rem";
    timeDiv.innerText = "Searched on " + item.created_at;
    resultsArea.appendChild(timeDiv);
    resultsArea.scrollTop = 0;
}

function sendFeedback(queryId, rating, container) {
    fetch("/api/feedback/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_id: queryId, rating: rating })
    })
    .then(res => res.json())
    .then(() => {
        container.innerHTML = rating === 1 
            ? "<span style='color:#10b981;font-size:0.85rem'>✓ Thanks for the feedback!</span>"
            : "<span style='color:#6b7280;font-size:0.85rem'>✓ Thanks for the feedback!</span>";
    });
}

function toggleBookmark(link, btn) {
    fetch("/api/bookmark/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: link.url, title: link.title, snippet: link.snippet })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === "saved") {
            btn.classList.add("bookmarked");
        } else {
            btn.classList.remove("bookmarked");
        }
    });
}

// Load recommendations on page load (only in hero mode)
loadRecommendations();