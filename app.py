from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math
import time

app = Flask(__name__)
CORS(app)

KAKAO_REST_KEY = "c6d24f0796bfca964b2de3f25ae8a0ee"

# 🔹 주소 → 좌표 변환
def get_coordinates(address, retry=2):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    params = {"query": address}

    for _ in range(retry):
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get("documents"):
                x = data["documents"][0]["x"]  # 경도
                y = data["documents"][0]["y"]  # 위도
                return f"{x},{y}"
        time.sleep(0.5)  # 재시도 대기

    return None

# 🔹 좌표 → 거리 계산
def get_distance(origin_coord, dest_coord):
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    params = {
        "origin": origin_coord,
        "destination": dest_coord,
        "priority": "RECOMMEND"
    }

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        return None, None

    try:
        route = res.json()["routes"][0]["summary"]
        distance_km = round(route["distance"] / 1000, 1)
        duration_min = math.ceil(route["duration"] / 60)
        return distance_km, duration_min
    except Exception:
        return None, None


@app.route("/")
def home():
    return "✅ Kakao Distance API 정상 작동 중!"


@app.route("/distance", methods=["GET"])
def distance():
    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not origin or not destination:
        return jsonify({"error": "origin and destination required"}), 400

    # 주소 → 좌표 변환
    origin_coord = get_coordinates(origin)
    dest_coord = get_coordinates(destination)

    if not origin_coord or not dest_coord:
        return jsonify({"error": "Invalid address"}), 400

    # 거리 계산
    distance_km, duration_min = get_distance(origin_coord, dest_coord)

    if distance_km is None:
        return jsonify({"error": "Failed to calculate distance"}), 500

    return jsonify({
        "origin": origin,
        "destination": destination,
        "distance_km": distance_km,
        "duration_min": duration_min
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
