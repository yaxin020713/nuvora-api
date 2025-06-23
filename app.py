from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///local.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    water_ml = db.Column(db.Integer, nullable=True)
    heart_rate = db.Column(db.Integer, nullable=True)
    sleep_hour = db.Column(db.Float, nullable=True)

@app.route("/health-data", methods=["POST"])
def add_data():
    data = request.get_json()
    entry = HealthData(
        user_id=data.get("user_id"),
        water_ml=data.get("water_ml"),
        heart_rate=data.get("heart_rate"),
        sleep_hour=data.get("sleep_hour")
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "Data added successfully"}), 201

@app.route("/health-data", methods=["GET"])
def get_data():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    records = HealthData.query.filter_by(user_id=user_id).order_by(HealthData.timestamp.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "water_ml": r.water_ml,
            "heart_rate": r.heart_rate,
            "sleep_hour": r.sleep_hour
        } for r in records
    ])

if __name__ == "__main__":
    app.run(debug=True)
