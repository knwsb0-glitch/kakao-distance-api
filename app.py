from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math

app = Flask(__name__)
CORS(app)  # 🔹 CORS 허용 (GPTs나 외부에서 API 호출 가능)

KAKAO_API_KEY = "c6d24f0796bfca964b2de3f25ae8a0ee"

def get_distance(origin, destination):
    """카카오 지도 API로 거리(km)와 예상 시간(분)을 계산"""
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    params = {
        "origin": origin,
        "destination": destination
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    try:
        distance_m = data["routes"][0]["summary"]["distance"]
        duration_s = data["routes"][0]["summary"]["duration"]
        return {
            "distance_km": round(distance_m / 1000, 1),
            "duration_min": math.ceil(duration_s / 60)
        }
    except Exception:
        return None


@app.route("/")
def home():
    return "🚛 Kakao Distance API 서버 정상 작동 중!"


@app.route("/distance", methods=["GET"])
def distance():
    """예시 요청: /distance?origin=127.123,37.123&destination=127.456,37.456"""
    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not origin or not destination:
        return jsonify({"error": "origin과 destination 파라미터가 필요합니다."}), 400

    result = get_distance(origin, destination)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "거리 계산 실패"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
