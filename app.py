import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

try:
    from duckduckgo_search import DDGS
except ImportError:
    st.error("❌ 'duckduckgo-search' eksik. Terminal: pip install duckduckgo-search")
    st.stop()

try:
    from groq import Groq
except ImportError:
    st.error("❌ 'groq' eksik. Terminal: pip install groq")
    st.stop()

GROQ_API_KEY = "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"

st.set_page_config(page_title="NumBot", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] { background: #000000 !important; }
[data-testid="stSidebar"] { background: #1a1a2e !important; }
.ana-baslik { font-size: 2rem; font-weight: bold; text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.mesaj-kullanici { text-align: right; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px; border-radius: 20px; margin: 5px; }
.mesaj-asistan { background: #1a1a2e; padding: 10px; border-radius: 20px; margin: 5px; color: #e0e0e0; border: 1px solid #333; }
.kaynak-kart { background: #2a2a3e; padding: 5px 10px; border-radius: 15px; text-decoration: none; color: #aaa; font-size: 12px; margin: 3px; display: inline-block; }
.isim-ekran { max-width: 400px; margin: 100px auto; background: #1a1a2e; padding: 40px; border-radius: 30px; text-align: center; }
</style>
""", unsafe_allow_html=True)

DIYALOG = {
    "selam": ["Selam! Ben NumBot, sana nasıl yardımcı olabilirim?", "Merhaba! Derslerinde sana destek olmak için buradayım."],
    "nasilsin": ["İyiyim, teşekkürler! Sen nasılsın?", "Harika hissediyorum!"],
    "iyi": ["Ne güzel! O zaman bir ders sorusu sormaya ne dersin?", "Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["Üzgünüm... Birlikte ders çalışırsak belki neşelenirsin.", "Geçer, merak etme!"],
    "teşekkür": ["Rica ederim! Başka sorun olursa buradayım.", "Ne demek!"],
    "kim": ["Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "NumBot - eğitim asistanın!"],
    "default": ["Ders konusunda bir sorun mu var? Matematik, fen, Türkçe sorabilirsin.", "Bir ders sorusu sormak ister misin?"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey"],
    "nasilsin": ["nasılsın", "iyi misin"],
    "iyi": ["iyiyim", "iyi", "güzel"],
    "kötü": ["kötüyüm", "kötü", "üzgün"],
    "teşekkür": ["teşekkür", "sağ ol"],
    "kim": ["kimsin", "nesin", "adın ne"]
}

EGITIM_KELIMELER = ["nedir", "nasıl", "açıkla", "anlat", "çöz", "matematik", "fen", "türkçe", "denklem", "kesir", "yüzde", "zarf", "zamir", "fiil", "fotosentez", "mitoz"]

def mesaj_turu(m):
    m = m.lower()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if any(k in m for k in EGITIM_KELIMELER) or len(m.split()) >= 3:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur):
    a = tur.split(":")[1] if ":" in tur else "default"
    import random
    return random.choice(DIYALOG.get(a, DIYALOG["default"]))

@st.cache_data(ttl=3600)
def ddg_ara(s):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return list(ddgs.text(s + " 7. sınıf", region="tr-tr", max_results=5))
    except:
        return []

def sayfa_cek(url):
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return " ".join([el.get_text(" ", strip=True) for el in soup.find_all(["p", "h2", "h3"])])[:3000]
    except:
        return ""

def tfidf_ozet(s, metinler):
    if not metinler:
        return "Bilgi yok."
    cumleler = []
    for m in metinler:
        cumleler += re.split(r'(?<=[.!?])\s+', m)
    cumleler = [c.strip() for c in cumleler if len(c.strip()) > 40][:30]
    if not cumleler:
        return "Yeterli açıklama yok."
    try:
        docs = [s] + cumleler
        vec = TfidfVectorizer(stop_words="turkish", max_features=300)
        tfidf = vec.fit_transform(docs)
        sim = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        idx = np.argsort(sim)[::-1][:4]
        return "\n\n".join([cumleler[i] for i in idx if sim[i] > 0.1])
    except:
        return "\n\n".join(cumleler[:4])

def groq_cevap(s, metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"7. sınıf öğrencisine şu soruyu cevapla: {s}\n\nBilgiler:\n{metin[:3000]}"}],
            max_tokens=500,
            temperature=0.4
        )
        return yanit.choices[0].message.content.strip()
    except:
        return None

def cevap_uret(soru):
    sonuc = ddg_ara(soru)
    if not sonuc:
        return "Üzgünüm, internette bulamadım.", [], None
    metinler = []
    kaynaklar = []
    for r in sonuc[:3]:
        if r.get("body"):
            metinler.append(r["body"])
        if r.get("href"):
            kaynaklar.append({"url": r["href"], "baslik": r.get("title", "Kaynak")[:40]})
            sayfa = sayfa_cek(r["href"])
            if sayfa:
                metinler.append(sayfa)
    if not metinler:
        return "İçerik alınamadı.", kaynaklar, None
    ham = "\n\n".join(metinler)
    c = groq_cevap(soru, ham)
    if not c:
        c = tfidf_ozet(soru, metinler)
    video = f"https://www.youtube.com/results?search_query=7.+sınıf+{soru.replace(' ', '+')}"
    return c, kaynaklar[:3], video

DOSYA = "sohbetler.json"

def yukle():
    if os.path.exists(DOSYA):
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def kaydet(data):
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "kullanici" not in st.session_state:
    st.session_state.kullanici = None
if "isim_sor" not in st.session_state:
    st.session_state.isim_sor = True
if "sohbetler" not in st.session_state:
    st.session_state.sohbetler = yukle()
if "aktif" not in st.session_state:
    st.session_state.aktif = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
if "sayac" not in st.session_state:
    st.session_state.sayac = 0

def aktif_sohbet():
    for s in st.session_state.sohbetler:
        if s["id"] == st.session_state.aktif:
            return s
    return None

with st.sidebar:
    st.markdown("### 💬 Sohbetler")
    if st.button("➕ Yeni Sohbet"):
        yeni = {"id": int(time.time()*1000), "baslik": "Yeni Sohbet", "mesajlar": []}
        st.session_state.sohbetler.insert(0, yeni)
        st.session_state.aktif = yeni["id"]
        kaydet(st.session_state.sohbetler)
        st.rerun()
    for s in st.session_state.sohbetler:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(s["baslik"][:20], key=f"sb_{s['id']}"):
                st.session_state.aktif = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                st.session_state.sohbetler = [x for x in st.session_state.sohbetler if x["id"] != s["id"]]
                if st.session_state.aktif == s["id"]:
                    st.session_state.aktif = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
                kaydet(st.session_state.sohbetler)
                st.rerun()

if st.session_state.isim_sor:
    st.markdown('<div class="isim-ekran"><h2>🤖 Hoş Geldin!</h2><p>Adını öğrenebilir miyim?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("", placeholder="Adın...")
    if st.button("Başla"):
        if isim.strip():
            st.session_state.kullanici = isim.strip()
            st.session_state.isim_sor = False
            if not st.session_state.sohbetler:
                st.session_state.sohbetler.append({"id": int(time.time()*1000), "baslik": "Yeni Sohbet", "mesajlar": []})
                st.session_state.aktif = st.session_state.sohbetler[0]["id"]
                kaydet(st.session_state.sohbetler)
            st.rerun()
    st.stop()

ad = st.session_state.kullanici or "Öğrenci"
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()
if sohbet is None:
    st.info("Yeni sohbet için ➕ butonuna tıkla")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici">👤 {m["icerik"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mesaj-asistan">🤖 {m["icerik"]}', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                for k in m["kaynaklar"]:
                    st.markdown(f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">🔗 {k["baslik"]}</a>', unsafe_allow_html=True)
            if m.get("video"):
                st.markdown(f'<a class="kaynak-kart" href="{m["video"]}" target="_blank">🎬 YouTube\'da Ara</a>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'⚠️ {m["uyari"]}')
            st.markdown("</div>", unsafe_allow_html=True)

    girdi = st.chat_input("Sorunu yaz...")
    if girdi:
        msg = girdi.strip()
        sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
        if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
            sohbet["baslik"] = msg[:20]
        
        tur = mesaj_turu(msg)
        if tur == "egitim":
            st.session_state.sayac = 0
            with st.spinner("Araştırılıyor..."):
                c, k, v = cevap_uret(msg)
            sohbet["mesajlar"].append({"rol": "asistan", "icerik": c, "kaynaklar": k, "video": v})
        else:
            st.session_state.sayac += 1
            c = diyalog_cevap(tur)
            u = None
            if st.session_state.sayac >= 3:
                u = "Sohbet güzel ama ders sorusu da sorabilirsin."
                st.session_state.sayac = 0
            sohbet["mesajlar"].append({"rol": "asistan", "icerik": c, "uyari": u})
        
        kaydet(st.session_state.sohbetler)
        st.rerun()
