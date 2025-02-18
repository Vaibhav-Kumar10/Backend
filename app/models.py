from . import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    medical_history = db.Column(db.Text, nullable=True)

    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_phone = db.Column(db.String(15), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    air_quality = db.Column(db.Integer, nullable=False)  # AQI
    pm25 = db.Column(db.Float, nullable=False)  # PM2.5
    so2_level = db.Column(db.Float, nullable=False)  # SO2 level
    no2_level = db.Column(db.Float, nullable=False)  # NO2 level
    co2_level = db.Column(db.Float, nullable=False)  # CO2 level
    humidity = db.Column(db.Float, nullable=False)  # Humidity
    temperature = db.Column(db.Float, nullable=False)  # Temperature

class InhalerUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    usage_count = db.Column(db.Integer, default=0, nullable=False)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class QuizResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String(255), nullable=False)  # Store full question text
    answer = db.Column(db.String(255), nullable=False)  # Store full selected answer
