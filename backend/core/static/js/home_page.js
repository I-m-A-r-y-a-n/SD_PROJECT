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
        // clear active history
        document.querySelectorAll(".history-entry").forEach(e => e.classList.remove("active"));
    };

    // ── SIDEBAR ITEMS ──
    document.querySelectorAll(".sidebar-item").forEach(item => {
        const action = item.dataset.action;
        item.addEventListener("click", function () {
            if (action === "logout") {
                fetch("/api/logout/").then(() => { window.location.href = "/login/"; });
            } else {
                alert(action.charAt(0).toUpperCase() + action.slice(1) + " — Coming Soon!");
            }
        });
    });

    // ── CHIPS ──
    document.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", function () {
            searchInput.value = this.innerText;
            sendSearch();
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
            suggestions.style.display = "none";
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

        // delay skeleton slightly so animation feels smooth
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

        // USER MESSAGE
        const userMsg = document.createElement("div");
        userMsg.classList.add("user-message");
        userMsg.innerText = data.query;
        block.appendChild(userMsg);

        // VIDEOS
        if (data.videos && data.videos.length > 0) {
            const label = document.createElement("div");
            label.classList.add("section-label");
            label.innerText = "📹 Related Videos";
            block.appendChild(label);

            const videoContainer = document.createElement("div");
            videoContainer.classList.add("video-container");
            data.videos.forEach(video => {
                const iframe = document.createElement("iframe");
                iframe.src = "https://www.youtube.com/embed/" + video.video_id + "?origin=https://sdproject-production.up.railway.app";
                iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share");
                iframe.setAttribute("allowfullscreen", "true");
                iframe.setAttribute("frameborder", "0");
                videoContainer.appendChild(iframe);
            });
            block.appendChild(videoContainer);
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

                const title = document.createElement("a");
                title.href = link.url;
                title.target = "_blank";
                title.classList.add("link-title");
                title.innerText = link.title;

                const snippet = document.createElement("p");
                snippet.classList.add("link-snippet");
                snippet.innerText = link.snippet;

                const url = document.createElement("span");
                url.classList.add("link-url");
                url.innerText = link.url;

                card.appendChild(title);
                card.appendChild(snippet);
                card.appendChild(url);
                linksContainer.appendChild(card);
            });
            block.appendChild(linksContainer);
        }

        resultsArea.insertBefore(block, resultsArea.firstChild);
    }

    // ── HISTORY SIDEBAR (list of queries) ──
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

            // group by date
            const groups = {};
            data.history.forEach(item => {
                const date = item.created_at.split(",")[0]; // "28 Mar 2026"
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
                        // mark active
                        document.querySelectorAll(".history-entry").forEach(e => e.classList.remove("active"));
                        entry.classList.add("active");

                        // show this single conversation
                        showHistoryItem(item);
                        closeSidebar();
                    });

                    historyList.appendChild(entry);
                });
            });
        });
    }

    // ── SHOW SINGLE HISTORY ITEM ──
    function showHistoryItem(item) {
        if (!hasSearched) {
            hasSearched = true;
            hero.classList.add("hidden");
            mainContent.classList.remove("hero-mode");
            searchWrapper.classList.add("bottom-mode");
            suggestions.style.display = "none";
        }

        resultsArea.innerHTML = "";

        // reuse renderResult — just pass item as if it came from search API
        renderResult({
            query: item.query,
            answer: item.answer,
            videos: item.videos || [],
            links: item.links || []
        });

        // add timestamp at bottom
        const timeDiv = document.createElement("div");
        timeDiv.style.cssText = "font-size:0.72rem;color:#9ca3af;text-align:right;padding:0 1.5rem 1rem";
        timeDiv.innerText = "Searched on " + item.created_at;
        resultsArea.appendChild(timeDiv);

        resultsArea.scrollTop = 0;
    }