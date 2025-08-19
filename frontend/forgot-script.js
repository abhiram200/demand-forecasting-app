// forgot-script.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = form.querySelector("input[type='email']").value;

    try {
      const response = await fetch("http://127.0.0.1:5050/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      if (response.ok) {
        alert("📩 " + data.message);
      } else {
        alert("⚠️ " + data.error);
      }
    } catch (err) {
      alert("Something went wrong. Try again.");
    }
  });
});
