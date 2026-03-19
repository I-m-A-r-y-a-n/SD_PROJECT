const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");

menuBtn.onclick = () => {

sidebar.classList.toggle("open");
overlay.classList.toggle("show");
menuBtn.classList.toggle("active");

};

overlay.onclick = () => {

sidebar.classList.remove("open");
overlay.classList.remove("show");
menuBtn.classList.remove("active");

};

const askBtn = document.getElementById("askBtn");
const searchInput = document.getElementById("searchInput");

askBtn.addEventListener("click", sendSearch);

searchInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendSearch();
    }
});

function sendSearch() {

    const query = searchInput.value.trim();
    if(query === "") return;

    fetch("/api/search/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {

        console.log("Stored:", data);

        const results = document.getElementById("results");

        // USER MESSAGE
        const userMessage = document.createElement("div");
        userMessage.classList.add("user-message");
        userMessage.innerText = "You: " + data.query;
        results.appendChild(userMessage);

        // YOUTUBE VIDEOS
        if(data.videos && data.videos.length > 0) {
            const videoContainer = document.createElement("div");
            videoContainer.classList.add("video-container");

           data.videos.forEach(video => {
                const iframe = document.createElement("iframe");
                iframe.src = "https://www.youtube.com/embed/" + video.video_id + "?origin=http://localhost:8000";
                iframe.width = "100%";
                iframe.height = "250";
                iframe.allowFullscreen = true;
                iframe.style.borderRadius = "12px";
                iframe.style.border = "none";
                iframe.style.marginBottom = "8px";

                // hide iframe if video can't be embedded
                iframe.onerror = function() {
                    this.style.display = "none";
                };

                videoContainer.appendChild(iframe);
            });

            results.appendChild(videoContainer);
        }

        // AI REPLY
        const aiReply = document.createElement("div");
        aiReply.classList.add("ai-message");
        aiReply.innerText = "AI: " + data.answer;
        results.appendChild(aiReply);

        searchInput.value = "";
    });
}






