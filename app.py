from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import joblib
import requests
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# ==============================
# App Setup
# ==============================
app = Flask(__name__)

# 🔥 FIX CORS (IMPORTANT)
CORS(app)

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response



# ==============================
# Load ML Model
# ==============================
try:
    model = joblib.load("model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model load error:", e)
    model = None

# ==============================
# Weather Config
# ==============================
load_dotenv()
API_KEY = os.getenv("API_KEY")
CITY = os.getenv("CITY")

# ==============================
# Routes
# ==============================
@app.route("/")
def home():
    return "🔥 Server Running"

latest_temp = 0   # 👈 at top

@app.route("/predict")
def predict():
    global latest_temp

    foot = request.args.get("foot")

    if foot is None:
        return jsonify({"error": "No foot temp"}), 400

    try:
        foot = float(foot)
    except:
        return jsonify({"error": "Invalid input"}), 400

    # 👇 STORE LIVE TEMP (IMPORTANT)
    latest_temp = foot

    # 🌡️ Weather
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()
        outside = data.get("main", {}).get("temp", 25)
    except:
        outside = 25

    # 🤖 ML
    input_df = pd.DataFrame([[foot, outside]], columns=["FootTemp", "OutsideTemp"])
    heat = int(model.predict(input_df)[0]) if model else 1

    return jsonify({
        "shoe_temp": foot,
        "outside_temp": outside,
        "heat": heat
    })
@app.route("/latest")
def latest():
    return jsonify({"shoe_temp": latest_temp})

# ==============================
# Run
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
