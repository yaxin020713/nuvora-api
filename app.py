from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# 設定資料庫連線
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 資料表模型
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    heart_rate = db.Column(db.Integer)
    sleep_hour = db.Column(db.Float)      # ✅ 統一名稱
    water_ml = db.Column(db.Integer)      # ✅ 統一名稱
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# 建立資料表（第一次部署時可以用）
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Nuvora API is running!'

@app.route('/health-data', methods=['POST'])
def add_health_data():
    data = request.json
    new_data = HealthData(
        heart_rate=data.get('heart_rate'),
        sleep_hours=data.get('sleep_hours'),
        water_intake=data.get('water_intake')
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({'message': 'Health data stored successfully'}), 201
