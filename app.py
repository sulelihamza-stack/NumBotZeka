import streamlit as st
import time
import re
import random
import json
import os
from duckduckgo_search import DDGS
from groq import Groq

GROQ_API_KEY = "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"

st.set_page_config(page_title="NumBot - 7. Sınıf Eğitim Asistanı", page_icon="🤖", layout="wide")

# Siyah tema (kısa versiyon)
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
# OFFLINE KONU HAVUZU (YEDEK - TÜM DERSLER)
# --------------------------------------------------------------
KONU_HAVUZU = {
    "zarf": "📚 **Zarflar (Belirteçler) - 7. Sınıf Türkçe**\n\nZarflar, fiilleri zaman, durum, miktar, yer-yön, soru yönünden belirtir.\n\n**Türleri:** Durum (hızlı koştu), Zaman (yarın gelecek), Miktar (çok okudu), Yer-Yön (içeri girdi), Soru (nasıl geldi?).",
    "tam sayı": "📚 **Tam Sayılar - 7. Sınıf Matematik**\n\nTam sayılar pozitif, negatif ve sıfırdan oluşur.\nToplama: Aynı işaretli toplanır. (-8)+(+3)=-5\nÇıkarma: (+5)-(-3)=+8\nÇarpma/Bölme: (-4)×(-2)=+8, (-4)×(+2)=-8",
    "fotosentez": "📚 **Fotosentez - 7. Sınıf Fen Bilimleri**\n\nFotosentez, bitkilerin güneş ışığıyla CO₂ ve H₂O'dan glikoz ve O₂ üretmesidir.\nDenklem: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",
    "mitoz": "📚 **Mitoz Bölünme - 7. Sınıf Fen Bilimleri**\n\n1 hücre → 2 hücre, kromozom sayısı değişmez. Evreleri: İnterfaz, Profaz, Metafaz, Anafaz, Telofaz.",
    "denklem": "📚 **Denklemler - 7. Sınıf Matematik**\n\nDenklem, içinde bilinmeyen bulunan eşitliktir. Örnek: 2x+3=7 → x=2",
    "üretim": "📚 **Üretim, Dağıtım, Tüketim - 7. Sınıf Sosyal Bilgiler**\n\nÜretim: mal/hizmet oluşturma. Dağıtım: tüketiciye ulaştırma. Tüketim: kullanma.",
    "simple present": "📚 **Simple Present Tense - 7. Sınıf İngilizce**\n\nGenel durumlar ve alışkanlıklar. Olumlu: I/You/We/They play, He/She/It plays. Olumsuz: don't/doesn't + fiil."
}

def offline_cevap(soru):
    soru_lower = soru.lower()
    for anahtar, cevap in KONU_HAVUZU.items():
        if anahtar in soru_lower:
            return cevap
    return None

# --------------------------------------------------------------
# İNTERNETTEN ARAMA (SADECE TÜRKÇE EĞİTİM SİTELERİ)
# --------------------------------------------------------------
def turkce_egitim_sitesi_mi(url):
    if not url:
        return False
    url_lower = url.lower()
    turkce_siteler = [".tr", "meb", "eba", "derslig", "morpakampus", "okulistik", "tongucakademi", "khanacademy.org.tr", "eokultv", "sinifogretmenim", "turkcedersi"]
    return any(site in url_lower for site in turkce_siteler)

def internetten_ara(soru):
    try:
        sorgu = f"{soru} 7 sınıf konu anlatımı"
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(sorgu, region="tr-tr", max_results=6))
            
            # Türkçe eğitim sitelerini filtrele
            turkce_sonuclar = [s for s in sonuclar if turkce_egitim_sitesi_mi(s.get("href"))]
            if not turkce_sonuclar:
                turkce_sonuclar = sonuclar[:3]
            
            if not turkce_sonuclar:
                return None, None
            
            metin = ""
            kaynaklar = []
            for s in turkce_sonuclar[:3]:
                if s.get("body"):
                    metin += s["body"] + "\n\n"
                if s.get("href"):
                    kaynaklar.append(s["href"])
            return metin[:3000], kaynaklar
    except:
        return None, None

def groq_cevap(soru, ham_metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = "Sen 7. sınıf öğrencilerine ders anlatan bir eğitim asistanısın. Verilen metne göre soruyu cevapla. MEB müfredatına uygun, anlaşılır Türkçe kullan."
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": sistem}, {"role": "user", "content": f"Soru: {soru}\n\nBilgiler:\n{ham_metin}"}],
            max_tokens=600,
            temperature=0.3
        )
        return yanit.choices[0].message.content.strip()
    except:
        return None

def cevap_uret(soru):
    # Önce internetten dene
    ham_metin, kaynaklar = internetten_ara(soru)
    if ham_metin:
        cevap = groq_cevap(soru, ham_metin)
        if cevap:
            if kaynaklar:
                cevap += "\n\n📚 **Kaynaklar:**\n" + "\n".join(kaynaklar)
            return cevap
        else:
            return "Üzgünüm, cevap üretirken bir sorun oluştu. Lütfen tekrar dener misin?", None
    
    # İnternet yoksa offline havuz
    offline = offline_cevap(soru)
    if offline:
        return offline + "\n\n📌 (İnternet bağlantısı olmadığı için hazır bilgilerden yararlanıldı.)", None
    
    return "🔍 Bu konuda internette veya hazır bilgilerimde bir şey bulamadım. Lütfen farklı bir soru sor.", None

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, sana nasıl yardımcı olabilirim?", "👋 Merhaba! Ders çalışmaya hazır mısın?"],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu soralım.", "⭐ Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["😔 Üzgünüm... Birlikte çalışırsak daha iyi hissedersin.", "💪 Geçer, merak etme!"],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek!"],
    "kim": ["🤖 Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "🧠 NumBot - eğitim asistanın!"],
    "ne yapabilirsin": ["🔍 İnternette güvenilir Türk eğitim sitelerinde araştırma yapıp sorularını cevaplarım.", "🌐 MEB, EBA, Derslig, Morpa, Okulistik, Tonguç gibi sitelerden bilgi toplarım."],
    "default": ["💭 Ders sorusu sorabilir misin? Matematik, Türkçe, Fen, Sosyal, İngilizce.", "📖 Bir konuyu sana anlatmamı ister misin?"]
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
    st.caption("🔍 Sadece güvenilir Türk eğitim sitelerinde araştırma yapar.")
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
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Yapay Zeka Eğitim Asistanı | Güvenilir Türk Sitelerinde Araştırır</div>', unsafe_allow_html=True)

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
                with st.spinner("🔍 NumBot güvenilir Türk eğitim sitelerinde araştırıyor..."):
                    cevap = cevap_uret(msg)
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "egitim"})
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
