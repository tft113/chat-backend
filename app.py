import os  # 用于读取环境变量
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)    # すべてのオリジンからのアクセスを許可

# API情報の設定
API_KEY = os.getenv("API_KEY", "")  # あなたのテンセントクラウド DeepSeek API キーに置き換えてください
BASE_URL = "https://api.lkeap.cloud.tencent.com/v1/chat/completions"  # テンセントクラウド DeepSeek API アドレス

@app.route('/generate_dialogue', methods=['POST', 'OPTIONS'])
def generate_dialogue():
    # CORS プリフライトリクエスト (OPTIONS) に対応
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response, 200
    
    # ユーザーが入力したキャラクターとシーンの情報を取得
    data = request.json
    character1 = data.get('character1', 'レッド')
    character2 = data.get('character2', 'ポル')
    scene = data.get('scene', '魔法使いと吸血鬼についての話題を語る')
    personality1 = data.get('personality1', 'ユーモラスな狼男')  
    personality2 = data.get('personality2', '理性的な吸血鬼')  

    # 初期の会話プロンプトを作成
    messages = [
        {
            "role": "user",
            "content": (
                f"以下のキャラクター設定に基づき、カジュアルなチャット形式の会話を生成してください。\n"
                f"【ルール】\n"
                f"1. 各発言は「キャラ名: セリフ」の形式で書く。\n"
                f"2. 1つの発言に複数の文を含めてもよいが、長すぎる場合は短文に分割する。\n"
                f"3. 1人のキャラクターが連続で複数のメッセージを送ることがある。\n"
                f"4. 「？」や「！」などの句読点がある場合、それぞれ独立した発言に分割してもよい。\n"
                f"5. 現代のチャット用語（例：「www」＝笑い、「えっ」＝驚き、絵文字）を適宜使用可能。\n"
                f"6. ユーモアや軽いツッコミを含み、自然な会話になるように。\n"
                f"7. キャラクター同士の関係性（例：親しみ、ツッコミ、議論など）を反映し、適切な長さで終える。\n"
                f"\n"
                f"【キャラクター設定】\n"
                f"1. {character1} - {personality1}\n"
                f"2. {character2} - {personality2}\n"
                f"\n"
                f"【会話シーン】\n"
                f"{scene}\n"
                f"\n"
                f"この設定に基づいて、自然なチャット風の会話を生成してください。"
            )
        }
    ]

    # リクエストパラメータを作成
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-v3",  # 使用するモデルを指定
        "messages": messages,
        "max_tokens": 500,  # 生成される会話の長さを増やす
        "temperature": 0.95  # 生成のランダム性を制御
    }

    try:
        print("Sending request to Tencent API...")  
        print("Request Payload:", json.dumps(payload, indent=2, ensure_ascii=False))  

        response = requests.post(BASE_URL, json=payload, headers=headers)

        # ✅ 让 Render Logs 显示腾讯 API 的 HTTP 状态码和返回内容
        print("Tencent API Response Status Code:", response.status_code)
        print("Tencent API Response:", response.text)  # 这里一定要确保打印 API 的返回信息

        response.raise_for_status()  
        result = response.json()

        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        finish_reason = result.get("choices", [{}])[0].get("finish_reason", "")

        print(f"📌 生成结束状态: {finish_reason}")

        return jsonify({"dialogue": generated_text, "finish_reason": finish_reason})

        # ✅ 确保返回给前端的 JSON 里包含正确的 CORS 头
        api_response = jsonify({"dialogue": generated_text})
        api_response.headers.add("Access-Control-Allow-Origin", "*")
        return api_response

    except requests.exceptions.RequestException as e:
        print("Tencent API Request Failed:", str(e))  
        api_response = jsonify({"error": str(e)})
        api_response.headers.add("Access-Control-Allow-Origin", "*")
        return api_response, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
