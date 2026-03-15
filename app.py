import json
import os
import secrets
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    api_token_hash = db.Column(db.String(255), nullable=True)


class HealthData(db.Model):
    __tablename__ = "health_data"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    heart_rate = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)


def get_database_url():
    database_url = os.getenv("DATABASE_URL") or "sqlite:///nuvora.db"
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def serialize_health_data(record):
    return {
        "id": record.id,
        "user_id": record.user_id,
        "heart_rate": record.heart_rate,
        "water_intake": record.water_intake,
        "sleep_hours": record.sleep_hours,
    }


def serialize_user(user):
    return {"id": user.id, "username": user.username}


def serialize_auth_response(user, token=None):
    payload = {"user": serialize_user(user)}
    if token:
        payload["token"] = token
        payload["token_type"] = "Bearer"
    return payload


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


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip() or None


def get_current_api_user():
    token = get_bearer_token()
    if not token:
        return None

    for user in User.query.filter(User.api_token_hash.isnot(None)).all():
        if check_password_hash(user.api_token_hash, token):
            return user
    return None


def get_authenticated_user():
    return get_current_api_user() or get_current_user()


def issue_api_token(user):
    raw_token = secrets.token_urlsafe(32)
    user.api_token_hash = generate_password_hash(raw_token)
    db.session.commit()
    return raw_token


def clear_api_token(user):
    user.api_token_hash = None
    db.session.commit()


def login_required(route):
    @wraps(route)
    def wrapped(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        return route(user, *args, **kwargs)

    return wrapped


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
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


def parse_and_optionally_save(text, openai_api_key, user_id=None, save_result=False):
    if not openai_api_key:
        return None, "OPENAI_API_KEY is not configured", 500

    client = OpenAI(api_key=openai_api_key)
    gpt_result = parse_health_text(client, text)

    saved_record = None
    if save_result:
        normalized_payload, error = validate_health_payload(
            {
                "user_id": user_id,
                "heart_rate": gpt_result.get("heartRate"),
                "water_intake": gpt_result.get("waterIntake"),
                "sleep_hours": gpt_result.get("sleepHours"),
            }
        )
        if error:
            return None, error, 400

        saved_record = create_health_data_record(normalized_payload)

    return {
        "input_text": text,
        "gpt_result": gpt_result,
        "saved": bool(saved_record),
        "saved_record": serialize_health_data(saved_record) if saved_record else None,
    }, None, 200


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/status")
    def status():
        return jsonify({"message": "Nuvora API running!"})

    @app.route("/auth/me")
    def auth_me():
        user = get_authenticated_user()
        return jsonify({"authenticated": bool(user), "user": serialize_user(user) if user else None})

    @app.route("/auth/register", methods=["POST"])
    def register():
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "JSON body is required"}), 400

        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        if len(username) < 3:
            return jsonify({"error": "username must be at least 3 characters"}), 400
        if len(password) < 6:
            return jsonify({"error": "password must be at least 6 characters"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "username already exists"}), 409

        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        token = issue_api_token(user)
        return jsonify({"message": "Registered successfully", **serialize_auth_response(user, token)}), 201

    @app.route("/auth/login", methods=["POST"])
    def login():
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "JSON body is required"}), 400

        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "invalid username or password"}), 401

        session["user_id"] = user.id
        token = issue_api_token(user)
        return jsonify({"message": "Logged in successfully", **serialize_auth_response(user, token)})

    @app.route("/auth/logout", methods=["POST"])
    def logout():
        user = get_authenticated_user()
        if user and get_bearer_token():
            clear_api_token(user)
        session.clear()
        return jsonify({"message": "Logged out"})

    @app.route("/health-data", methods=["GET"])
    @login_required
    def list_health_data(current_user):
        records = HealthData.query.filter_by(user_id=current_user.username).order_by(HealthData.id.desc()).all()
        return jsonify({"count": len(records), "items": [serialize_health_data(record) for record in records]})

    @app.route("/health-data", methods=["POST"])
    @login_required
    def add_health_data(current_user):
        payload = request.get_json() or {}
        payload["user_id"] = current_user.username
        normalized_payload, error = validate_health_payload(payload)
        if error:
            return jsonify({"error": error}), 400

        new_data = create_health_data_record(normalized_payload)
        return jsonify({"message": "Health data added successfully", "data": serialize_health_data(new_data)}), 201

    @app.route("/parse-text", methods=["POST"])
    @login_required
    def parse_text(current_user):
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "JSON body is required"}), 400

        input_text = payload.get("text")
        if not input_text:
            return jsonify({"error": "text is required"}), 400

        result, error, status_code = parse_and_optionally_save(
            input_text,
            app.config["OPENAI_API_KEY"],
            user_id=current_user.username,
            save_result=bool(payload.get("save")),
        )
        if error:
            return jsonify({"error": error}), status_code

        return jsonify(result), status_code

    @app.route("/whisper", methods=["POST"])
    @login_required
    def whisper_gpt(current_user):
        audio_file = request.files.get("audio")
        if not audio_file:
            return jsonify({"error": "audio file is required"}), 400

        openai_api_key = app.config["OPENAI_API_KEY"]
        if not openai_api_key:
            return jsonify({"error": "OPENAI_API_KEY is not configured"}), 500

        client = OpenAI(api_key=openai_api_key)
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

        result, error, status_code = parse_and_optionally_save(
            transcript.text,
            openai_api_key,
            user_id=current_user.username,
            save_result=request.form.get("save", "false").lower() == "true",
        )
        if error:
            return jsonify({"error": error}), status_code

        result["whisper_result"] = transcript.text
        return jsonify(result)

    @app.cli.command("seed-local-data")
    def seed_local_data():
        user = User.query.filter_by(username="demo-user").first()
        if not user:
            user = User(
                username="demo-user",
                password_hash=generate_password_hash("demo-pass"),
            )
            db.session.add(user)
            db.session.commit()

        sample = HealthData(user_id=user.username, heart_rate=72, water_intake=1800, sleep_hours=7.5)
        db.session.add(sample)
        db.session.commit()
        print("Seeded demo user and health data.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
