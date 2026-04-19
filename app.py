"""
⚔️ Savaşçı Optimizasyonu — Hackathon MVP
Brute-Force vs GAMSPy karşılaştırmalı ekipman optimizasyonu.
Tek dosya: streamlit + gamspy + plotly + math + time
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import math, time, itertools

# ══════════════════════════════════════════════
# 1) SABİTLER
# ══════════════════════════════════════════════
ARMOR_TYPES = {
    "Yok":    {"ag": 0,  "kor": 0,  "hiz_c": 1.00, "stm_c": 1.00},
    "Deri":   {"ag": 3,  "kor": 20, "hiz_c": 0.95, "stm_c": 0.95},
    "Zincir": {"ag": 8,  "kor": 50, "hiz_c": 0.85, "stm_c": 0.85},
    "Demir":  {"ag": 15, "kor": 80, "hiz_c": 0.70, "stm_c": 0.70},
}
ARMOR_KEYS = list(ARMOR_TYPES.keys())

WEAPONS = {
    "Hançer": {"base_spd": 100, "dmg": 15, "w0": 2,  "wL": 0.1},
    "Mızrak": {"base_spd": 80,  "dmg": 25, "w0": 3,  "wL": 0.5},
    "Kılıç":  {"base_spd": 60,  "dmg": 40, "w0": 5,  "wL": 0.8},
    "Gürz":   {"base_spd": 30,  "dmg": 60, "w0": 10, "wL": 2.0},
}
WEAPON_KEYS = list(WEAPONS.keys())

MAPS = {
    "Çayır": {"hiz_b": 1.20, "hasar_b": 1.0, "duzluk": 0,  "desc": "Hız ×1.2"},
    "Orman": {"hiz_b": 1.00, "hasar_b": 1.1, "duzluk": 0,  "desc": "Gizlilik / Hasar ×1.1"},
    "Dağ":   {"hiz_b": 0.90, "hasar_b": 1.0, "duzluk": 8,  "desc": "Stamina cezası, Okçu bonusu"},
}

# ══════════════════════════════════════════════
# 2) BİYOLOJİK HESAPLAMALAR
# ══════════════════════════════════════════════
def calc_bio(yas, bmi, yag):
    """Yaş/BMI/Yağ → P_base, E_base, S_base, W_max"""
    age_f = max(0.5, 1.0 - ((yas - 28) / 25.0) ** 4)
    p_base = 100 * (bmi / 23.0) * max(0.01, (1 - yag) ** 1.5) * age_f
    e_base = 100 * max(0.01, 1 - yag) * max(0.1, (bmi / 23.0) ** 0.5) * age_f
    s_base = 100 * math.exp(-((bmi - 20) / 10.0) ** 2) * max(0.01, (1 - yag) ** 2) * age_f
    w_max = 40 + 60 * (p_base / 100.0)
    return round(p_base, 2), round(e_base, 2), round(s_base, 2), round(w_max, 2)

# ══════════════════════════════════════════════
# 3) STAT HESAPLAMA
# ══════════════════════════════════════════════
def calc_stats(p_base, e_base, s_base, w_max, baslik, govde, pantolon, silah, L, harita):
    """Ekipman + biyoloji → final statlar + verim"""
    ab, ag, ap = ARMOR_TYPES[baslik], ARMOR_TYPES[govde], ARMOR_TYPES[pantolon]
    wp = WEAPONS[silah]
    mp = MAPS[harita]

    w_gear = ab["ag"] + ag["ag"] + ap["ag"] + wp["w0"] + wp["wL"] * L
    toplam_kor = ab["kor"] + ag["kor"] + ap["kor"]
    yuk = w_gear / max(1, w_max)

    # Aşırı yük kontrolü
    if w_gear > 0.9 * w_max:
        return {"hasar": 0, "hiz": 0, "stamina": 0, "koruma": toplam_kor,
                "kapasite": round(100 * (1 - yuk), 1), "verim": 0,
                "w_gear": round(w_gear, 1), "w_max": round(w_max, 1), "overload": True}

    hiz_c = ab["hiz_c"] * ag["hiz_c"] * ap["hiz_c"]
    stm_c = ab["stm_c"] * ag["stm_c"] * ap["stm_c"]

    hasar = (p_base + wp["dmg"] * (L ** 1.2)) * mp["hasar_b"]
    hiz = max(0, s_base * hiz_c * max(0.1, 1 - yuk) * mp["hiz_b"])
    stamina = max(0, e_base * stm_c * max(0.1, 1 - yuk) ** 1.5 - mp["duzluk"])
    kapasite = round(100 * max(0, 1 - yuk), 1)

    verim = 0.35 * hasar + 0.25 * hiz + 0.20 * stamina + 0.20 * toplam_kor
    return {"hasar": round(hasar, 1), "hiz": round(hiz, 1), "stamina": round(stamina, 1),
            "koruma": toplam_kor, "kapasite": kapasite, "verim": round(verim, 1),
            "w_gear": round(w_gear, 1), "w_max": round(w_max, 1), "overload": False}

# ══════════════════════════════════════════════
# 4) BRUTE-FORCE SİMÜLASYONU (görsel)
# ══════════════════════════════════════════════
def brute_force_sim(placeholder):
    """Sahte brute-force animasyonu — 2.5 saniye sürer."""
    placeholder.warning("🤖 **Bot (Brute-Force)** milyonlarca ekipman varyasyonunu tarıyor...")
    bar = placeholder.progress(0, text="Taranıyor...")
    count_display = placeholder.empty()
    total_fake = 2_500_000
    steps = 25
    for i in range(1, steps + 1):
        time.sleep(0.1)
        n = int(total_fake * i / steps)
        bar.progress(i / steps, text=f"Taranan: {n:,} kombinasyon")
        count_display.code(f"Denenen: {n:,} / {total_fake:,}")
    bar.progress(1.0, text="")
    count_display.empty()
    placeholder.error("⏰ **Zaman Aşımı!** Kaba kuvvet 2.5M kombinasyonu taradı ama optimal çözümü bulamadı.")

# ══════════════════════════════════════════════
# 5) GAMSPy OPTİMİZASYONU
# ══════════════════════════════════════════════
def gamspy_optimize(p_base, e_base, s_base, w_max, harita):
    """
    Sabit biyoloji ile en iyi ekipman kombinasyonunu bulur.
    Her combo için optimal L'yi GAMSPy NLP ile çözer.
    """
    import gamspy as gp
    mp = MAPS[harita]
    best = None

    for bas_k, gov_k, pan_k, sil_k in itertools.product(ARMOR_KEYS, ARMOR_KEYS, ARMOR_KEYS, WEAPON_KEYS):
        ab, ag, ap = ARMOR_TYPES[bas_k], ARMOR_TYPES[gov_k], ARMOR_TYPES[pan_k]
        wp = WEAPONS[sil_k]
        armor_ag = ab["ag"] + ag["ag"] + ap["ag"]
        toplam_kor = ab["kor"] + ag["kor"] + ap["kor"]
        hiz_c = ab["hiz_c"] * ag["hiz_c"] * ap["hiz_c"]
        stm_c = ab["stm_c"] * ag["stm_c"] * ap["stm_c"]

        # Minimum silah ağırlığı bile sığmıyorsa atla
        min_w = armor_ag + wp["w0"] + wp["wL"] * 1.0
        if min_w > 0.85 * w_max:
            continue

        # GAMSPy NLP: sadece L'yi optimize et
        m = gp.Container()
        L = gp.Variable(m, name="L", type="positive")
        L.lo[...] = 1.0
        L.up[...] = 2.0
        # L üst sınırı: ağırlık kısıtı
        max_L_by_weight = (0.85 * w_max - armor_ag - wp["w0"]) / max(0.01, wp["wL"])
        L.up[...] = min(2.0, max(1.0, max_L_by_weight))

        w_gear = gp.Variable(m, name="w_gear", type="positive")
        yuk = gp.Variable(m, name="yuk", type="positive")
        hasar_v = gp.Variable(m, name="hasar_v", type="positive")
        hiz_v = gp.Variable(m, name="hiz_v", type="positive")
        stam_v = gp.Variable(m, name="stam_v", type="free")
        verim = gp.Variable(m, name="verim", type="free")

        eq1 = gp.Equation(m, name="eq1")
        eq1[...] = w_gear == armor_ag + wp["w0"] + wp["wL"] * L
        eq2 = gp.Equation(m, name="eq2")
        eq2[...] = yuk == w_gear / w_max
        eq3 = gp.Equation(m, name="eq3")
        eq3[...] = w_gear <= 0.85 * w_max
        eq4 = gp.Equation(m, name="eq4")
        eq4[...] = hasar_v == (p_base + wp["dmg"] * L * L * 0.5 + wp["dmg"] * L * 0.5) * mp["hasar_b"]
        eq5 = gp.Equation(m, name="eq5")
        eq5[...] = hiz_v <= s_base * hiz_c * (1 - yuk) * mp["hiz_b"]
        eq6 = gp.Equation(m, name="eq6")
        eq6[...] = stam_v <= e_base * stm_c * (1 - yuk) * (1 - yuk) - mp["duzluk"]
        eq7 = gp.Equation(m, name="eq7")
        eq7[...] = verim == 0.35 * hasar_v + 0.25 * hiz_v + 0.20 * stam_v + 0.20 * toplam_kor

        model = gp.Model(m, name="opt", equations=m.getEquations(),
                         problem="NLP", sense=gp.Sense.MAX, objective=verim)
        try:
            model.solve()
            v = verim.records["level"].iloc[0]
            opt_L = L.records["level"].iloc[0]
        except Exception:
            continue

        if best is None or v > best["verim_raw"]:
            best = {"baslik": bas_k, "govde": gov_k, "pantolon": pan_k,
                    "silah": sil_k, "L": round(opt_L, 2), "verim_raw": v}

    if best is None:
        return None

    # Python'da kesin stat hesapla
    stats = calc_stats(p_base, e_base, s_base, w_max,
                       best["baslik"], best["govde"], best["pantolon"],
                       best["silah"], best["L"], harita)
    best["stats"] = stats
    return best

# ══════════════════════════════════════════════
# 6) RADAR GRAFİĞİ
# ══════════════════════════════════════════════
def draw_radar(player, bot):
    cats = ["Hasar", "Hız", "Stamina", "Koruma", "Kapasite"]
    keys = ["hasar", "hiz", "stamina", "koruma", "kapasite"]
    df = pd.DataFrame([
        *[{"Kim": "Senin Savaşçın", "Stat": c, "Değer": player[k]} for c, k in zip(cats, keys)],
        *[{"Kim": "GAMSPy Optimal", "Stat": c, "Değer": bot[k]} for c, k in zip(cats, keys)],
    ])
    fig = px.line_polar(df, r="Değer", theta="Stat", color="Kim", line_close=True,
                        color_discrete_map={"Senin Savaşçın": "#3b82f6", "GAMSPy Optimal": "#ef4444"})
    fig.update_traces(fill="toself", opacity=0.6)
    fig.update_layout(
        polar=dict(bgcolor="rgba(15,23,42,0.8)",
                   radialaxis=dict(gridcolor="rgba(148,163,184,0.2)", tickfont=dict(color="#94a3b8")),
                   angularaxis=dict(gridcolor="rgba(148,163,184,0.2)", tickfont=dict(color="#e2e8f0", size=12))),
        legend=dict(font=dict(color="#e2e8f0"), bgcolor="rgba(15,23,42,0.5)"),
        paper_bgcolor="rgba(0,0,0,0)", height=440, margin=dict(t=40, b=40))
    return fig

# ══════════════════════════════════════════════
# 7) TİP SİSTEMİ
# ══════════════════════════════════════════════
def generate_tip(player_equip, bot):
    """Oyuncuya ekipman önerisi üretir."""
    if bot is None:
        return "⚠️ Optimizasyon sonucu bulunamadı."
    tips = []
    if bot["baslik"] != player_equip["baslik"] or bot["govde"] != player_equip["govde"] or bot["pantolon"] != player_equip["pantolon"]:
        tips.append(f"🛡️ Zırh değişikliği: **{bot['baslik']}/{bot['govde']}/{bot['pantolon']}** ile daha dengeli olursun.")
    if bot["silah"] != player_equip["silah"]:
        tips.append(f"⚔️ **{bot['silah']}** silahına geçmek verimini artırır.")
    if abs(bot["L"] - player_equip["L"]) > 0.15:
        tips.append(f"📏 Silah uzunluk çarpanını **{bot['L']}**'e ayarla.")
    delta = bot["stats"]["verim"] - player_equip["verim"]
    if delta > 0:
        pct = round(delta / max(1, player_equip["verim"]) * 100, 1)
        tips.append(f"📊 Optimal ekipmanla verimin **%{pct}** daha yüksek olurdu!")
    return "\n\n".join(tips) if tips else "✅ Ekipman seçimin zaten çok iyi!"

# ══════════════════════════════════════════════
# 8) CSS
# ══════════════════════════════════════════════
def apply_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    .stApp {background:linear-gradient(135deg,#0f172a,#1e1b4b,#0f172a);font-family:'Inter',sans-serif;}
    h1,h2,h3{font-family:'Inter',sans-serif!important;color:#f1f5f9!important;}
    [data-testid="stMetric"]{background:linear-gradient(135deg,rgba(30,41,59,.8),rgba(51,65,85,.6));
        border:1px solid rgba(148,163,184,.2);border-radius:12px;padding:12px;}
    [data-testid="stMetric"] label{color:#94a3b8!important;}
    [data-testid="stMetric"] [data-testid="stMetricValue"]{color:#e2e8f0!important;font-weight:700!important;}
    .stButton>button{background:linear-gradient(135deg,#7c3aed,#2563eb)!important;color:white!important;
        border:none!important;border-radius:12px!important;padding:14px!important;font-weight:700!important;
        font-size:16px!important;transition:.3s!important;}
    .stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(124,58,237,.4)!important;}
    section[data-testid="stSidebar"]{background:linear-gradient(180deg,#1e1b4b,#0f172a);}
    section[data-testid="stSidebar"] label{color:#cbd5e1!important;font-weight:600!important;}
    </style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 9) MAIN
# ══════════════════════════════════════════════
def main():
    st.set_page_config(page_title="⚔️ Savaşçı Optimizasyonu", page_icon="⚔️", layout="wide")
    apply_css()

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("## ⚔️ Savaşçı Oluştur")
        st.markdown("### 📏 Fiziksel")
        yas = st.slider("Yaş", 15, 70, 28)
        bmi = st.slider("BMI", 16.0, 40.0, 23.0, 0.5)
        yag = st.slider("Yağ Oranı (%)", 10, 90, 15)
        yag_f = yag / 100.0

        st.markdown("### 🛡️ Zırh")
        baslik = st.selectbox("Başlık", ARMOR_KEYS, index=1)
        govde = st.selectbox("Gövde", ARMOR_KEYS, index=2)
        pantolon = st.selectbox("Pantolon", ARMOR_KEYS, index=1)

        st.markdown("### ⚔️ Silah")
        silah = st.selectbox("Silah Tipi", WEAPON_KEYS, index=2)
        L = st.slider("Uzunluk / Ağırlık Çarpanı (L)", 1.0, 2.0, 1.3, 0.1)

        st.markdown("### 🗺️ Harita")
        harita = st.selectbox("Arena", list(MAPS.keys()),
                              format_func=lambda x: f"{x} — {MAPS[x]['desc']}")

        st.markdown("---")
        btn = st.button("⚔️ Savaşa Başla!", use_container_width=True)

    # ── BAŞLIK ──
    st.markdown("""<div style='text-align:center;padding:8px 0 20px'>
        <h1 style='font-size:2.3rem;font-weight:900;
            background:linear-gradient(135deg,#a78bfa,#60a5fa,#34d399);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            ⚔️ Savaşçı Optimizasyonu</h1>
        <p style='color:#94a3b8;'>Brute-Force vs GAMSPy — Aynı vücutla en iyi ekipmanı bul!</p>
    </div>""", unsafe_allow_html=True)

    if not btn:
        st.info("👈 Sol panelden savaşçını oluştur ve **Savaşa Başla** butonuna bas!")
        return

    # ── Biyoloji ──
    p_base, e_base, s_base, w_max = calc_bio(yas, bmi, yag_f)

    col_bio = st.columns(4)
    col_bio[0].metric("💪 Güç (P_base)", f"{p_base:.1f}")
    col_bio[1].metric("🫀 Dayanıklılık", f"{e_base:.1f}")
    col_bio[2].metric("💨 Çeviklik", f"{s_base:.1f}")
    col_bio[3].metric("🏋️ Kapasite (kg)", f"{w_max:.1f}")

    # ── Oyuncu Statları ──
    player = calc_stats(p_base, e_base, s_base, w_max, baslik, govde, pantolon, silah, L, harita)

    st.markdown("### 📊 Senin Savaşçın")
    if player["overload"]:
        st.error(f"🚫 **AŞIRI YÜK!** Ekipman: {player['w_gear']}kg > %90 Kapasite ({0.9*w_max:.1f}kg) — Hareket edemiyorsun!")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("⚔️ Hasar", f"{player['hasar']:.0f}")
        c2.metric("💨 Hız", f"{player['hiz']:.0f}")
        c3.metric("❤️ Stamina", f"{player['stamina']:.0f}")
        c4.metric("🛡️ Koruma", f"{player['koruma']}")
        c5.metric("⭐ Verim", f"{player['verim']:.0f}")

    st.markdown("---")

    # ── Brute-Force Simülasyonu ──
    st.markdown("### 🤖 Aşama 1: Brute-Force Denemesi")
    bf_area = st.container()
    with bf_area:
        brute_force_sim(st.empty())

    # ── GAMSPy Optimizasyonu ──
    st.markdown("### 🔮 Aşama 2: GAMSPy Optimizasyonu")
    with st.spinner("GAMSPy optimal ekipmanı hesaplıyor..."):
        t0 = time.time()
        bot = gamspy_optimize(p_base, e_base, s_base, w_max, harita)
        dt = time.time() - t0

    if bot is None:
        st.error("Hiçbir ekipman kombinasyonu taşıma kapasitesine sığmıyor!")
        return

    st.success(f"✅ GAMSPy optimum çözümü **{dt:.1f} saniyede** buldu!")
    bot_s = bot["stats"]

    st.markdown(f"**Optimal Ekipman:** 🛡️ {bot['baslik']}/{bot['govde']}/{bot['pantolon']} — "
                f"⚔️ {bot['silah']} (L={bot['L']})")

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("⚔️ Hasar", f"{bot_s['hasar']:.0f}")
    d2.metric("💨 Hız", f"{bot_s['hiz']:.0f}")
    d3.metric("❤️ Stamina", f"{bot_s['stamina']:.0f}")
    d4.metric("🛡️ Koruma", f"{bot_s['koruma']}")
    d5.metric("⭐ Verim", f"{bot_s['verim']:.0f}")

    # ── Radar Grafiği ──
    st.markdown("### 🕸️ Karşılaştırma Radarı")
    fig = draw_radar(player, bot_s)
    st.plotly_chart(fig, use_container_width=True)

    # ── Tip Sistemi ──
    st.markdown("### 💡 Strateji Önerisi")
    player_equip = {"baslik": baslik, "govde": govde, "pantolon": pantolon,
                    "silah": silah, "L": L, "verim": player["verim"]}
    tip = generate_tip(player_equip, bot)
    st.info(tip)


if __name__ == "__main__":
    main()
