from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import openai

# 載入 .env
load_dotenv()

app = Flask(__name__)

# 設定資料庫連線
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 健康數據模型
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    heart_rate = db.Column(db.Integer)
    sleep_hour = db.Column(db.Float)
    water_ml = db.Column(db.Integer)

with app.app_context():
    db.create_all()

# Whisper + GPT 需要的金鑰
openai.api_key = os.environ.get("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")

@app.route("/")
def index():
    return "Nuvora API is running!"

# 新增健康數據
@app.route("/health-data", methods=["POST"])
def add_health_data():
    data = request.json
    new_data = HealthData(
        user_id = data.get("user_id"),
        heart_rate = data.get("heart_rate"),
        sleep_hour = data.get("sleep_hour"),
        water_ml = data.get("water_ml")
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Health data saved"}), 201

# Whisper 語音轉文字 + GPT 範例
@app.route("/whisper", methods=["POST"])
def whisper():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    audio.save("temp_audio.mp3")

    # Whisper 轉文字
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=open("temp_audio.mp3", "rb"),
        response_format="text"
    )

    # GPT 解析文字 ➜ 生成健康數據 JSON
    prompt = f"""
    使用者輸入：{transcript}
    請從中擷取以下 JSON：
    {{
      "heartRate": ...
      "sleepHour": ...
      "waterML": ...
    }}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一個健康數據解析助理"},
            {"role": "user", "content": prompt}
        ]
    )

    gpt_result = response.choices[0].message.content

    return jsonify({
        "transcript": transcript,
        "gpt_result": gpt_result
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
