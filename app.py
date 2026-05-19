import streamlit as st
import time
import re
import random
import json
import os
import requests
from groq import Groq

# --------------------------------------------------------------
# GOOGLE CSE BİLGİLERİ (SENİN VERDİKLERİN)
# --------------------------------------------------------------
SEARCH_ENGINE_ID = "230f6376b7740411d"
API_KEY = "AIzaSyA0_BxAEG2pcd0SdwhzanArxQq6gF84TvE"
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
.isim-ekran { max-width: 400px; margin: 100px auto; background: #1a1a2e; border-radius: 30px; padding: 40px; text-align: center; border: 1px solid #2a2a3e; }
[data-testid="stChatInput"] { background: #1a1a2e !important; border-color: #2a2a3e !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# SPOR FİLTRESİ
# --------------------------------------------------------------
SPOR_KELIMELER = ["nba", "futbol", "basketbol", "maç", "takım", "lig", "şampiyon", "lakers", "galatasaray", "fenerbahçe", "beşiktaş", "premier league", "spor", "gol", "transfer", "trabzonspor", "başakşehir", "süper lig", "şampiyonlar ligi"]

def spor_mu(baslik, icerik):
    kontrol = (baslik + " " + icerik).lower()
    for kelime in SPOR_KELIMELER:
        if kelime in kontrol:
            return True
    return False

# --------------------------------------------------------------
# GOOGLE CSE ARAMA (GERÇEK API ÇAĞRISI)
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def google_cse_ara(soru):
    sorgu = f"{soru} 7 sınıf konu anlatımı"
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={sorgu}&lr=lang_tr"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data:
            st.warning("Google CSE sonuç bulamadı. Yanıt: " + str(data))
            return None, None
        
        metin = ""
        kaynaklar = []
        for item in data["items"][:3]:
            baslik = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            
            if spor_mu(baslik, snippet):
                continue
            
            metin += f"{baslik}\n{snippet}\n\n"
            kaynaklar.append(link)
        
        if not metin:
            return None, None
        return metin[:3000], kaynaklar
    except Exception as e:
        st.error(f"Google CSE hatası: {e}")
        return None, None

# --------------------------------------------------------------
# GROQ SENTEZ
# --------------------------------------------------------------
def groq_cevap(soru, metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = """Sen 7. sınıf öğrencilerine ders anlatan bir eğitim asistanısın.
        Verilen metne göre soruyu cevapla. MEB müfredatına uygun, anlaşılır Türkçe kullan.
        Örnekler ver, madde işaretleri kullan.
        ASLA spor (futbol, basketbol, NBA, Premier League, Süper Lig) ile ilgili örnek verme.
        Sadece ders konularına odaklan."""
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem},
                {"role": "user", "content": f"Soru: {soru}\n\nBilgiler:\n{metin[:3500]}"}
            ],
            max_tokens=600,
            temperature=0.3
        )
        return yanit.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Groq hatası: {e}")
        return None

def cevap_uret(soru):
    metin, kaynaklar = google_cse_ara(soru)
    if not metin:
        return "🔍 Bu konuda güvenilir eğitim sitelerinde (MEB, Derslig, Morpa, Okulistik, Tonguç) bilgi bulamadım. Lütfen farklı bir soru sor.", None
    
    cevap = groq_cevap(soru, metin)
    if not cevap:
        cevap = "Üzgünüm, cevap üretilemedi. Lütfen tekrar dene."
    
    if kaynaklar:
        cevap += "\n\n📚 **Kaynaklar:**\n" + "\n".join([f"🔗 {k}" for k in kaynaklar[:3]])
    
    return cevap, kaynaklar

# --------------------------------------------------------------
# DİYALOG SİSTEMİ (Kısa)
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, 7. sınıf derslerinde sana yardımcı olabilirim.", "👋 Merhaba! Ders sorusu sorabilirsin."],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu soralım.", "⭐ Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["😔 Üzgünüm... Birlikte çalışalım, daha iyi hissedersin.", "💪 Geçer, merak etme!"],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek!"],
    "kim": ["🤖 Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "🧠 NumBot - eğitim asistanın!"],
    "ne yapabilirsin": ["🔍 Sadece güvenilir eğitim sitelerinde (MEB, Derslig, Morpa, Okulistik, Tonguç) araştırma yaparım.", "📚 7. sınıf tüm derslerde sana yardımcı olurum."],
    "default": ["💭 Ders sorusu sorabilir misin? İnternette güvenilir kaynaklardan araştırayım.", "📖 Bir konuyu sana anlatmamı ister misin?"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber"],
    "nasilsin": ["nasılsın", "iyi misin"],
    "iyi": ["iyiyim", "iyi", "güzel"],
    "kötü": ["kötüyüm", "kötü", "üzgün"],
    "teşekkür": ["teşekkür", "sağ ol"],
    "kim": ["kimsin", "nesin", "adın ne"],
    "ne yapabilirsin": ["ne yapabilirsin", "ne yaparsın", "yeteneklerin neler"]
}

EGITIM_KELIMELER = ["nedir", "anlat", "açıkla", "konu", "ders", "matematik", "fen", "türkçe", "sosyal", "ingilizce"]

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
# SOHBET YÖNETİMİ (JSON)
# --------------------------------------------------------------
SOHBET_DOSYA = "sohbetler.json"

def sohbetleri_yukle():
    if os.path.exists(SOHBET_DOSYA):
        try:
            with open(SOHBET_DOSYA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    else:
        with open(SOHBET_DOSYA, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

def sohbetleri_kaydet(sohbetler):
    with open(SOHBET_DOSYA, "w", encoding="utf-8") as f:
        json.dump(sohbetler, f, ensure_ascii=False, indent=2)

def yeni_sohbet_olustur(baslik):
    return {"id": int(time.time() * 1000), "baslik": baslik, "mesajlar": [], "olusturma": time.time()}

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
    st.caption("🔍 Google CSE ile sadece güvenilir eğitim siteleri taranıyor.")
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
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Eğitim Asistanı | Google CSE + Groq AI</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Başlamak için sol menüdeki **➕ Yeni Sohbet** butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mesaj-asistan"><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div style="background:rgba(255,200,100,0.1);border-radius:10px;padding:8px;margin-top:8px;color:#ffd966">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    girdi = st.chat_input(f"{ad}, ders sorusu sorabilirsin...")
    if girdi:
        msg = girdi.strip()
        if msg:
            sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
            sohbetleri_kaydet(st.session_state.sohbetler)
            
            if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
                sohbet["baslik"] = msg[:30] + ("..." if len(msg) > 30 else "")
                sohbetleri_kaydet(st.session_state.sohbetler)
            
            tur = mesaj_turu_tespit(msg)
            
            if tur == "egitim":
                st.session_state.disi_sayac = 0
                with st.spinner("🔍 NumBot, Google CSE ile güvenilir eğitim sitelerinde araştırıyor..."):
                    cevap, kaynaklar = cevap_uret(msg)
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "egitim", "kaynaklar": kaynaklar})
                sohbetleri_kaydet(st.session_state.sohbetler)
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice(["💡 Sohbet güzel ama ders sorusu da sorabilirsin!", "📖 Bir ders sorusu sormaya ne dersin?"])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "diyalog", "uyari": uyari})
                sohbetleri_kaydet(st.session_state.sohbetler)
            
            st.rerun()
