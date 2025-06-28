from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# 建議從環境變數讀取
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/whisper', methods=['POST'])
def whisper_gpt():
    data = request.json
    text = data.get('text', '')

    prompt = f"""
    使用者說：「{text}」
    請將此句轉成 JSON，包含：
    - heartRate
    - waterIntake
    - sleepHours
    沒有的值給 null，只要回傳 JSON。
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一個健康數據解析助手"},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    try:
        result = eval(answer) if '{' in answer else {}
    except:
        result = {}

    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
