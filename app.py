import streamlit as st
import time
import re
import random
import json
import os
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
    "tam sayı": "📚 **Tam Sayılar - 7. Sınıf Matematik**\n\nTam sayılar pozitif, negatif ve sıfırdan oluşur.\n\n**Toplama:** Aynı işaretli toplanır, işaret aynı kalır. (+3)+(+5)=+8, (-3)+(-5)=-8\n**Çıkarma:** Çıkarılanın işareti değişir. (+5)-(-3)=+8\n**Çarpma/Bölme:** Aynı işaretli → pozitif, farklı işaretli → negatif. (-4)×(-2)=+8, (-4)×(+2)=-8\n\nÖrnek: Dalgıç -15 m'de iken 8 m yükselirse (-15)+(+8)=-7 m olur.",
    "denklem": "📚 **Denklemler - 7. Sınıf Matematik**\n\nDenklem, içinde bilinmeyen bulunan eşitliktir.\nÖrnek: 2x+3=7 → 2x=4 → x=2\n\nDenklem çözerken bilinmeyenleri bir tarafa, sayıları diğer tarafa toplarız.",
    "oran": "📚 **Oran ve Orantı - 7. Sınıf Matematik**\n\nOran, iki çokluğun birbirine bölünerek karşılaştırılmasıdır.\nÖrnek: 3/5 = 6/10 → doğru orantı\nBir sınıfta kızların erkeklere oranı 2/3 ise 12 kız varsa erkek sayısı 18'dir.",
    "yüzde": "📚 **Yüzdeler - 7. Sınıf Matematik**\n\nYüzde, bir sayının 100'de kaç olduğunu gösterir.\nÖrnek: 200 TL'nin %25'i = 200 × 25/100 = 50 TL indirim.\nİndirimli fiyat = 200 - 50 = 150 TL.",
    "zarf": "📚 **Zarflar (Belirteçler) - 7. Sınıf Türkçe**\n\nZarflar, fiilleri zaman, durum, miktar, yer-yön, soru yönünden belirtir.\n\n**Türleri:**\n1. Durum: hızlı koştu, güzel yazdı\n2. Zaman: yarın gelecek, şimdi gidiyor\n3. Miktar: çok okudu, az yedi\n4. Yer-Yön: içeri girdi, ileri gitti\n5. Soru: nasıl geldi?, ne zaman gitti?",
    "fiil": "📚 **Fiiller - 7. Sınıf Türkçe**\n\nFiiller, iş, oluş, hareket bildirir.\n\n- İş fiili: kitabı okudu\n- Oluş fiili: havalar soğudu\n- Durum fiili: bebek uyuyor\n\nHaber kipleri: geldi, gelmiş, geliyor, gelecek, gelir",
    "fotosentez": "📚 **Fotosentez - 7. Sınıf Fen Bilimleri**\n\n6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂\n\nBitkiler güneş ışığıyla besin üretir. Sadece gündüz gerçekleşir.",
    "mitoz": "📚 **Mitoz Bölünme - 7. Sınıf Fen Bilimleri**\n\n1 hücre → 2 hücre, kromozom sayısı değişmez. Evreleri: İnterfaz, Profaz, Metafaz, Anafaz, Telofaz. Büyüme, onarım.",
    "mayoz": "📚 **Mayoz Bölünme - 7. Sınıf Fen Bilimleri**\n\n1 hücre → 4 hücre, kromozom sayısı yarıya iner. Üreme hücreleri oluşur.",
    "elektrik": "📚 **Elektrik Devreleri - 7. Sınıf Fen Bilimleri**\n\nBasit devre: pil, lamba, anahtar, kablo. Seri ve paralel bağlantı.",
    "üretim": "📚 **Üretim, Dağıtım, Tüketim - 7. Sınıf Sosyal Bilgiler**\n\nÜretim → Dağıtım → Tüketim döngüsü. Bilinçli tüketim ve tüketici hakları.",
    "tarih": "📚 **Türk Tarihi - 7. Sınıf Sosyal Bilgiler**\n\nOrta Asya Türk devletleri, Malazgirt 1071, Osmanlı, Kurtuluş Savaşı, Cumhuriyet.",
    "coğrafya": "📚 **Türkiye'nin Bölgeleri - 7. Sınıf Sosyal Bilgiler**\n\n7 bölge ve özellikleri: Karadeniz (çay, fındık), Akdeniz (turizm), Ege (zeytin), Marmara (sanayi), İç Anadolu (tahıl), Doğu Anadolu (hayvancılık), Güneydoğu (pamuk).",
    "simple present": "📚 **Simple Present Tense - 7. Sınıf İngilizce**\n\nGenel durumlar, alışkanlıklar. I/You/We/They play. He/She/It plays. Olumsuz: don't/doesn't, Soru: Do/Does.",
    "present continuous": "📚 **Present Continuous - 7. Sınıf İngilizce**\n\nŞu anda olan olaylar. am/is/are + V-ing. I am playing, He is playing, They are playing."
}

def offline_cevap(soru):
    soru_lower = soru.lower()
    for anahtar, cevap in KONU_HAVUZU.items():
        if anahtar in soru_lower:
            return cevap
    return None

# --------------------------------------------------------------
# İNTERNETTEN ARAMA (DUCKDUCKGO) + GROQ İLE ÖZET
# --------------------------------------------------------------
def internetten_ara_groq(soru):
    try:
        sorgu = f"{soru} 7 sınıf konu anlatımı site:meb.gov.tr OR site:eba.gov.tr OR site:derslig.com OR site:morpakampus.com OR site:okulistik.com"
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(sorgu, region="tr-tr", max_results=4))
            if not sonuclar:
                return None, None
            metin = ""
            kaynaklar = []
            for s in sonuclar[:3]:
                if s.get("body"):
                    metin += s["body"] + "\n\n"
                if s.get("href"):
                    kaynaklar.append(s["href"])
            if not metin:
                return None, None
            # Groq ile özet çıkar
            client = Groq(api_key=GROQ_API_KEY)
            sistem = "Sen 7. sınıf öğrencilerine ders anlatan bir eğitim asistanısın. Verilen metni özetle, anlaşılır Türkçe kullan, madde işaretleri yap."
            yanit = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": sistem},
                    {"role": "user", "content": f"Soru: {soru}\n\nMetin:\n{metin[:3000]}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            ozet = yanit.choices[0].message.content.strip()
            kaynak_metni = "\n\n📚 **Kaynaklar:**\n" + "\n".join(kaynaklar) if kaynaklar else ""
            return ozet + kaynak_metni, kaynaklar
    except Exception as e:
        return None, None

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
    "ne yapabilirsin": ["📚 Tüm 7. sınıf derslerinde yardımcı olurum. İnternette araştırıp güvenilir kaynaklardan cevap veririm.", "🔍 Matematik, Türkçe, Fen, Sosyal, İngilizce sorularını cevaplarım."],
    "default": ["💭 Ders sorusu sorabilir misin?", "📖 Sana bir konuyu anlatmamı ister misin?"]
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

EGITIM_KELIMELER = ["nedir", "anlat", "açıkla", "konu", "zarf", "tam sayı", "fotosentez", "mitoz", "denklem", "yüzde", "oran", "fiil", "mayoz", "elektrik", "üretim", "tarih", "coğrafya", "simple present"]

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
    # Önce internet + Groq dene
    internet_cevap, _ = internetten_ara_groq(soru)
    if internet_cevap:
        return internet_cevap
    # Sonra offline havuz
    offline = offline_cevap(soru)
    if offline:
        return offline
    return "📚 Bu konuda henüz bilgim yok. Lütfen farklı bir soru sor veya konuyu daha açık yaz."

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
    st.caption("🔍 İnternette araştırır, Groq ile özetler, güvenilir kaynaklar.")
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
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Eğitim Asistanı | Groq ile Akıllı Cevaplar</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Başlamak için sol menüdeki ➕ Yeni Sohbet butonuna tıklayın.")
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
                with st.spinner("🔍 NumBot internette araştırıyor ve Groq ile özetliyor..."):
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
