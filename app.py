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
        return jsonify({"message": "CORS preflight OK"}), 200
    
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
                f"以下のキャラクター情報に基づいて、自然なマルチターンの会話を生成してください。条件は次の通りです：\n"
                f"1. 会話内容は、現代人がスマホでチャットするスタイルを模倣し、カジュアルで自然にしてください。あまりにフォーマルや丁寧すぎる表現は避けてください。文末の句点を避ける\n"
                f"2. フォーマット要件：各セリフは1行ずつ書く。同じキャラクターが連続して短い文章を複数送ることが可能。\n"
                f"3. 句読点（例：？、！、。）がある場合は、内容を短い文章に分割し、それぞれ独立して送信し、長文を一度に送らないようにする。\n"
                f"4. 会話には現代のチャット用語を含めてもよい。例えば、‘www’は笑い、単独の‘？’は疑問、‘えっ’は驚きを表す。\n"
                f"5. 内容は軽快でユーモラスにし、冗談や軽いツッコミを加えて、現代の若者のチャットスタイルに合わせる。\n"
                f"6. 会話の中には感情の起伏を持たせ、キャラクター同士の関係（例えば親しみ、ツッコミ、議論など）を反映させる。適切な長さで締めくくる。\n"
                f"キャラクター情報：\n"
                f"キャラクター1：{character1}、設定：{personality1}\n"
                f"キャラクター2：{character2}、設定：{personality2}\n"
                f"会話シーン：{scene}\n\n"
                f"上記のルールに基づいて会話を生成してください："
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
        "max_tokens": 300,  # 生成される会話の長さを増やす
        "temperature": 0.95  # 生成のランダム性を制御
    }

    try:
        # リクエストパラメータを出力（デバッグ用）
        print("Request Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

        # リクエストを送信
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()  # APIがエラーを返した場合、例外をスロー
        result = response.json()

        # APIレスポンスの詳細を出力（デバッグ用）
        print("API Response:", json.dumps(result, indent=2, ensure_ascii=False))

        # 生成された会話を取得
        # テンセントクラウドAPIのレスポンス形式に応じて調整
        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # 生成された会話内容を返す
        return jsonify({"dialogue": generated_text})
    except requests.exceptions.RequestException as e:
        # リクエストエラーをキャッチし、エラーメッセージを返す
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
