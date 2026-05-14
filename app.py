import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import json
import os
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

st.set_page_config(page_title="NumBot - 7. Sınıf Eğitim Asistanı", page_icon="🤖", layout="wide")

# --------------------------------------------------------------
# SİYAH TEMA
# --------------------------------------------------------------
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] { background: #000000 !important; }
[data-testid="stSidebar"] { background: #1a1a2e !important; border-right: 1px solid #2a2a3e !important; }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.sb-baslik { font-size: 1.2rem; font-weight: 700; text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 12px; margin: 10px; color: white; }
.ana-baslik { font-size: 2rem; font-weight: 700; text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 20px 0 5px; }
.ana-alt { font-size: 0.9rem; color: #888; text-align: center; margin-bottom: 20px; }
.mesaj-kullanici { display: flex; justify-content: flex-end; margin: 10px 0; }
.mesaj-kullanici span { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px 18px; border-radius: 20px; max-width: 80%; }
.mesaj-asistan { margin: 10px 0; }
.cevap-kutu { background: #1a1a2e; border-radius: 20px; padding: 15px 20px; color: #e0e0e0; border: 1px solid #2a2a3e; line-height: 1.6; }
.kaynak-kart { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 15px; padding: 4px 12px; font-size: 12px; text-decoration: none; margin: 3px; display: inline-block; color: #aaa; }
.kaynak-kart:hover { background: #667eea; color: white; }
.isim-ekran { max-width: 400px; margin: 100px auto; background: #1a1a2e; border-radius: 30px; padding: 40px; text-align: center; border: 1px solid #2a2a3e; }
[data-testid="stChatInput"] { background: #1a1a2e !important; border-color: #2a2a3e !important; color: white !important; }
.video-oneri a { background: #ff6b6b; padding: 6px 14px; border-radius: 20px; text-decoration: none; font-size: 12px; color: white; display: inline-block; margin-top: 10px; }
.uyari-kutu { background: rgba(255,200,100,0.1); border-radius: 10px; padding: 8px; margin-top: 8px; color: #ffd966; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, 7. sınıf derslerinde sana yardımcı olabilirim.", "👋 Merhaba! Ders çalışmaya hazır mısın?"],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu soralım.", "⭐ Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["😔 Üzgünüm... Birlikte çalışırsak daha iyi hissedersin.", "💪 Geçer, merak etme!"],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek!"],
    "günaydın": ["🌅 Günaydın! Verimli bir gün geçirmeni dilerim.", "☀️ Günaydın! Yeni bilgiler öğrenmeye hazır mısın?"],
    "iyi geceler": ["🌙 İyi geceler! Yarın görüşürüz.", "⭐ İyi geceler! Öğrendiklerini tekrar etmeyi unutma."],
    "kim": ["🤖 Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "🧠 NumBot - eğitim asistanın!"],
    "ne yapabilirsin": ["🔍 Sana 7. sınıf konularını anlatabilirim! Matematik, fen, Türkçe, İngilizce sorularını cevaplarım.", "📚 Her ders sorusunu internette araştırıp cevaplarım."],
    "sıkıldım": ["😊 Sıkılmak normal! Hadi bir soru sor, belki ilginç bir şey keşfederiz.", "🎮 Küçük bir soruyla başlayalım!"],
    "default": ["💭 Ders konusunda bir sorun mu var? Matematik, fen, Türkçe sorabilirsin.", "📖 Bir ders sorusu sormak ister misin?"]
}

DERS_DISI_UYARI = [
    "💡 Sohbet güzel ama biraz ders sorusu soralım mı?",
    "📖 Ders dışına çıktık, hadi bir soru sor.",
    "🎯 NumBot olarak asıl görevim derslerinde sana yardımcı olmak!"
]

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber", "selamlar"],
    "nasilsin": ["nasılsın", "iyi misin", "ne yapıyorsun"],
    "iyi": ["iyiyim", "iyi", "güzel", "harika", "süper"],
    "kötü": ["kötüyüm", "kötü", "berbat", "üzgün", "mutsuz"],
    "teşekkür": ["teşekkür", "sağ ol", "mersi", "thanks"],
    "günaydın": ["günaydın", "iyi sabahlar", "sabah"],
    "iyi geceler": ["iyi geceler", "iyi akşamlar"],
    "kim": ["kimsin", "nesin", "adın ne", "sen kimsin"],
    "ne yapabilirsin": ["ne yapabilirsin", "ne yaparsın", "nasıl yardım"],
    "sıkıldım": ["sıkıldım", "bıktım", "canım sıkılıyor"]
}

EGITIM_KELIMELER = [
    "nedir", "nasıl", "açıkla", "anlat", "çöz", "hesapla", "öğret",
    "matematik", "fen", "türkçe", "tarih", "coğrafya", "ingilizce", "sosyal",
    "denklem", "kesir", "yüzde", "oran", "tam sayı", "rasyonel",
    "zarf", "zamir", "fiil", "isim", "sıfat", "noktalama", "dilbilgisi",
    "fotosentez", "mitoz", "hücre", "dna", "basınç", "elektrik",
    "üretim", "dağıtım", "tüketim", "ekonomi"
]

def mesaj_turu_tespit(mesaj):
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

# --------------------------------------------------------------
# SPOR İÇERİK ENGELLEME
# --------------------------------------------------------------
SPOR_KELIMELERI = [
    "nba", "futbol", "basketbol", "maç", "takım", "lig", "şampiyon", "lakers",
    "galatasaray", "fenerbahçe", "beşiktaş", "spor", "karşılaşma", "skor", 
    "gol", "sayı", "oyuncu", "transfer", "kupa", "galibiyet", "maçı", "son dakika"
]

def spor_icerik_mi(baslik, icerik):
    kontrol_metni = (baslik + " " + icerik).lower()
    for kelime in SPOR_KELIMELERI:
        if kelime in kontrol_metni:
            return True
    return False

# --------------------------------------------------------------
# TÜRKÇE SİTE KONTROLÜ
# --------------------------------------------------------------
def turkce_site_mi(url):
    url_lower = url.lower()
    # Türkçe site uzantıları
    if ".tr" in url_lower:
        return True
    # Türkçe eğitim siteleri (uzantı .com olsa bile)
    turkce_siteler = [
        "eokultv", "derslig", "morpakampus", "okulistik", "tongucakademi",
        "sinifogretmenim", "turkcedersi", "sosyalciniz", "konuvakti", "dersarsivi",
        "meb", "eba", "odsgm"
    ]
    for site in turkce_siteler:
        if site in url_lower:
            return True
    return False

# --------------------------------------------------------------
# SAYFA ÇEKME
# --------------------------------------------------------------
def sayfa_cek(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=8, headers=headers)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        metin = " ".join([el.get_text(" ", strip=True) for el in soup.find_all(["p", "h2", "h3", "li"])])
        metin = re.sub(r'(reklam|copyright|©|gizlilik|cookie|facebook|twitter|instagram|youtube)[^.]*\.', '', metin, flags=re.IGNORECASE)
        return metin[:3000]
    except:
        return ""

# --------------------------------------------------------------
# TF-IDF FALLBACK
# --------------------------------------------------------------
def tfidf_ozet(soru, metinler):
    if not metinler:
        return "Bilgi bulunamadı."
    
    cumleler = []
    for m in metinler:
        cumleler += re.split(r'(?<=[.!?])\s+', m)
    cumleler = [c.strip() for c in cumleler if len(c.strip()) > 40][:30]
    
    if not cumleler:
        return "Yeterli açıklama yok."
    
    try:
        docs = [soru] + cumleler
        vec = TfidfVectorizer(stop_words="turkish", max_features=400)
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
def groq_cevap(soru, metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = """Sen 7. sınıf öğrencilerine ders anlatan bir eğitim asistanısın. NumBot'sun.
        Verilen metne göre soruyu cevapla.
        MEB müfredatına uygun, 7. sınıf seviyesinde anlaşılır Türkçe kullan.
        Örnekler ver, madde işaretleri kullan."""
        
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem},
                {"role": "user", "content": f"Soru: {soru}\n\nBilgiler:\n{metin[:3500]}"}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return yanit.choices[0].message.content.strip()
    except:
        return None

# --------------------------------------------------------------
# NORMAL ARAMA (SADECE TÜRKÇE SİTELER, YABANCI YOK)
# --------------------------------------------------------------
def normal_ara(soru):
    if any(k in soru.lower() for k in ["zarf", "zamir", "fiil", "isim", "sıfat", "dilbilgisi"]):
        arama_sorgusu = f"{soru} türkçe dilbilgisi konu anlatımı 7 sınıf"
    else:
        arama_sorgusu = f"{soru} 7 sınıf konu anlatımı"
    
    try:
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(arama_sorgusu, region="tr-tr", max_results=10))
            
            # SADECE TÜRKÇE SİTELERİ VE SPOR İÇERMEYENLERİ TUT
            turkce_sonuclar = []
            for s in sonuclar:
                url = s.get("href", "").lower()
                baslik = s.get("title", "").lower()
                icerik = s.get("body", "").lower()
                
                # Yabancı siteleri engelle
                if not turkce_site_mi(url):
                    continue
                
                # Spor içerikleri engelle
                if spor_icerik_mi(baslik, icerik):
                    continue
                
                turkce_sonuclar.append(s)
            
            return turkce_sonuclar[:6]
    except:
        return []

# --------------------------------------------------------------
# CEVAP OLUŞTUR
# --------------------------------------------------------------
def cevap_uret(soru):
    sonuclar = normal_ara(soru)
    
    if not sonuclar:
        return "Üzgünüm, bu konuda Türkçe kaynaklarda bir şey bulamadım. Lütfen farklı bir soru sor.", [], None
    
    metinler = []
    kaynaklar = []
    
    for sonuc in sonuclar[:4]:
        if sonuc.get("body"):
            metinler.append(sonuc["body"])
        if sonuc.get("href") and sonuc.get("title"):
            kaynaklar.append({"url": sonuc["href"], "baslik": sonuc["title"][:50]})
            sayfa = sayfa_cek(sonuc["href"])
            if sayfa:
                metinler.append(sayfa)
            time.sleep(0.15)
    
    if not metinler:
        return "İçerik alınamadı.", kaynaklar[:3], None
    
    ham = "\n\n".join(metinler)
    cevap = groq_cevap(soru, ham)
    if not cevap:
        cevap = tfidf_ozet(soru, metinler)
    
    video_link = f"https://www.youtube.com/results?search_query={soru.replace(' ', '+')}+7+sınıf+konu+anlatımı"
    
    return cevap, kaynaklar[:3], video_link

# --------------------------------------------------------------
# SOHBET YÖNETİMİ (JSON)
# --------------------------------------------------------------
SOHBET_DOSYA = "sohbetler.json"

def sohbetleri_yukle():
    if os.path.exists(SOHBET_DOSYA):
        with open(SOHBET_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(SOHBET_DOSYA, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

def sohbetleri_kaydet(sohbetler):
    with open(SOHBET_DOSYA, "w", encoding="utf-8") as f:
        json.dump(sohbetler, f, ensure_ascii=False, indent=2)

def yeni_sohbet_olustur(baslik):
    return {
        "id": int(time.time() * 1000),
        "baslik": baslik,
        "mesajlar": [],
        "olusturma": time.time()
    }

# --------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------
if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = None
if "isim_bekleniyor" not in st.session_state:
    st.session_state.isim_bekleniyor = True
if "sohbetler" not in st.session_state:
    st.session_state.sohbetler = sohbetleri_yukle()
if "aktif_id" not in st.session_state:
    if st.session_state.sohbetler:
        st.session_state.aktif_id = st.session_state.sohbetler[0]["id"]
    else:
        st.session_state.aktif_id = None
if "disi_sayac" not in st.session_state:
    st.session_state.disi_sayac = 0

def aktif_sohbet():
    for s in st.session_state.sohbetler:
        if s["id"] == st.session_state.aktif_id:
            return s
    return None

# --------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-baslik">💬 Sohbetler</div>', unsafe_allow_html=True)
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        yeni = yeni_sohbet_olustur("Yeni Sohbet")
        st.session_state.sohbetler.insert(0, yeni)
        st.session_state.aktif_id = yeni["id"]
        sohbetleri_kaydet(st.session_state.sohbetler)
        st.rerun()
    
    st.markdown("---")
    
    for s in st.session_state.sohbetler:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(s["baslik"][:25], key=f"sb_{s['id']}"):
                st.session_state.aktif_id = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                st.session_state.sohbetler = [x for x in st.session_state.sohbetler if x["id"] != s["id"]]
                if st.session_state.aktif_id == s["id"]:
                    st.session_state.aktif_id = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
                sohbetleri_kaydet(st.session_state.sohbetler)
                st.rerun()
    
    st.markdown("---")
    st.caption("🔍 NumBot - Sadece Türkçe Kaynaklar")
    
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='text-align:center;margin-top:20px;padding:10px;background:rgba(102,126,234,0.2);border-radius:15px;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA EKRANI
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>🤖 Hoş Geldin!</h2><p>Ben NumBot, sana nasıl hitap edeyim?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("", placeholder="Adını yaz...", label_visibility="collapsed")
    if st.button("Başlayalım!"):
        if isim.strip():
            st.session_state.kullanici_adi = isim.strip()
            st.session_state.isim_bekleniyor = False
            if not st.session_state.sohbetler:
                yeni = yeni_sohbet_olustur("Yeni Sohbet")
                st.session_state.sohbetler.append(yeni)
                st.session_state.aktif_id = yeni["id"]
                sohbetleri_kaydet(st.session_state.sohbetler)
            st.rerun()
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Yapay Zeka Eğitim Asistanı | Sadece Türkçe Kaynaklar</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Başlamak için sol menüdeki **➕ Yeni Sohbet** butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mesaj-asistan"><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                html = '<div style="margin-top:10px">📚 <strong>Kaynaklar:</strong><br>'
                for k in m["kaynaklar"][:3]:
                    html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">🔗 {k["baslik"][:45]}</a> '
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
            if m.get("video_link"):
                st.markdown(f'<div class="video-oneri"><a href="{m["video_link"]}" target="_blank">🎬 YouTube\'da Ara</a></div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    girdi = st.chat_input(f"{ad}, ders sorusu sorabilirsin...")
    if girdi:
        msg = girdi.strip()
        if msg:
            sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
            
            if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
                sohbet["baslik"] = msg[:30] + ("..." if len(msg) > 30 else "")
                sohbetleri_kaydet(st.session_state.sohbetler)
            
            tur = mesaj_turu_tespit(msg)
            
            if tur == "egitim":
                st.session_state.disi_sayac = 0
                with st.spinner("🔍 NumBot Türkçe kaynaklarda araştırıyor..."):
                    cevap, kaynaklar, video = cevap_uret(msg)
                sohbet["mesajlar"].append({
                    "rol": "asistan",
                    "icerik": cevap,
                    "kaynaklar": kaynaklar,
                    "video_link": video,
                    "tur": "egitim"
                })
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice(DERS_DISI_UYARI)
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({
                    "rol": "asistan",
                    "icerik": cevap,
                    "tur": "diyalog",
                    "uyari": uyari
                })
            
            sohbetleri_kaydet(st.session_state.sohbetler)
            st.rerun()
