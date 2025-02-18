from flask import Blueprint, request, jsonify
from .models import db, User, SensorData, Alert, QuizResponse, InhalerUsage
from datetime import datetime
import requests
from flask_cors import CORS

routes = Blueprint("routes", __name__)
CORS(routes)


# ---------------------- HOME ROUTE ----------------------
@routes.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Smart Inhaler API!"}


# ---------------------- SENSOR DATA ROUTES ----------------------
@routes.route("/upload-sensor-data", methods=["POST"])
def upload_sensor_data():
    data = request.json

    # Validate required fields
    required_fields = [
        "user_id",
        "air_quality",
        "pm25",
        "so2_level",
        "no2_level",
        "co2_level",
        "humidity",
        "temperature",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Store sensor data in database
    new_data = SensorData(
        user_id=data["user_id"],
        timestamp=datetime.now(),
        air_quality=data["air_quality"],
        pm25=data["pm25"],
        so2_level=data["so2_level"],
        no2_level=data["no2_level"],
        co2_level=data["co2_level"],
        humidity=data["humidity"],
        temperature=data["temperature"],
    )

    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Sensor data uploaded successfully"}), 201


@routes.route("/get-user-data/<int:user_id>", methods=["GET"])
def get_user_data(user_id):
    user_data = SensorData.query.filter_by(user_id=user_id).all()

    # Retrieve all stored sensor data for the user
    data = [
        {
            "timestamp": d.timestamp,
            "air_quality": d.air_quality,
            "pm25": d.pm25,
            "so2_level": d.so2_level,
            "no2_level": d.no2_level,
            "co2_level": d.co2_level,
            "humidity": d.humidity,
            "temperature": d.temperature,
        }
        for d in user_data
    ]

    return jsonify({"user_data": data})


# ---------------------- ALERT ROUTES ----------------------
@routes.route("/get-alerts/<int:user_id>", methods=["GET"])
def get_alerts(user_id):
    alerts = Alert.query.filter_by(user_id=user_id).all()
    alert_data = [{"message": a.message, "timestamp": a.timestamp} for a in alerts]
    return jsonify({"alerts": alert_data})


# ---------------------- SAVE & RETRIEVE USER PROFILE ----------------------
@routes.route("/save-profile", methods=["POST"])
def save_profile():
    data = request.json

    user = User.query.filter_by(phone_no=data["mobile"]).first()

    if user:
        # Update existing user
        user.name = data["name"]
        user.age = data["age"]
        user.gender = data["gender"]
        user.medical_history = data.get("medicalHistory", "")
        user.emergency_contact_name = data["emergencyContacts"][0]["name"]
        user.emergency_contact_phone = data["emergencyContacts"][0]["phone"]
    else:
        # Create new user
        user = User(
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            phone_no=data["mobile"],
            medical_history=data.get("medicalHistory", ""),
            emergency_contact_name=data["emergencyContacts"][0]["name"],
            emergency_contact_phone=data["emergencyContacts"][0]["phone"],
        )
        db.session.add(user)

    db.session.commit()

    return jsonify({"message": "Profile saved successfully", "user_id": user.id}), 201


@routes.route("/get-user/<string:id>", methods=["GET"])
def get_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender,
        "phone_no": user.phone_no,
        "medical_history": user.medical_history,
        "emergency_contact_name": user.emergency_contact_name,
        "emergency_contact_phone": user.emergency_contact_phone,
    }

    return jsonify(user_data)


# ---------------------- INHALER USAGE ROUTES ----------------------


@routes.route("/use-inhaler", methods=["POST"])
def use_inhaler():
    """Increments the inhaler usage counter each time it's used."""
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    inhaler_usage = InhalerUsage.query.filter_by(user_id=user_id).first()

    if inhaler_usage:
        inhaler_usage.usage_count += 1
    else:
        inhaler_usage = InhalerUsage(user_id=user_id, usage_count=1)
        db.session.add(inhaler_usage)

    db.session.commit()
    return (
        jsonify(
            {
                "message": "Inhaler usage recorded",
                "usage_count": inhaler_usage.usage_count,
            }
        ),
        200,
    )


@routes.route("/get-inhaler-usage/<int:user_id>", methods=["GET"])
def get_inhaler_usage(user_id):
    """Fetches the current inhaler usage count for the user."""
    inhaler_usage = InhalerUsage.query.filter_by(user_id=user_id).first()

    if not inhaler_usage:
        return jsonify({"error": "No inhaler usage data found for the user"}), 404

    return jsonify({"user_id": user_id, "usage_count": inhaler_usage.usage_count}), 200


# ---------------------- SUBMIT & RETRIEVE QUIZ RESPONSES ----------------------
# @routes.route("/submit-quiz", methods=["POST"])
# def submit_quiz():
#     data = request.json
#     user_id = data.get("user_id")
#     answers = data.get("answers", {})

#     if not user_id or not answers:
#         return jsonify({"error": "Invalid request. Provide user_id and at least one answer"}), 400

#     # Store only relevant quiz questions (store = true in frontend)
#     stored_questions = [
#         "How often do you experience asthma symptoms?",
#         "Which of the following most commonly triggers your symptoms?",  # ✅ Updated for single-choice
#         "Do you notice symptoms worsening in specific weather conditions?",
#         "Do you live in or frequently visit areas with poor air quality?",
#         "Do you experience difficulty breathing at night?",
#     ]

#     for question, answer_text in answers.items():
#         if question in stored_questions:
#             new_response = QuizResponse(
#                 user_id=user_id, question=question, answer=answer_text
#             )
#             db.session.add(new_response)


#     db.session.commit()
#     return jsonify({"message": "Quiz responses saved successfully"}), 201
@routes.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    data = request.json
    user_id = data.get("user_id")
    answers = data.get("answers", {})

    print("Received quiz data:", data)  # Debugging step

    if not user_id or not answers:
        return (
            jsonify(
                {"error": "Invalid request. Provide user_id and at least one answer"}
            ),
            400,
        )

    stored_questions = [
        "How often do you experience asthma symptoms?",
        "Which of the following commonly trigger your symptoms?",
        "Do you notice symptoms worsening in specific weather conditions?",
        "Do you live in or frequently visit areas with poor air quality?",
        "Do you experience difficulty breathing at night?",
    ]

    for question, answer_text in answers.items():
        print(
            f"Processing question: {question}, Answer: {answer_text}"
        )  # Debugging step
        if question in stored_questions:
            new_response = QuizResponse(
                user_id=user_id, question=question, answer=answer_text
            )
            db.session.add(new_response)

    db.session.commit()
    return jsonify({"message": "Quiz responses saved successfully"}), 201


@routes.route("/get-quiz-responses/<int:user_id>", methods=["GET"])
def get_quiz_responses(user_id):
    responses = QuizResponse.query.filter_by(user_id=user_id).all()
    quiz_data = [{"question": r.question, "answer": r.answer} for r in responses]
    return jsonify({"quiz_responses": quiz_data})


# ---------------------- AI INTEGRATION ROUTE ----------------------
# AI Model URL
# AI_MODEL_URL = "https://ml-model-aasthma-pio6.onrender.com/predict"
AI_MODEL_URL = "http://127.0.0.1:7860/predict"


@routes.route("/send-data-to-ai/<int:user_id>", methods=["GET"])
def send_data_to_ai(user_id):
    # Fetch the latest sensor data for the user
    latest_sensor_data = (
        SensorData.query.filter_by(user_id=user_id)
        .order_by(SensorData.timestamp.desc())
        .first()
    )
    if not latest_sensor_data:
        return jsonify({"error": "No sensor data found for the user"}), 404

    # Fetch stored quiz responses for the user
    responses = QuizResponse.query.filter_by(user_id=user_id).all()
    if not responses:
        return jsonify({"error": "No quiz responses found for the user"}), 404

    # Prepare sensor data
    sensor_data = {
        "AQI": latest_sensor_data.air_quality,
        "PM2.5": latest_sensor_data.pm25,
        "SO2 level": latest_sensor_data.so2_level,
        "NO2 level": latest_sensor_data.no2_level,
        "CO2 level": latest_sensor_data.co2_level,
        "Humidity": latest_sensor_data.humidity,
        "Temperature": latest_sensor_data.temperature,
    }

    # Prepare quiz data (ensure keys match expected AI model input)
    quiz_data = {
        "Asthma Symptoms Frequency": responses[0].answer,
        "Triggers": responses[1].answer,
        "Weather Sensitivity": responses[2].answer,
        "Poor Air Quality Exposure": responses[3].answer,
        "Night Breathing Difficulty": responses[4].answer,
    }

    # Merge both datasets
    combined_data = {**sensor_data, **quiz_data}

    try:
        # Send data to AI model
        ai_response = requests.post(AI_MODEL_URL, json=combined_data, timeout=10)
        ai_response.raise_for_status()  # Raise an error for failed requests

        # Parse AI response
        ai_result = ai_response.json()
        risk_score = ai_result.get(
            "asthma_risk_score", 0
        )  # Default risk score = 0 if missing

        # If risk score is high, store an alert
        if risk_score >= 0.6:
            new_alert = Alert(
                user_id=user_id,
                message=f"High Risk Detected: {risk_score}",
                timestamp=datetime.now(),
            )
            db.session.add(new_alert)
            db.session.commit()

        return (
            jsonify({"risk_score": risk_score, "message": "AI risk score received"}),
            200,
        )

    except requests.exceptions.RequestException as e:
        return (
            jsonify({"error": "Failed to connect to AI model", "details": str(e)}),
            500,
        )
