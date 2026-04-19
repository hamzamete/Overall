"""
server.py — Gladyatör Arenası Flask API Sunucusu
=================================================
Frontend (index.html) ile GAMSPy backend arasındaki köprü.
POST /api/optimize  →  optimize_gladiators() çağırır, JSON döner.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

# ══════════════════════════════════════════════
# Flask App & CORS
# ══════════════════════════════════════════════
app = Flask(__name__)
CORS(app)  # HTML'den gelen cross-origin istekleri engellenmez


# ══════════════════════════════════════════════════════════════
# BURAYA SENİN GAMSPy FONKSIYONUN GELECEK
# ══════════════════════════════════════════════════════════════
# Aşağıdaki fonksiyonu kendi optimize_gladiators() kodunla değiştir.
# Fonksiyon şu yapıda bir dict döndürmeli:
#   {
#     "soldiers": [ {boy, kilo, yas, yag, silah, konum, ...}, ... ],
#     "total_score": 725.3
#   }
#
# def optimize_gladiators(current_data):
#     ...GAMSPy modeli burada çalışır...
#     return {"soldiers": [...], "total_score": ...}
# ══════════════════════════════════════════════════════════════


def optimize_gladiators(current_data):
    """
    Placeholder — Bunu kendi GAMSPy kodunla değiştir.
    Şu an demo değerler döndürüyor.
    """
    soldiers = current_data.get("soldiers", [])
    total_score = 0

    optimized_soldiers = []
    for s in soldiers:
        # Demo: her askere örnek optimal değerler ata
        opt = {
            "boy": 182,
            "kilo": 97,
            "yas": 26,
            "yag": 15,
            "silah": "Gurz",
            "konum": "Cayir",
            "zirh_bas": "Deri",
            "zirh_govde": "Deri",
            "zirh_pantolon": "Deri",
        }
        optimized_soldiers.append(opt)
        total_score += 250  # Demo skor

    return {
        "soldiers": optimized_soldiers,
        "total_score": round(total_score, 1),
    }


# ══════════════════════════════════════════════
# API ENDPOINT
# ══════════════════════════════════════════════
@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    try:
        # Frontend'den gelen JSON verisini al
        payload = request.json

        # action ve data alanlarını çıkar
        action = payload.get("action", "get_recommendation")
        player_data = payload.get("current_data") or payload.get("data") or payload

        # GAMSPy fonksiyonunu çağır
        result = optimize_gladiators(current_data=player_data)

        # Action'a göre yanıt döndür
        if action == "get_recommendation":
            return jsonify({
                "success": True,
                "soldiers": result["soldiers"],
            })

        elif action == "calculate_score":
            return jsonify({
                "success": True,
                "total_score": result["total_score"],
            })

        else:
            return jsonify({
                "success": True,
                "soldiers": result["soldiers"],
                "total_score": result["total_score"],
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


# ══════════════════════════════════════════════
# SUNUCUYU BAŞLAT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("[*] Gladyator Arenasi API sunucusu baslatiliyor...")
    print("[*] http://localhost:5000/api/optimize")
    app.run(port=5000, debug=True)
