import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from dotenv import load_dotenv

# 讀取 .env
load_dotenv()

# 初始化
app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 資料庫設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
db = SQLAlchemy(app)

# 建立資料表模型
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    heart_rate = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)
    sleep_hours = db.Column(db.Integer)

# 建表（第一次跑可用，之後可註解）
with app.app_context():
    db.create_all()

# 健康檢查
@app.route('/')
def index():
    return "Nuvora API is running!"

# 新增健康數據
@app.route('/health-data', methods=['POST'])
def add_health_data():
    data = request.get_json()
    new_data = HealthData(
        user_id=data.get('user_id'),
        heart_rate=data.get('heart_rate'),
        water_intake=data.get('water_intake'),
        sleep_hours=data.get('sleep_hours')
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({'message': 'Health data added successfully!'})

# Whisper + GPT 文字轉數據範例
@app.route('/whisper', methods=['POST'])
def whisper_gpt():
    text = request.json.get('text', '')
    prompt = f"""
    使用者說：{text}
    請將此句轉成 JSON，包含：
    - heartRate
    - waterIntake
    - sleepHours
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是能把句子轉成 JSON 格式的健康助理。"},
            {"role": "user", "content": prompt}
        ]
    )
    return jsonify(response.choices[0].message)

if __name__ == '__main__':
    app.run(debug=True)
