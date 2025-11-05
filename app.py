from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math

app = Flask(__name__)
CORS(app)

# 🔹 본인 REST API 키 입력
KAKAO_API_KEY = "c6d24f0796bfca964b2de3f25ae8a0ee"

def get_distance(origin, destination):
    """카카오 내비 API로 거리(km)와 예상 시간(분) 계산"""
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "origin": origin,         # 예: "126.9784,37.5667"
        "destination": destination,  # 예: "127.0286,37.4979"
        "priority": "RECOMMEND"   # ✅ 추천경로 사용
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # ✅ 응답 정상 처리
        if response.status_code == 200 and "routes" in data:
            route = data["routes"][0]["summary"]
            distance_km = round(route["distance"] / 1000, 1)
            duration_min = math.ceil(route["duration"] / 60)
            return {"distance_km": distance_km, "duration_min": duration_min}
        else:
            return {"error": data.get("msg", "Invalid address")}
    except Exception as e:
        return {"error": str(e)}


@app.route("/")
def home():
    return "🚀 Kakao Distance API 정상 작동 중입니다."


@app.route("/distance", methods=["GET"])
def distance():
    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not origin or not destination:
        return jsonify({"error": "origin과 destination 파라미터가 필요합니다."}), 400

    result = get_distance(origin, destination)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
