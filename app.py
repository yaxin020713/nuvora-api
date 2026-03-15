import os
import json
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化 Flask
app = Flask(__name__)

# 讀取環境變數
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///nuvora.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 設定 SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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


def serialize_health_data(record):
    return {
        "id": record.id,
        "user_id": record.user_id,
        "heart_rate": record.heart_rate,
        "water_intake": record.water_intake,
        "sleep_hours": record.sleep_hours,
    }


def validate_health_payload(payload):
    if not payload:
        return None, "JSON body is required"

    user_id = payload.get("user_id")
    if not user_id:
        return None, "user_id is required"

    try:
        normalized = {
            "user_id": str(user_id),
            "heart_rate": int(payload["heart_rate"]) if payload.get("heart_rate") is not None else None,
            "water_intake": int(payload["water_intake"]) if payload.get("water_intake") is not None else None,
            "sleep_hours": float(payload["sleep_hours"]) if payload.get("sleep_hours") is not None else None,
        }
    except (TypeError, ValueError):
        return None, "heart_rate and water_intake must be integers, sleep_hours must be a number"

    return normalized, None


def create_health_data_record(payload):
    record = HealthData(**payload)
    db.session.add(record)
    db.session.commit()
    return record


def parse_health_text(client, text):
    prompt = f"""
    使用者說：「{text}」
    請將此句轉成 JSON，包含：
    - heartRate
    - waterIntake
    - sleepHours
    如果缺少某欄位，請填 null。
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "你是健康數據助理，負責把句子轉成結構化 JSON"},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)


def parse_and_optionally_save(text, user_id=None, save_result=False):
    if not OPENAI_API_KEY:
        return None, "OPENAI_API_KEY is not configured", 500

    client = OpenAI(api_key=OPENAI_API_KEY)
    gpt_result = parse_health_text(client, text)

    saved_record = None
    if save_result:
        normalized_payload, error = validate_health_payload({
            "user_id": user_id,
            "heart_rate": gpt_result.get("heartRate"),
            "water_intake": gpt_result.get("waterIntake"),
            "sleep_hours": gpt_result.get("sleepHours"),
        })
        if error:
            return None, error, 400

        saved_record = create_health_data_record(normalized_payload)

    return {
        "input_text": text,
        "gpt_result": gpt_result,
        "saved": bool(saved_record),
        "saved_record": serialize_health_data(saved_record) if saved_record else None,
    }, None, 200

# Whisper + GPT 路由
@app.route("/whisper", methods=["POST"])
def whisper_gpt():
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "audio file is required"}), 400

    if not OPENAI_API_KEY:
        return jsonify({"error": "OPENAI_API_KEY is not configured"}), 500

    client = OpenAI(api_key=OPENAI_API_KEY)
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    save_result = request.form.get("save", "false").lower() == "true"
    user_id = request.form.get("user_id")
    result, error, status_code = parse_and_optionally_save(
        transcript.text,
        user_id=user_id,
        save_result=save_result,
    )
    if error:
        return jsonify({"error": error}), status_code

    result["whisper_result"] = transcript.text
    return jsonify(result)


@app.route("/parse-text", methods=["POST"])
def parse_text():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "JSON body is required"}), 400

    input_text = payload.get("text")
    if not input_text:
        return jsonify({"error": "text is required"}), 400

    result, error, status_code = parse_and_optionally_save(
        input_text,
        user_id=payload.get("user_id"),
        save_result=bool(payload.get("save")),
    )
    if error:
        return jsonify({"error": error}), status_code

    return jsonify(result), status_code


@app.route("/health-data", methods=["GET"])
def list_health_data():
    user_id = request.args.get("user_id")
    query = HealthData.query

    if user_id:
        query = query.filter_by(user_id=user_id)

    records = query.order_by(HealthData.id.desc()).all()
    return jsonify({
        "count": len(records),
        "items": [serialize_health_data(record) for record in records],
    })

# 健康數據手動輸入
@app.route("/health-data", methods=["POST"])
def add_health_data():
    normalized_payload, error = validate_health_payload(request.get_json())
    if error:
        return jsonify({"error": error}), 400

    new_data = create_health_data_record(normalized_payload)
    return jsonify({
        "message": "Health data added successfully",
        "data": serialize_health_data(new_data),
    }), 201

# 根目錄測試
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    return jsonify({"message": "Nuvora API running!"})


if __name__ == "__main__":
    app.run(debug=True)
