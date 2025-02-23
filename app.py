from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS for cross-origin requests
import pandas as pd
import joblib
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained model and encoders
try:
    model = joblib.load("malaria_model.pkl")
    le_region = joblib.load("le_region.pkl")
    le_gender = joblib.load("le_gender.pkl")
    le_drug = joblib.load("le_drug.pkl")
    le_tablets = joblib.load("le_tablets.pkl")
    logger.info("Model and encoders loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model or encoders: {e}")

# Dosage calculation function
def calculate_dosage(drug, weight):
    """Calculate the dosage based on the drug and patient's weight."""
    try:
        if drug == "Artemether-lumefantrine":
            if weight < 15:
                return "1 tablet per dose"
            elif weight < 25:
                return "2 tablets per dose"
            elif weight < 35:
                return "3 tablets per dose"
            else:
                return "4 tablets per dose"
        elif drug == "IV artesunate":
            return f"{2.4 * weight} mg per dose"
        elif drug == "Chloroquine phosphate":
            initial = 10 * weight
            subsequent = 5 * weight
            return f"Initial: {initial} mg base, Subsequent: {subsequent} mg base per dose"
        elif drug == "Atovaquone-proguanil":
            if weight < 8:
                return "2 pediatric tablets (62.5 mg atovaquone/25 mg proguanil) per dose"
            elif weight < 10:
                return "3 pediatric tablets (62.5 mg atovaquone/25 mg proguanil) per dose"
            elif weight < 20:
                return "1 adult tablet (250 mg atovaquone/100 mg proguanil) per dose"
            elif weight < 30:
                return "2 adult tablets (250 mg atovaquone/100 mg proguanil) per dose"
            elif weight < 40:
                return "3 adult tablets (250 mg atovaquone/100 mg proguanil) per dose"
            else:
                return "4 adult tablets (250 mg atovaquone/100 mg proguanil) per dose"
        else:
            return "Dosage not defined"
    except Exception as e:
        logger.error(f"Error in dosage calculation: {e}")
        return "Error in dosage calculation"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate incoming data (you can add further validation)
        if not data:
            logger.warning("Empty request data")
            return jsonify({"error": "No data provided"}), 400

        # Create DataFrame from input data
        input_data = pd.DataFrame({
            "fever": [int(data.get("fever", 0))],
            "chills": [int(data.get("chills", 0))],
            "sweats": [int(data.get("sweats", 0))],
            "headache": [int(data.get("headache", 0))],
            "nausea": [int(data.get("nausea", 0))],
            "vomiting": [int(data.get("vomiting", 0))],
            "body_aches": [int(data.get("body_aches", 0))],
            "impaired_consciousness": [int(data.get("impaired_consciousness", 0))],
            "prostration": [int(data.get("prostration", 0))],
            "convulsions": [int(data.get("convulsions", 0))],
            "deep_breathing": [int(data.get("deep_breathing", 0))],
            "respiratory_distress": [int(data.get("respiratory_distress", 0))],
            "abnormal_bleeding": [int(data.get("abnormal_bleeding", 0))],
            "jaundice": [int(data.get("jaundice", 0))],
            "severe_anemia": [int(data.get("severe_anemia", 0))],
            "Age": [int(data.get("age", 0))],
            "Weight": [int(data.get("weight", 0))],
            "Region": le_region.transform([data.get("region", "Sub-Saharan Africa")]),
            "Gender": le_gender.transform([data.get("gender", "Male")]),
            "Pregnant": [int(data.get("pregnant", 0))],
            "G6PD_Deficiency": [int(data.get("g6pd_deficiency", 0))],
            "Previous_Medications": [int(data.get("previous_medications", 0))]
        })

        # Make prediction
        prediction = model.predict(input_data)
        pred_drug = le_drug.inverse_transform([prediction[0][0]])[0]
        pred_tablets = le_tablets.inverse_transform([prediction[0][1]])[0]
        dosage = calculate_dosage(pred_drug, input_data["Weight"][0])

        # Return JSON response
        return jsonify({
            "recommended_drug": pred_drug,
            "tablets_per_day": int(pred_tablets),
            "dosage": dosage
        })
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return jsonify({"error": "Failed to process the request"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
