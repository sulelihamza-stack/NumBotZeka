import streamlit as st
import time
import re
import random
import json
import os

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
# 7. SINIF KONU HAVUZU (NUMBOT'UN BİLDİĞİ KONULAR)
# --------------------------------------------------------------
KONU_HAVUZU = {
    "zarf": """📚 **Zarflar (Belirteçler) - 7. Sınıf Türkçe**

Zarflar, fiilleri (eylemleri) ve fiilimsileri; zaman, durum, miktar, yer-yön, soru gibi yönlerden belirten sözcüklerdir.

**Zarfların Özellikleri:**
- Tek başlarına kullanıldıklarında isim olabilirler
- Cümlede zarf görevinde kullanılırlar
- Fiillere sorulan "nasıl?", "ne zaman?", "ne kadar?", "nereye?" sorularına cevap verirler

**Zarf Türleri ve Örnekler:**

1. **Durum Zarfları:** Fiilin nasıl yapıldığını gösterir.
   - "hızlı koştu", "güzel yazdı", "sessizce ağladı"

2. **Zaman Zarfları:** Fiilin ne zaman yapıldığını gösterir.
   - "yarın gelecek", "şimdi gidiyor", "akşam yedim"

3. **Miktar Zarfları:** Fiilin ne kadar yapıldığını gösterir.
   - "çok okudu", "biraz yürüdü", "az uyudu"

4. **Yer-Yön Zarfları:** Fiilin nereye yapıldığını gösterir.
   - "içeri girdi", "ileri gitti", "aşağı indi"

5. **Soru Zarfları:** Fiili soru yoluyla belirtir.
   - "nasıl geldi?", "ne zaman gitti?", "niye ağladı?"

**Örnek Cümleler:**
- "Ali **hızlı** koştu." (Nasıl koştu? → Durum zarfı)
- "**Yarın** okula gideceğim." (Ne zaman gidecek? → Zaman zarfı)
- "**Çok** kitap okudum." (Ne kadar okudu? → Miktar zarfı)
- "**İçeri** girdi." (Nereye girdi? → Yer-yön zarfı)
- "**Nasıl** başardın?" (Soru zarfı)

📌 Zarflar, cümleye anlam katar ve anlatımı zenginleştirir.""",

    "tam sayı": """📚 **Tam Sayılar - 7. Sınıf Matematik**

Tam sayılar, pozitif tam sayılar, negatif tam sayılar ve sıfırdan oluşur.

**Tam Sayılarda İşlemler:**

1. **Toplama:**
   - Aynı işaretli: Toplanır, işaret aynı kalır
     (+3) + (+5) = +8
     (-3) + (-5) = -8
   - Farklı işaretli: Büyük sayıdan küçük çıkarılır, büyüğün işareti konur
     (-8) + (+3) = -5

2. **Çıkarma:**
   - Çıkarılan sayının işareti değişir
     (+5) - (-3) = (+5) + (+3) = +8

3. **Çarpma ve Bölme:**
   - Aynı işaretli → Pozitif
     (-4) × (-2) = +8
   - Farklı işaretli → Negatif
     (-4) × (+2) = -8

**Örnek:**
Bir dalgıç deniz seviyesinden -15 m'de iken 8 m yükselirse son konumu:
(-15) + (+8) = -7 m olur.""",

    "fotosentez": """📚 **Fotosentez - 7. Sınıf Fen Bilimleri**

Fotosentez, bitkilerin güneş ışığını kullanarak karbondioksit ve sudan besin (glikoz) ve oksijen üretmesidir.

**Fotosentez Denklemi:**
6CO₂ + 6H₂O → (ışık) → C₆H₁₂O₆ + 6O₂

**Fotosentezin Gerçekleştiği Yer:**
Kloroplast (bitki hücresinde bulunur)

**Fotosentez İçin Gerekenler:**
- Güneş ışığı
- Karbondioksit (CO₂)
- Su (H₂O)
- Klorofil (kloroplastta bulunan pigment)

**Fotosentez Sonucu Oluşanlar:**
- Glikoz (bitkinin besini)
- Oksijen (atmosfere verilir)

🔑 İpucu: Fotosentez sadece GÜNDÜZ gerçekleşir!""",

    "mitoz": """📚 **Mitoz Bölünme - 7. Sınıf Fen Bilimleri**

Mitoz, bir hücrenin iki yeni hücreye bölünmesidir.

**Mitozun Evreleri:**
1. **İnterfaz:** DNA kendini eşler
2. **Profaz:** Kromozomlar belirginleşir, çekirdek zarı erir
3. **Metafaz:** Kromozomlar hücrenin ortasına dizilir
4. **Anafaz:** Kromatidler ayrılır ve kutuplara çekilir
5. **Telofaz:** Çekirdek zarı yeniden oluşur

**Mitozun Özellikleri:**
- 1 hücre → 2 hücre oluşur
- Kromozom sayısı değişmez
- Tek hücrelilerde üreme, çok hücrelilerde büyüme ve onarım sağlar"""

}

def konu_bul(soru):
    soru_lower = soru.lower()
    for anahtar, cevap in KONU_HAVUZU.items():
        if anahtar in soru_lower:
            return cevap
    return None

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
    "ne yapabilirsin": ["📚 Bildiğim konular: Zarflar, Tam Sayılar, Fotosentez, Mitoz. Başka konuları da öğrenmek ister misin?", "🔍 Şu konuları anlatabilirim: Zarflar (Türkçe), Tam Sayılar (Matematik), Fotosentez (Fen), Mitoz (Fen)"],
    "default": ["💭 Ders sorusu sorabilir misin? Bildiğim konular: Zarflar, Tam Sayılar, Fotosentez, Mitoz", "📖 Sana Zarflar, Tam Sayılar, Fotosentez veya Mitoz konularını anlatabilirim. Hangisini istersin?"]
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

EGITIM_KELIMELER = ["nedir", "anlat", "açıkla", "konu", "zarf", "tam sayı", "fotosentez", "mitoz"]

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

def cevap_uret(soru):
    cevap = konu_bul(soru)
    if cevap:
        return cevap
    else:
        return "📚 Şu anda bildiğim konular: **Zarflar** (Türkçe), **Tam Sayılar** (Matematik), **Fotosentez** (Fen), **Mitoz** (Fen).\n\nBu konulardan birini sorabilir misin? Örneğin: 'Zarflar nedir?' veya 'Fotosentezi anlatır mısın?'"

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
    st.caption("📚 Bildiğim konular: Zarflar, Tam Sayılar, Fotosentez, Mitoz")
    
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
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Yapay Zeka Eğitim Asistanı</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Başlamak için sol menüdeki **➕ Yeni Sohbet** butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mesaj-asistan"><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
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
                cevap = cevap_uret(msg)
                sohbet["mesajlar"].append({
                    "rol": "asistan",
                    "icerik": cevap,
                    "tur": "egitim"
                })
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice(["💡 Sohbet güzel ama ders sorusu da sorabilirsin!", "📖 Bir ders sorusu sormaya ne dersin?"])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({
                    "rol": "asistan",
                    "icerik": cevap,
                    "tur": "diyalog",
                    "uyari": uyari
                })
            
            sohbetleri_kaydet(st.session_state.sohbetler)
            st.rerun()
