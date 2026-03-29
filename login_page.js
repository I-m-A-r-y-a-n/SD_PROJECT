document.querySelector(".signin").addEventListener("click", async function () {
    const data = {
        email: document.querySelector(".email").value,
        password: document.querySelector(".password").value
    };

    const res = await fetch("http://127.0.0.1:8000/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    if (res.ok) {
        localStorage.setItem("username", result.username || data.email);
        window.location.href = "home_page.html";  
    } else {
        alert(result.error || "Login failed");
    }
});


