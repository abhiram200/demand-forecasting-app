from flask import Flask, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from dotenv import load_dotenv
import secrets
import sqlite3
import os

# ML imports (from your original code)
import pandas as pd
import joblib
import traceback

# Load model, encoders and .env
model = joblib.load('models/xgb_demand_forecasting_model.pkl')
encoders = joblib.load('models/ordinal_encoders.pkl')
load_dotenv()

# Secure API key
API_KEY = "your_super_secret_api_key"

# Create Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

# Secret key for sessions
app.secret_key = "another_super_secret_session_key"

# Ensure DB exists
DB_PATH = "users.db"
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    reset_token TEXT
                )''')
    conn.commit()
    conn.close()


# ---------------- MAIL CONFIG ---------------- #

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# ---------------- AUTH ROUTES ---------------- #

# Signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if username/email exists
    c.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "User already exists"}), 400
    
    # Generate API key
    api_key = secrets.token_urlsafe(32)

    # Hash password
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    c.execute("INSERT INTO users (username, email, password_hash, api_key) VALUES (?, ?, ?, ?)",
              (username, email, pw_hash, api_key))
    conn.commit()
    conn.close()

    return jsonify({"message": "Account created successfully. Please log in."}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    user_id, pw_hash = user
    if bcrypt.check_password_hash(pw_hash, password):
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    

# Forgot password endpoint
@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "No account found with that email"}), 404

    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)

    # Save token in DB (with expiry in real system)
    cursor.execute("UPDATE users SET reset_token = ? WHERE email = ?", (reset_token, email))
    conn.commit()
    conn.close()

    # Create reset link
    reset_link = f"http://127.0.0.1:5050/reset-password?token={reset_token}"

    # Send email
    try:
        msg = Message("Password Reset Request",
                      recipients=[email])
        msg.body = f"""Hello,  
We received a request to reset your password.  

Click the link below to reset your password:  
{reset_link}  

If you did not request this, you can ignore this email.  
"""
        mail.send(msg)
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

    return jsonify({"message": f"Password reset link sent to {email}"}), 200

# Serve reset-password.html when token link is opened
@app.route("/reset-password", methods=["GET"])
def reset_password_page():
    return send_from_directory(app.static_folder, "reset-password.html")


# Handle new password submission
@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password required"}), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE reset_token = ?", (token,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Invalid or expired token"}), 400

    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    # Update password and clear reset_token
    cursor.execute("UPDATE users SET password_hash = ?, reset_token = NULL WHERE reset_token = ?",
                   (hashed_password, token))
    conn.commit()
    conn.close()

    return jsonify({"message": "Password reset successful! Please login."}), 200


# Logout endpoint
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

# Session Checker endpoint
@app.route('/check_session', methods=['GET'])
def check_session():
    if 'user_id' not in session:
        return jsonify({"logged_in": False}), 200

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, api_key FROM users WHERE id = ?", (session['user_id'],))
    row = c.fetchone()
    conn.close()

    if row:
        username, api_key = row
        return jsonify({
            "logged_in": True,
            "username": username,
            "api_key": api_key   # ✅ send api_key too
        }), 200
    else:
        return jsonify({"logged_in": False}), 200


# ---------------- PROTECTED ROUTE ---------------- #

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/index.html')  # redirect to login if not authenticated
    return send_from_directory(app.static_folder, 'home.html')


# ---------------- ML ROUTES ---------------- #

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/predict', methods=['POST'])
def predict():
    provided_key = request.headers.get('x-api-key')
    if not provided_key:
        return jsonify({'error': 'Missing API key'}), 401

    # ✅ Validate API key from DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE api_key = ?", (provided_key,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'Invalid API key'}), 403

    try:
        json_data = request.get_json()
        input_df = pd.DataFrame([json_data])

        # Time features
        input_df['Date'] = pd.to_datetime(input_df['Date'])
        input_df['Year'] = input_df['Date'].dt.year
        input_df['Month'] = input_df['Date'].dt.month
        input_df['Day'] = input_df['Date'].dt.day
        input_df['DayOfWeek'] = input_df['Date'].dt.dayofweek

        # Encode categorical columns
        categorical_cols = ['Product ID', 'Category', 'Region',
                            'Weather Condition', 'Seasonality', 'Holiday/Promotion']
        for col in categorical_cols:
            if col in input_df.columns:
                input_df[[col]] = encoders[col].transform(input_df[[col]])

        input_df = input_df.drop(columns=['Date', 'Store ID'], errors='ignore')

        # Model prediction
        prediction = model.predict(input_df)[0]
        return jsonify({'prediction': round(float(prediction), 2)})

    except Exception as e:
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5050)
