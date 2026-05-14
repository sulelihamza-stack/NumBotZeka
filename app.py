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
from duckduckgo_search import DDGS
from groq import Groq

# --------------------------------------------------------------
# GROQ API ANAHTARI
# --------------------------------------------------------------
GROQ_API_KEY = "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"

st.set_page_config(page_title="NumBot - 7. Sınıf Eğitim Asistanı", page_icon="🤖", layout="wide")

# --------------------------------------------------------------
# SİYAH TEMA
# --------------------------------------------------------------
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] { background: #000000 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid #2a2a3e !important; }
.sb-baslik { font-size: 1.2rem; font-weight: 700; padding: 15px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin: 10px; color: white !important; }
.ana-baslik { font-size: 2rem; font-weight: 700; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.mesaj-kullanici { display: flex; justify-content: flex-end; margin: 15px 0; }
.mesaj-kullanici span { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 20px; border-radius: 25px 25px 5px 25px; max-width: 70%; }
.mesaj-asistan { margin: 15px 0; }
.cevap-kutu { background: #1a1a2e; border-radius: 25px 25px 25px 5px; padding: 16px 22px; color: #e0e0e0; border: 1px solid #2a2a3e; }
.kaynak-kart { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 20px; padding: 6px 14px; font-size: 12px; text-decoration: none; margin: 5px; display: inline-block; color: #aaa; }
.kaynak-kart:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.isim-ekran { max-width: 450px; margin: 100px auto; background: #1a1a2e; border-radius: 30px; padding: 40px; text-align: center; border: 1px solid #2a2a3e; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, sana nasıl yardımcı olabilirim?", "👋 Merhaba! NumBot derslerinde sana destek olmak için burada."],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu sormaya ne dersin?", "⭐ Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["😔 Üzgünüm... Birlikte ders çalışırsak belki moralin düzelir.", "💪 Geçer, merak etme!"],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek!"],
    "kim": ["🤖 Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "🧠 NumBot - eğitim asistanın!"],
    "default": ["💭 Ders konusunda bir sorun mu var? Matematik, fen, Türkçe, İngilizce sorabilirsin.", "📖 Bir ders sorusu sormak ister misin?"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber"],
    "nasilsin": ["nasılsın", "iyi misin"],
    "iyi": ["iyiyim", "iyi", "güzel"],
    "kötü": ["kötüyüm", "kötü", "üzgün"],
    "teşekkür": ["teşekkür", "sağ ol"],
    "kim": ["kimsin", "nesin", "adın ne"]
}

EGITIM_ANAHTAR = [
    "tam sayı", "denklem", "oran", "yüzde", "kesir", "açı", "üçgen", "alan",
    "zarf", "zamir", "fiil", "isim", "sıfat", "noktalama", "cümle",
    "fotosentez", "mitoz", "hücre", "dna", "basınç", "elektrik",
    "tarih", "coğrafya", "iklim", "harita", "cumhuriyet",
    "simple present", "past tense", "pronoun", "verb",
    "nedir", "nasıl", "açıkla", "anlat", "çöz", "konu"
]

def mesaj_turu_tespit(mesaj: str) -> str:
    m = mesaj.lower().strip()
    if any(k in m for k in EGITIM_ANAHTAR) or len(m.split()) >= 3:
        return "egitim"
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    return "diyalog:default"

def diyalog_cevap(tur: str) -> str:
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

def konu_basligi_cikar(soru: str) -> str:
    soru_lower = soru.lower()
    if "tam sayı" in soru_lower: return "Tam Sayılar"
    if "zarf" in soru_lower: return "Zarflar (Türkçe)"
    if "denklem" in soru_lower: return "Denklemler"
    if "fotosentez" in soru_lower: return "Fotosentez"
    return soru[:30] + ("..." if len(soru) > 30 else "")

# --------------------------------------------------------------
# SAYFA İÇERİĞİ ÇEKME (GÜÇLÜ)
# --------------------------------------------------------------
def sayfa_metni_al(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        metin = " ".join([el.get_text(" ", strip=True) for el in soup.find_all(["p", "h2", "h3", "li"])])
        return metin[:3000]
    except:
        return ""

# --------------------------------------------------------------
# DUCKDUCKGO ARAMA
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def duckduckgo_ara(sorgu: str, n: int = 6):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(f"{sorgu} 7. sınıf", region="tr-tr", max_results=n))
    except:
        return []

# --------------------------------------------------------------
# TF-IDF FALLBACK (SAĞLAM)
# --------------------------------------------------------------
def tfidf_ozetle(soru: str, metin_parcalari: list) -> str:
    if not metin_parcalari:
        return "Bilgi bulunamadı."
    
    cumleler = []
    for p in metin_parcalari:
        cumleler += re.split(r'(?<=[.!?])\s+', p)
    cumleler = [c.strip() for c in cumleler if len(c.strip()) > 40]
    
    if not cumleler:
        return "Yeterli açıklama yok."
    
    try:
        docs = [soru] + cumleler[:50]
        vec = TfidfVectorizer(stop_words="turkish", max_features=500)
        tfidf = vec.fit_transform(docs)
        sim = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        idx = np.argsort(sim)[::-1][:5]
        secilen = [cumleler[i] for i in idx if sim[i] > 0.1]
        return "\n\n".join(secilen[:4]) if secilen else cumleler[0]
    except:
        return "\n\n".join(cumleler[:4])

# --------------------------------------------------------------
# GROQ CEVAP
# --------------------------------------------------------------
def groq_cevap(soru: str, kaynak_metin: str) -> str:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = """Sen NumBot'sun, 7. sınıf öğrencisine yardım eden eğitim asistanısın.
        Verilen bilgilere göre soruyu cevapla. Anlaşılır Türkçe kullan, madde işaretleri yap.
        "Tam sayılar" matematik konusudur. "Zarflar" Türkçe dilbilgisi konusudur. SAKIN KARIŞTIRMA!"""
        
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem},
                {"role": "user", "content": f"Soru: {soru}\n\nBilgiler:\n{kaynak_metin[:4000]}"}
            ],
            max_tokens=700,
            temperature=0.3
        )
        return yanit.choices[0].message.content.strip()
    except:
        return None

# --------------------------------------------------------------
# ANA CEVAP ÜRETİCİ (KAYNAKLI)
# --------------------------------------------------------------
def cevap_uret(soru: str):
    # 1. DuckDuckGo ara
    arama_sonuclari = duckduckgo_ara(soru, n=6)
    
    if not arama_sonuclari:
        return "🔍 İnternette kaynak bulamadım. Lütfen farklı bir soru sor.", [], None, None
    
    # 2. Özetleri ve sayfa içeriklerini topla
    metin_parcalari = []
    kaynak_listesi = []
    
    for sonuc in arama_sonuclari[:5]:
        if sonuc.get("body"):
            metin_parcalari.append(sonuc["body"])
        if sonuc.get("url") and sonuc.get("title"):
            kaynak_listesi.append({"url": sonuc["url"], "baslik": sonuc["title"]})
            # Sayfa içeriğini de çek (daha kaliteli bilgi)
            sayfa_metni = sayfa_metni_al(sonuc["url"])
            if sayfa_metni:
                metin_parcalari.append(sayfa_metni)
            time.sleep(0.3)
    
    if not metin_parcalari:
        return "Kaynak metin bulunamadı.", [], None, None
    
    ham_metin = "\n\n".join(metin_parcalari)
    
    # 3. Önce Groq'u dene
    cevap = groq_cevap(soru, ham_metin)
    
    # 4. Groq çalışmazsa TF-IDF kullan
    if not cevap:
        cevap = tfidf_ozetle(soru, metin_parcalari)
    
    # 5. YouTube linki
    video_link = f"https://www.youtube.com/results?search_query=7.+sınıf+{soru.replace(' ', '+')}"
    
    return cevap, kaynak_listesi[:4], video_link

# --------------------------------------------------------------
# SOHBET YÖNETİMİ
# --------------------------------------------------------------
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

def yeni_sohbet():
    return {"id": int(time.time()*1000), "baslik": "Yeni Sohbet", "mesajlar": []}

def aktif_sohbet():
    for s in st.session_state.sohbetler:
        if s["id"] == st.session_state.aktif_id:
            return s
    return None

def sohbeti_sil(sid):
    st.session_state.sohbetler = [s for s in st.session_state.sohbetler if s["id"] != sid]
    if st.session_state.aktif_id == sid:
        st.session_state.aktif_id = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
    st.rerun()

# --------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-baslik">💬 Sohbetler</div>', unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        yeni = yeni_sohbet()
        st.session_state.sohbetler.insert(0, yeni)
        st.session_state.aktif_id = yeni["id"]
        st.rerun()
    st.markdown("---")
    for s in st.session_state.sohbetler:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(f"📄 {s['baslik'][:25]}", key=f"sb_{s['id']}"):
                st.session_state.aktif_id = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                sohbeti_sil(s["id"])
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='margin-top:20px;text-align:center'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>🤖 Hoş Geldin!</h2><p>Ben NumBot, sana nasıl hitap edebilirim?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("", placeholder="Adını yaz...", label_visibility="collapsed")
    if st.button("Başlayalım!"):
        if isim.strip():
            st.session_state.kullanici_adi = isim.strip()
            st.session_state.isim_bekleniyor = False
            if not st.session_state.sohbetler:
                yeni = yeni_sohbet()
                st.session_state.sohbetler.append(yeni)
                st.session_state.aktif_id = yeni["id"]
            st.rerun()
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#888;margin-bottom:20px">NumBot | İnternette Araştırır, Kaynak ve Video Sunar</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Yeni sohbet için sol menüdeki ➕ butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "📝 Eğitim" if m.get("tur") == "egitim" else "💬 Sohbet"
            st.markdown(f'<div class="mesaj-asistan"><div style="font-size:11px;color:#888">{tur_yazi}</div><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                html = '<div style="margin-top:10px">'
                for i, k in enumerate(m["kaynaklar"][:3], 1):
                    html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">🔗 Kaynak {i}</a> '
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
            if m.get("video_link"):
                st.markdown(f'<div style="margin-top:10px"><a class="kaynak-kart" href="{m["video_link"]}" target="_blank" style="background:linear-gradient(135deg,#ff6b6b,#ee5a24);color:white">🎬 YouTube\'da Ara</a></div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div style="background:rgba(255,200,100,0.1);border-radius:15px;padding:8px;margin-top:8px;color:#ffd966">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    girdi = st.chat_input(f"{ad}, sorunu yaz...")
    if girdi:
        msg = girdi.strip()
        if msg:
            sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
            if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
                sohbet["baslik"] = konu_basligi_cikar(msg)
            
            tur = mesaj_turu_tespit(msg)
            
            if tur == "egitim":
                st.session_state.disi_sayac = 0
                with st.spinner("🔍 NumBot internette araştırıyor ve kaynak topluyor..."):
                    cevap, kaynaklar, video_link = cevap_uret(msg)
                sohbet["mesajlar"].append({
                    "rol": "asistan", "icerik": cevap,
                    "kaynaklar": kaynaklar, "video_link": video_link, "tur": "egitim"
                })
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice(["💡 Sohbet güzel ama biraz ders sorusu soralım mı?", "📖 Ders dışına çıktık, hadi bir soru sor."])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "diyalog", "uyari": uyari})
            
            st.rerun()
