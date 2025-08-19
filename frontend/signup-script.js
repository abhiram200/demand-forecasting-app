document.getElementById("signupForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value;
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      const res = await fetch("http://127.0.0.1:5050/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });

      const data = await res.json();
      if (res.ok) {
        alert(data.message);
        window.location.href = "index.html";
      } else {
        alert(data.error);
      }
    });