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
[data-testid="stSidebar"] { background: #1a1a2e !important; border-right: 1px solid #2a2a3e !important; }
.ana-baslik { font-size: 2rem; font-weight: bold; text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 20px 0 5px; }
.mesaj-kullanici { text-align: right; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px 15px; border-radius: 20px; margin: 10px 0; display: inline-block; float: right; clear: both; }
.mesaj-asistan { background: #1a1a2e; padding: 12px 18px; border-radius: 20px; margin: 10px 0; color: #e0e0e0; border: 1px solid #2a2a3e; }
.kaynak-kart { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 20px; padding: 5px 12px; font-size: 12px; text-decoration: none; margin: 3px; display: inline-block; color: #aaa; }
.kaynak-kart:hover { background: #667eea; color: white; }
.isim-ekran { max-width: 400px; margin: 100px auto; background: #1a1a2e; padding: 40px; border-radius: 30px; text-align: center; border: 1px solid #2a2a3e; }
[data-testid="stChatInput"] { background: #1a1a2e !important; border-color: #2a2a3e !important; }
</style>
""", unsafe_allow_html=True)

# DİYALOG SİSTEMİ
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, 7. sınıf derslerinde sana yardımcı olabilirim.", "👋 Merhaba! Ders çalışmaya hazır mısın?"],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu soralım.", "⭐ Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["😔 Üzgünüm... Birlikte çalışırsak daha iyi hissedersin.", "💪 Geçer, merak etme!"],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek!"],
    "kim": ["🤖 Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "🧠 NumBot - eğitim asistanın!"],
    "default": ["📚 Ders sorusu sormak ister misin? Matematik, Fen, Türkçe...", "🎯 Bir konuyu sana anlatabilirim, hangisi?"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber"],
    "nasilsin": ["nasılsın", "iyi misin"],
    "iyi": ["iyiyim", "iyi", "güzel"],
    "kötü": ["kötüyüm", "kötü", "üzgün"],
    "teşekkür": ["teşekkür", "sağ ol"],
    "kim": ["kimsin", "nesin", "adın ne"]
}

EGITIM_KELIMELER = ["nedir", "nasıl", "açıkla", "anlat", "çöz", "öğret", "matematik", "fen", "türkçe", "ingilizce", "sosyal", "tarih", "coğrafya", "denklem", "kesir", "yüzde", "oran", "zarf", "zamir", "fiil", "isim", "sıfat", "fotosentez", "mitoz", "hücre", "dna", "basınç", "elektrik"]

def mesaj_turu(mesaj):
    m = mesaj.lower().strip()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if any(k in m for k in EGITIM_KELIMELER) or len(m.split()) >= 3:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur):
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

# GÜVENİLİR KAYNAK FİLTRESİ
GUVENILIR_SITELER = ["meb", "eba.gov", "derslig", "okulistik", "morpakampüs", "vitamineba", "khanacademy", "tr.wikipedia", "tdk", "tdk.gov"]

def kaynak_guvenilir_mi(url):
    url_lower = url.lower()
    for site in GUVENILIR_SITELER:
        if site in url_lower:
            return True
    return False

# ARAMA
@st.cache_data(ttl=3600, show_spinner=False)
def ddg_ara(sorgu):
    # Daha spesifik arama sorgusu
    arama_sorgusu = f"{sorgu} 7.sınıf konu anlatımı"
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(arama_sorgusu, region="tr-tr", max_results=8))
    except:
        return []

def sayfa_cek(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=10, headers=headers)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        # Ana içerik etiketlerini bul
        metin = ""
        for etiket in ["article", "main", "div class='content'", "div class='lesson'", "p", "h2", "h3"]:
            for el in soup.find_all(etiket.split()[0] if " " in etiket else etiket):
                metin += el.get_text(" ", strip=True) + " "
        
        if not metin:
            metin = " ".join([el.get_text(" ", strip=True) for el in soup.find_all(["p", "h2", "h3", "li"])])
        
        return metin[:4000]
    except:
        return ""

def tfidf_ozet(soru, metinler):
    if not metinler:
        return "Bilgi bulunamadı."
    
    cumleler = []
    for m in metinler:
        cumleler += re.split(r'(?<=[.!?])\s+', m)
    cumleler = [c.strip() for c in cumleler if len(c.strip()) > 40 and not any(x in c for x in ["reklam", "cookie", "gizlilik", "copyright", "©"])]
    
    if not cumleler:
        return "Yeterli açıklama bulunamadı."
    
    try:
        docs = [soru] + cumleler[:50]
        vec = TfidfVectorizer(stop_words="turkish", max_features=400)
        tfidf = vec.fit_transform(docs)
        sim = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        idx = np.argsort(sim)[::-1][:6]
        secilen = [cumleler[i] for i in idx if sim[i] > 0.1]
        return "\n\n".join(secilen[:5]) if secilen else cumleler[0]
    except:
        return "\n\n".join(cumleler[:5])

def groq_cevap(soru, metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = """Sen 7. sınıf öğrencilerine ders anlatan bir eğitim asistanısın.
        Verilen metne göre soruyu cevapla.
        Kurallar:
        - MEB müfredatına uygun ol
        - 7. sınıf seviyesinde anlaşılır Türkçe kullan
        - Örnekler ver
        - Madde işaretleri kullan
        - Kaynak ismi veya site adı YAZMA"""
        
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem},
                {"role": "user", "content": f"Soru: {soru}\n\nDers notları:\n{metin[:4000]}"}
            ],
            max_tokens=600,
            temperature=0.3
        )
        return yanit.choices[0].message.content.strip()
    except Exception as e:
        return None

def cevap_uret(soru):
    sonuclar = ddg_ara(soru)
    
    if not sonuclar:
        return "Üzgünüm, bu konuda kaynak bulamadım. Lütfen farklı bir soru sor.", [], None
    
    # Önce güvenilir kaynakları filtrele
    guvenilir_sonuclar = [s for s in sonuclar if s.get("href") and kaynak_guvenilir_mi(s["href"])]
    if guvenilir_sonuclar:
        sonuclar = guvenilir_sonuclar + [s for s in sonuclar if s not in guvenilir_sonuclar]
    
    metinler = []
    kaynaklar = []
    
    for sonuc in sonuclar[:5]:
        if sonuc.get("body"):
            metinler.append(sonuc["body"])
        if sonuc.get("href") and sonuc.get("title"):
            baslik = sonuc["title"][:50]
            # Güvenilir kaynaklara rozet ekle
            if kaynak_guvenilir_mi(sonuc["href"]):
                baslik = "🛡️ " + baslik
            kaynaklar.append({"url": sonuc["href"], "baslik": baslik})
            
            sayfa = sayfa_cek(sonuc["href"])
            if sayfa:
                metinler.append(sayfa)
            time.sleep(0.2)
    
    if not metinler:
        return "İçerik alınamadı.", kaynaklar[:4], None
    
    ham = "\n\n".join(metinler)
    cevap = groq_cevap(soru, ham)
    if not cevap:
        cevap = tfidf_ozet(soru, metinler)
    
    video_link = f"https://www.youtube.com/results?search_query={soru.replace(' ', '+')}+7+sınıf+konu+anlatımı"
    
    return cevap, kaynaklar[:4], video_link

# SOHBET YÖNETİMİ
SOHBET_DOSYA = "sohbetler.json"

def yukle():
    if os.path.exists(SOHBET_DOSYA):
        with open(SOHBET_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def kaydet(sohbetler):
    with open(SOHBET_DOSYA, "w", encoding="utf-8") as f:
        json.dump(sohbetler, f, ensure_ascii=False, indent=2)

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

def yeni_sohbet():
    return {"id": int(time.time()*1000), "baslik": "Yeni Sohbet", "mesajlar": []}

# SIDEBAR
with st.sidebar:
    st.markdown("### 💬 Sohbetler")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        yeni = yeni_sohbet()
        st.session_state.sohbetler.insert(0, yeni)
        st.session_state.aktif = yeni["id"]
        kaydet(st.session_state.sohbetler)
        st.rerun()
    
    st.markdown("---")
    for s in st.session_state.sohbetler:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(s["baslik"][:25], key=f"sb_{s['id']}"):
                st.session_state.aktif = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                st.session_state.sohbetler = [x for x in st.session_state.sohbetler if x["id"] != s["id"]]
                if st.session_state.aktif == s["id"]:
                    st.session_state.aktif = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
                kaydet(st.session_state.sohbetler)
                st.rerun()
    
    st.markdown("---")
    st.caption("🔍 Güvenilir kaynaklar: MEB, EBA, Derslig, Khan Academy")
    if st.session_state.kullanici:
        st.markdown(f"👤 {st.session_state.kullanici}")

# İSİM SORMA
if st.session_state.isim_sor:
    st.markdown('<div class="isim-ekran"><h2>🤖 Hoş Geldin!</h2><p>Ben NumBot, adını öğrenebilir miyim?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("", placeholder="Adını yaz...", label_visibility="collapsed")
    if st.button("Başlayalım!"):
        if isim.strip():
            st.session_state.kullanici = isim.strip()
            st.session_state.isim_sor = False
            if not st.session_state.sohbetler:
                st.session_state.sohbetler.append(yeni_sohbet())
                st.session_state.aktif = st.session_state.sohbetler[0]["id"]
                kaydet(st.session_state.sohbetler)
            st.rerun()
    st.stop()

# ANA ALAN
ad = st.session_state.kullanici or "Öğrenci"
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#888;margin-bottom:20px">NumBot | MEB Müfredatına Uygun | Güvenilir Kaynaklar</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()
if sohbet is None:
    st.info("💡 Yeni sohbet için sol menüdeki ➕ butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div style="text-align:right; margin:10px 0"><div class="mesaj-kullanici">👤 {m["icerik"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mesaj-asistan">🤖 {m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                html = '<div style="margin-top:10px">'
                for k in m["kaynaklar"][:3]:
                    html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">🔗 {k["baslik"]}</a> '
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
            if m.get("video"):
                st.markdown(f'<a class="kaynak-kart" href="{m["video"]}" target="_blank" style="background:#ff6b6b;color:white">🎬 YouTube\'da Ara</a>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div style="background:rgba(255,200,100,0.1);border-radius:10px;padding:8px;margin-top:8px;color:#ffd966">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
    
    girdi = st.chat_input(f"{ad}, ders sorusu sorabilirsin...")
    if girdi:
        msg = girdi.strip()
        sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
        
        if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
            sohbet["baslik"] = msg[:25]
        
        tur = mesaj_turu(msg)
        
        if tur == "egitim":
            st.session_state.sayac = 0
            with st.spinner("📚 Güvenilir kaynaklardan araştırılıyor..."):
                cevap, kaynaklar, video = cevap_uret(msg)
            sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "kaynaklar": kaynaklar, "video": video})
        else:
            st.session_state.sayac += 1
            cevap = diyalog_cevap(tur)
            uyari = None
            if st.session_state.sayac >= 3:
                uyari = "💡 Sohbet güzel ama ders sorusu da sorabilirsin."
                st.session_state.sayac = 0
            sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "uyari": uyari})
        
        kaydet(st.session_state.sohbetler)
        st.rerun()
