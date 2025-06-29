import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import openai

# 載入 .env
load_dotenv()

app = Flask(__name__)

# 讀取環境變數
DATABASE_URL = os.environ.get('DATABASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# 設定 SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

# 設定 OpenAI Key
openai.api_key = OPENAI_API_KEY

# 定義一個簡單的 HealthData 範例資料表
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heart_rate = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)

# 初始化 DB（正式環境請改成 migration 工具）
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return jsonify({'message': 'Nuvora API is running!'})

@app.route('/whisper', methods=['POST'])
def whisper_gpt():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']

    # 1️⃣ 語音轉文字（Whisper）
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )

    text = transcript['text']

    # 2️⃣ 呼叫 GPT 做文字轉 JSON
    prompt = f"""
    使用者說：{text}
    請將此句轉成 JSON，包含：
    - heartRate
    - waterIntake
    - sleepHours
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是健康助理，負責把輸入的敘述轉成健康數據 JSON。"},
            {"role": "user", "content": prompt}
        ]
    )

    gpt_json = response['choices'][0]['message']['content']

    # 3️⃣（可選）把結果寫進 DB
    # 注意：這裡要自己做 JSON 解析與格式驗證
    # 範例略

    return jsonify({
        'transcript': text,
        'gpt_json': gpt_json
    })

if __name__ == '__main__':
    app.run(debug=True)
