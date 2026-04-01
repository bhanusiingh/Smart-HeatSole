from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import requests
import pandas as pd
import warnings

# 🔇 Hide sklearn warnings
warnings.filterwarnings("ignore")

# ==============================
# App Setup
# ==============================
app = Flask(__name__)
CORS(app)

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
# Weather API Config
# ==============================
API_KEY = "e01e93ea7584bcc38b3fc065aeecbbc5"
CITY = "Jalandhar"

# ==============================
# Home Route
# ==============================
@app.route("/")
def home():
    return "🔥 AI Heating Insole Server Running"

# ==============================
# Prediction Route
# ==============================
@app.route("/predict")
def predict():
    foot = request.args.get("foot")

    # 🔍 Validate input
    if foot is None:
        return jsonify({"error": "Provide foot temperature"}), 400

    try:
        foot = float(foot)
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400

    # ==============================
    # Get Weather Data
    # ==============================
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},IN&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()

        outside = data.get("main", {}).get("temp", 25)

    except Exception as e:
        print("❌ Weather API error:", e)
        outside = 25  # fallback

    # ==============================
    # ML Prediction
    # ==============================
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        input_df = pd.DataFrame([[foot, outside]], columns=["FootTemp", "OutsideTemp"])
        pred = model.predict(input_df)
        heat = int(pred[0])
    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500

    # ==============================
    # Debug (optional)
    # ==============================
    print(f"Foot: {foot} | Outside: {outside} | Heat: {heat}")

    # ==============================
    # Response
    # ==============================
    return jsonify({
        "shoe_temp": foot,
        "outside_temp": round(outside, 1),
        "heat": heat
    })

# ==============================
# Run Server
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)