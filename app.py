import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

# 初始化 Flask
app = Flask(__name__)

# 讀取環境變數
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 設定 SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)

# 定義資料表
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    heart_rate = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)

with app.app_context():
    db.create_all()

# Whisper + GPT 路由
@app.route("/whisper", methods=["POST"])
def whisper_gpt():
    client = OpenAI(api_key=OPENAI_API_KEY)

    audio_file = request.files["audio"]
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    text = transcript.text

    prompt = f"""
    使用者說：「{text}」
    請將此句轉成 JSON，包含：
    - heartRate
    - waterIntake
    - sleepHours
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是健康數據助理，負責把句子轉成結構化 JSON"},
            {"role": "user", "content": prompt}
        ]
    )

    return jsonify({"whisper_result": text, "gpt_result": response.choices[0].message.content})

# 健康數據手動輸入
@app.route("/health-data", methods=["POST"])
def add_health_data():
    data = request.get_json()
    new_data = HealthData(
        user_id=data.get("user_id"),
        heart_rate=data.get("heart_rate"),
        water_intake=data.get("water_intake"),
        sleep_hours=data.get("sleep_hours")
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Health data added successfully"})

# 根目錄測試
@app.route("/")
def index():
    return jsonify({"message": "Nuvora API running!"})
