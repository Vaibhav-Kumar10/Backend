import sys
import os

# Add parent directory to sys.path so Python can find 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import db, create_app  # Import db and Flask app factory
from app.models import User, SensorData, Alert, QuizResponse, InhalerUsage

# Create Flask app instance
app = create_app()

# Run database queries inside the app context
with app.app_context():
    def get_all_users():
        return User.query.all()

    def get_all_sensor_data():
        return SensorData.query.all()

    def get_all_alerts():
        return Alert.query.all()

    def get_all_quiz_responses():
        return QuizResponse.query.all()
    
    def get_all_inhaler_usage():
        return InhalerUsage.query.all()

    # Function to fetch and print all data
    def fetch_all_data():
        print("\n========================= USERS =========================")
        users = get_all_users()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Age: {user.age}, Gender: {user.gender}, "
                  f"Phone: {user.phone_no}, Medical History: {user.medical_history}, "
                  f"Emergency Contact: {user.emergency_contact_name} ({user.emergency_contact_phone})")

        print("\n===================== SENSOR DATA =====================")
        sensor_data = get_all_sensor_data()
        for data in sensor_data:
            print(f"ID: {data.id}, User ID: {data.user_id}, Timestamp: {data.timestamp}, AQI: {data.air_quality}, "
                  f"PM2.5: {data.pm25}, SO2: {data.so2_level}, NO2: {data.no2_level}, CO2: {data.co2_level}, "
                  f"Humidity: {data.humidity}, Temperature: {data.temperature}")

        print("\n======================= ALERTS =======================")
        alerts = get_all_alerts()
        for alert in alerts:
            print(f"ID: {alert.id}, User ID: {alert.user_id}, Message: {alert.message}, Timestamp: {alert.timestamp}")

        print("\n==================== QUIZ RESPONSES ====================")
        quiz_responses = get_all_quiz_responses()
        for quiz in quiz_responses:
            print(f"ID: {quiz.id}, User ID: {quiz.user_id}, Question: {quiz.question}, Answer: {quiz.answer}")

        print("\n=================== INHALER USAGE ====================")
        inhaler_usage = get_all_inhaler_usage()
        for usage in inhaler_usage:
            print(f"ID: {usage.id}, User ID: {usage.user_id}, Usage Count: {usage.usage_count}")

    if __name__ == "__main__":
        fetch_all_data()

