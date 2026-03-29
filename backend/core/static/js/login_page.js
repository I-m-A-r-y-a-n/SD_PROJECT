


document.addEventListener("DOMContentLoaded", function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    document.querySelector(".signin").addEventListener("click", async function () {

        const email = document.querySelector(".email").value;
        const password = document.querySelector(".password").value;

        const res = await fetch("/api/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            credentials: "same-origin",
            body: JSON.stringify({ email, password })
        });

        const result = await res.json();

        if (res.ok) {
            alert("Login successful!");
            window.location.href = "/home/";
        } else {
            alert(result.error || "Login failed");
        }
    });

});


