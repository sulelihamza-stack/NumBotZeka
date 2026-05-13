import streamlit as st
import requests
import time
import re
import random
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

st.set_page_config(page_title="7. Sınıf Eğitim Asistanı", page_icon="📚", layout="wide")

# Basit CSS (aynen)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap');
html, body, [data-testid="stAppViewContainer"] { background-color: #ffffff; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
.sb-baslik { font-size: 1.1rem; font-weight: 600; padding: 10px 16px; border-bottom: 1px solid #e0e0e0; text-align: center; }
.ana-baslik { font-size: 1.4rem; font-weight: 600; text-align: center; margin: 20px 0 5px; }
.ana-alt { font-size: 0.85rem; color: #6c757d; text-align: center; margin-bottom: 20px; }
.mesaj-kullanici { display: flex; justify-content: flex-end; margin: 10px 0; }
.mesaj-kullanici span { background: #007bff; color: white; padding: 8px 15px; border-radius: 18px; max-width: 75%; }
.mesaj-asistan { margin: 10px 0; }
.asistan-tur { font-size: 11px; color: #6c757d; border-left: 2px solid #007bff; padding-left: 8px; margin-bottom: 5px; }
.cevap-kutu { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 12px 18px; }
.kaynak-kart { background: #fff; border: 1px solid #dee2e6; border-radius: 6px; padding: 3px 8px; font-size: 12px; text-decoration: none; margin-right: 5px; }
.uyari-kutu { background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; padding: 8px 12px; margin-top: 8px; color: #856404; }
.video-oneri a { background: #f1f1f1; padding: 4px 10px; border-radius: 20px; text-decoration: none; font-size: 13px; }
.isim-ekran { max-width: 400px; margin: 100px auto; background: white; border: 1px solid #dee2e6; border-radius: 20px; padding: 30px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Diyalog sistemleri (kısa)
DIYALOG_KALIPLARI = {
    "selam": ["Selam! Nasılsın? Hangi konuda yardım edebilirim?", "Merhaba! Ders çalışmaya hazır mısın?"],
    "nasilsin": ["İyiyim, teşekkürler! Sen nasılsın?", "Gayet iyiyim! Sana nasıl yardımcı olabilirim?"],
    "iyi": ["Ne güzel! O zaman bir soru sormaya ne dersin?", "Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["Üzgünüm... Birlikte ders çalışırsak belki neşelenirsin.", "Geçer, merak etme! Ders sorusu sormak ister misin?"],
    "teşekkür": ["Rica ederim! Başka sorun olursa buradayım.", "Ne demek!"],
    "günaydın": ["Günaydın! Verimli bir gün geçirmeni dilerim.", "Günaydın! Yeni bilgiler öğrenmeye ne dersin?"],
    "iyi geceler": ["İyi geceler! Yarın görüşürüz.", "İyi geceler! Öğrendiklerini unutma."],
    "kim": ["Ben 7. Sınıf Eğitim Asistanı'yım.", "Yapay zeka asistanıyım, derslerde yardımcı olurum."],
    "ne yapabilirsin": ["Sana 7. sınıf konularını anlatabilirim, sorularını cevaplayabilirim.", "Her ders sorusunu araştırıp cevaplarım."],
    "sıkıldım": ["Hadi bir soru sor, belki ilginç bir şey öğreniriz.", "Sıkılmak normal, ama öğrenmek eğlencelidir. Soru sor!"],
    "default": ["Anlıyorum! Ders konusunda bir sorun mu var?", "Bir ders sorusu sormak ister misin?"]
}
DIYALOG_ANAHTAR = {
    "selam": ["selam","merhaba","hey"], "nasilsin": ["nasılsın","iyi misin"], "iyi": ["iyiyim","iyi","güzel"],
    "kötü": ["kötü","berbat","üzgün"], "teşekkür": ["teşekkür","sağ ol"], "günaydın": ["günaydın","sabah"],
    "iyi geceler": ["iyi geceler","akşam"], "kim": ["kimsin","nesin"], "ne yapabilirsin": ["ne yapabilirsin"],
    "sıkıldım": ["sıkıldım","bıktım"]
}
EGITIM_ANAHTAR = ["nedir","nasıl","ne zaman","açıkla","anlat","formül","hesapla","çöz","konu","ders","matematik","fen","tarih"]

def mesaj_turu_tespit(mesaj: str) -> str:
    m = mesaj.lower()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if any(k in m for k in EGITIM_ANAHTAR) or len(m.split())>=4:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur: str) -> str:
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

# Kaynak güvenilirliği
def guvenilirlik_puani(url: str) -> int:
    u = url.lower()
    if any(d in u for d in [".gov.tr", ".edu.tr", "meb", "eba"]): return 10
    if any(d in u for d in ["wikipedia", "britannica", "khanacademy"]): return 8
    return 1

# Sadece DuckDuckGo arama özetlerini kullan (sayfa içi çekme yok)
@st.cache_data(ttl=3600, show_spinner=False)
def ddg_ara_cached(sorgu: str, n: int = 8):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(sorgu, region="tr-tr", max_results=n))
    except Exception as e:
        st.error(f"Arama hatası: {e}")
        return []

# TF‑IDF özetleme (fallback)
def tfidf_ozetle(soru, metin_parcalari):
    if not metin_parcalari:
        return "İlgili içerik bulunamadı."
    # metin_parcalari her bir arama sonucunun body'si
    cumleler = []
    for p in metin_parcalari:
        cumleler += re.split(r'(?<=[.!?])\s+', p)
    cumleler = [c.strip() for c in cumleler if len(c.strip())>40]
    if not cumleler:
        return "Detaylı bilgi yok."
    docs = [soru] + cumleler
    vec = TfidfVectorizer(stop_words="turkish", max_features=500)
    tfidf = vec.fit_transform(docs)
    sim = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    idx = np.argsort(sim)[::-1][:5]
    secilen = [cumleler[i] for i in idx if sim[i]>0.1]
    return "\n\n".join(secilen[:4]) if secilen else cumleler[0]

# Groq sentez
def groq_sentezle(soru, ham_metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = "Sen 7. sınıf öğrencisine yardım eden bir eğitim asistanısın. Verilen metne göre soruyu cevapla, sade ve anlaşılır Türkçe kullan, 3-5 paragraf veya madde halinde yaz. Kaynak adı yazma."
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem},
                {"role": "user", "content": f"Soru: {soru}\n\nMetin:\n{ham_metin[:4000]}"}
            ],
            max_tokens=600,
            temperature=0.4
        )
        return yanit.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Groq hatası: {e}")
        return None

# Görsel ve video (opsiyonel)
def konu_icin_gorsel(soru):
    try:
        with DDGS() as ddgs:
            res = list(ddgs.images(soru, max_results=1))
            return res[0]["image"] if res else None
    except:
        return None

def konu_icin_video_linki(soru):
    return f"https://www.youtube.com/results?search_query=7.+sınıf+{soru.replace(' ','+')}"

# Ana cevap üretici (sadece arama özetleri)
def cevap_olustur(soru):
    sonuclar = ddg_ara_cached(f"{soru} 7. sınıf", n=8)
    if not sonuclar:
        return "Üzgünüm, internette bir şey bulamadım.", [], None, ""
    # Özet metinleri topla
    ozetler = [r.get("body", "") for r in sonuclar if r.get("body")]
    # Kaynakları hazırla
    kaynaklar = []
    for r in sonuclar[:6]:
        url = r.get("href")
        if url:
            kaynaklar.append({"url": url, "baslik": r.get("title", url), "guven": guvenilirlik_puani(url)})
    kaynaklar.sort(key=lambda x: x["guven"], reverse=True)
    if not ozetler:
        return "Arama sonucu metin yok.", kaynaklar[:5], None, ""
    ham_metin = "\n\n".join(ozetler)
    # Groq dene
    sentez = groq_sentezle(soru, ham_metin)
    if not sentez:
        sentez = tfidf_ozetle(soru, ozetler)
    return sentez, kaynaklar[:5], konu_icin_gorsel(soru), konu_icin_video_linki(soru)

# Session state (JSON yok)
if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = None
if "isim_bekleniyor" not in st.session_state:
    st.session_state.isim_bekleniyor = True
if "sohbetler" not in st.session_state:
    st.session_state.sohbetler = []
if "aktif_id" not in st.session_state:
    st.session_state.aktif_id = None
if "disi_sayac" not in st.session_state:
    st.session_state.disi_sayac = 0

def yeni_sohbet(adi):
    return {"id": int(time.time()*1000), "baslik": adi, "mesajlar": []}

def aktif_sohbet():
    for s in st.session_state.sohbetler:
        if s["id"] == st.session_state.aktif_id:
            return s
    return None

# Sidebar
with st.sidebar:
    st.markdown('<div class="sb-baslik">💬 Sohbetler</div>', unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        yeni = yeni_sohbet("Yeni Sohbet")
        st.session_state.sohbetler.insert(0, yeni)
        st.session_state.aktif_id = yeni["id"]
        st.rerun()
    st.markdown("---")
    for s in st.session_state.sohbetler:
        if st.button(s["baslik"][:30], key=f"sb_{s['id']}"):
            st.session_state.aktif_id = s["id"]
            st.rerun()
    if st.session_state.kullanici_adi:
        st.markdown(f"👤 {st.session_state.kullanici_adi}")

# İsim sorma
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>Hoş Geldin!</h2><p>Adını öğrenebilir miyim?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("Adın:", placeholder="Adını yaz...", label_visibility="collapsed")
    if st.button("Başla"):
        if isim.strip():
            st.session_state.kullanici_adi = isim.strip()
            st.session_state.isim_bekleniyor = False
            if not st.session_state.sohbetler:
                yeni = yeni_sohbet("Yeni Sohbet")
                st.session_state.sohbetler.append(yeni)
                st.session_state.aktif_id = yeni["id"]
            st.rerun()
    st.stop()

# Ana alan
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">7. Sınıf Eğitim Asistanı (Sadece arama özetleri, hızlı ve hafif)</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()
if sohbet is None:
    st.info("Yeni sohbet oluşturmak için sol menüdeki ➕ butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mesaj-asistan"><div class="asistan-tur">{"Cevap" if m.get("tur")=="egitim" else "Sohbet"}</div><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                src_html = '<div style="margin-top:6px">'
                for i, k in enumerate(m["kaynaklar"], 1):
                    src_html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">{i}. {k["baslik"][:40]}</a> '
                src_html += '</div>'
                st.markdown(src_html, unsafe_allow_html=True)
            if m.get("gorsel"):
                st.image(m["gorsel"], width=200)
            if m.get("video_link"):
                st.markdown(f'<div class="video-oneri">🎬 <a href="{m["video_link"]}" target="_blank">YouTube’da ara</a></div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    girdi = st.chat_input(f"Sorunu yaz, {ad}...")
    if girdi:
        msg = girdi.strip()
        if msg:
            sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
            if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
                sohbet["baslik"] = msg[:30] + ("..." if len(msg)>30 else "")
            tur = mesaj_turu_tespit(msg)
            if tur == "egitim":
                st.session_state.disi_sayac = 0
                with st.spinner("Araştırılıyor..."):
                    cevap, kaynaklar, gorsel, vlink = cevap_olustur(msg)
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "kaynaklar": kaynaklar, "tur": "egitim", "gorsel": gorsel, "video_link": vlink})
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice(["Sohbet güzel ama biraz ders sorusu soralım mı?", "Ders dışına çıktık, hadi bir soru sor."])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "diyalog", "uyari": uyari})
            st.rerun()
