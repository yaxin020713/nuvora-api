import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai

# === 初始化 Flask 與資料庫 ===
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === 資料庫模型 ===
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    heart_rate = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    water_intake = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

with app.app_context():
    db.create_all()

# === 設定 OpenAI 金鑰 ===
openai.api_key = os.environ.get("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")

# === Health Data API ===
@app.route('/health-data', methods=['POST'])
def add_health_data():
    data = request.json
    new_data = HealthData(
        user_id = data.get('user_id'),
        heart_rate = data.get('heart_rate'),
        sleep_hours = data.get('sleep_hours'),
        water_intake = data.get('water_intake')
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({'message': 'Health data stored successfully'}), 201


# === Whisper + GPT API ===
@app.route('/whisper', methods=['POST'])
def whisper_gpt():
    # 如果是 JSON 直接拿 text
    if request.is_json:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'No text provided'}), 400

    # 如果是 form-data 就處理音檔
    else:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file uploaded'}), 400

        audio_file = request.files['audio']

        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        text = transcript['text']

    # GPT: 將 text 結構化
    prompt = f"""
    使用者說：{text}
    請將此句轉成 JSON，包含：
    - heartRate
    - waterIntake
    - sleepHours
    如果沒有提到請回 null。
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "你是一個健康數據的結構化助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    structured_data = response['choices'][0]['message']['content']

    return jsonify({
        'transcript': text,
        'structured_data': structured_data
    })


# === 健康檢查路由 ===
@app.route('/')
def index():
    return 'Nuvora API is running!'


# === Run ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
