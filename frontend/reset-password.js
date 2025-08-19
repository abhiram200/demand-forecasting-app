document.getElementById("resetForm").addEventListener("submit", async function(e) {
      e.preventDefault();
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");
      const newPassword = document.getElementById("newPassword").value;

      const res = await fetch("/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword })
      });

      const data = await res.json();
      alert(data.message || data.error);
      if (res.ok) {
        window.location.href = "index.html";
      }
    });