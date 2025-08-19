document.getElementById("loginForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      const res = await fetch("http://127.0.0.1:5050/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();
      if (res.ok) {
        alert("Login successful!");
        window.location.href = "home.html";
      } else {
        alert(data.error);
      }
    });