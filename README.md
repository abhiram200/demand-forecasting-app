# 📊 Demand Forecasting Web Application

An interactive **demand forecasting system** built with **Flask (Python backend)** and **HTML/CSS/JS frontend**, powered by **Machine Learning models**.  

This app allows users to:
- 🔑 Register, login, and securely manage accounts (with API keys).
- 📧 Reset forgotten passwords via email verification.
- 📂 Upload data for forecasting.
- 🔮 Get ML-driven demand predictions for products.
- 🌐 Use a React/HTML frontend that communicates with the Flask backend.

---

## 🚀 Features
- **Authentication System**  
  Login, Signup, Forgot Password, Session Management, API Key authentication.  
- **Secure API**  
  All predictions require a valid API key.  
- **Machine Learning Integration**  
  Trained model predicts future product demand based on historical and contextual features.  
- **Email Support**  
  Password reset via email using Gmail SMTP.  
- **Frontend-Backend Separation**  
  Clean structure with `index.html`, `style.css`, and JS for interaction.  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/demand-forecasting-app.git
cd demand-forecasting-app
pip install -r requirements.txt
```

### 2️⃣ Create a .env file in the root directory
```bash
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_gmail@gmail.com
```

### 3️⃣ Run the application
```bash
python app.py
```

### 4️⃣ Open your browser at
http://127.0.0.1:5050

## 🛠️ Usage
Sign Up with your email and password.
Login → You’ll be redirected to the dashboard.
Enter product details and date to get forecasted demand.
If password is forgotten → Use Forgot Password (reset link will be sent to email).

## 👤 Author
Abhiram RS
📧 Email - abhiramrs24@gmail.com
💼 Portfolio - https://abhiram200.github.io/portfolio/
