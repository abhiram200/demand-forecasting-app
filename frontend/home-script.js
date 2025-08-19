async function checkSession() {
  const res = await fetch("http://127.0.0.1:5050/check_session", {
    method: "GET",
    credentials: "include"
  });
  const data = await res.json();

  if (!data.logged_in) {
    window.location.href = "index.html";
    return null;
  } else {
    document.getElementById("userInfo").innerText = "Hello, " + data.username;
    localStorage.setItem("api_key", data.api_key);
    return data;
  }
}

document.getElementById("forecastForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  // 🔐 Check session again before predicting
  const session = await checkSession();
  if (!session) return; // not logged in, redirected

  const loader = document.getElementById("loader");
  const resultDiv = document.getElementById("result");

  // Clear previous results and show loader
  resultDiv.innerHTML = "";
  loader.style.display = "block";

  const formData = new FormData(e.target);
  const data = {};

  formData.forEach((value, key) => {
    if (key === "Holiday/Promotion") {
      data[key] = value === "Yes" ? 1 : 0; // Convert to numeric
    } else if (!isNaN(value) && value.trim() !== "") {
      data[key] = parseFloat(value); // Convert numeric values
    } else {
      data[key] = value; // Keep string values as is
    }
  });

  fetch("http://localhost:5050/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": localStorage.getItem("api_key")
    },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(response => {
      resultDiv.style.display = "block";

      if (response.prediction !== undefined) {
        resultDiv.innerHTML = `<strong>🔮 Predicted Demand:</strong> ${response.prediction}`;
      } else if (response.error) {
        resultDiv.innerHTML = `<span style="color:red;">⚠️ Server Error: ${response.error}</span>`;
      } else {
        resultDiv.innerHTML = `<span style="color:red;">⚠️ Unexpected response from server.</span>`;
      }
    })
    .catch(error => {
      resultDiv.innerHTML = `<span style="color:red;">❌ Network Error: ${error.message}</span>`;
    })
    .finally(() => {
      loader.style.display = "none";
    });
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("http://127.0.0.1:5050/logout", {
    method: "POST",
    credentials: "include"
  });
  window.location.href = "index.html";
});

// ✅ Initial session check when page loads
checkSession();
