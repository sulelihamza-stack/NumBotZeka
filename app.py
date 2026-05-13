import streamlit as st
import requests
import time
import re
import random
from html.parser import HTMLParser

# --------------------------------------------------------------
# GROQ API YOK - SADECE KENDİ BİLGİMİZLE CEVAP VERİYORUZ
# --------------------------------------------------------------

st.set_page_config(page_title="7. Sınıf Eğitim Asistanı", page_icon="📚", layout="wide")

# --------------------------------------------------------------
# TEMA (CSS)
# --------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap');
html, body, [data-testid="stAppViewContainer"] { background-color: #ffffff; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
.sb-baslik { font-size: 1.1rem; font-weight: 600; padding: 10px 16px; border-bottom: 1px solid #e0e0e0; text-align: center; }
.ana-baslik { font-size: 1.4rem; font-weight: 600; text-align: center; margin: 20px 0 5px; color: #2c3e50; }
.ana-alt { font-size: 0.85rem; color: #6c757d; text-align: center; margin-bottom: 20px; }
.mesaj-kullanici { display: flex; justify-content: flex-end; margin: 10px 0; }
.mesaj-kullanici span { background: #007bff; color: white; padding: 8px 15px; border-radius: 18px 18px 4px 18px; max-width: 75%; }
.mesaj-asistan { margin: 10px 0; }
.asistan-tur { font-size: 11px; color: #6c757d; border-left: 2px solid #007bff; padding-left: 8px; margin-bottom: 5px; }
.cevap-kutu { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px 18px 18px 18px; padding: 12px 18px; line-height: 1.6; }
.isim-ekran { max-width: 400px; margin: 100px auto; background: white; border: 1px solid #dee2e6; border-radius: 20px; padding: 30px; text-align: center; }
.uyari-kutu { background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; padding: 8px 12px; margin-top: 8px; color: #856404; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# 7. SINIF MÜFREDATI (KENDİ BİLGİ HAVUZUMUZ)
# --------------------------------------------------------------
BILGI_HAVUZU = {
    "fotosentez": "Fotosentez, bitkilerin güneş ışığını kullanarak karbondioksit ve sudan besin (glikoz) ve oksijen üretmesidir. 7. sınıf fen bilimleri konusudur. Fotosentez için ışık, klorofil, su ve karbondioksit gereklidir.",
    "mitoz": "Mitoz, bir hücrenin iki yeni hücreye bölünmesidir. 7. sınıf fen bilimlerinde mitozun evreleri: profaz, metafaz, anafaz, telofaz. Mitoz sonucu iki yavru hücre oluşur.",
    "mayoz": "Mayoz, üreme hücrelerinin oluşumunda görülen hücre bölünmesidir. Sonuçta 4 yavru hücre oluşur ve kromozom sayısı yarıya iner.",
    "denklem": "Denklem, içinde bilinmeyen bulunan eşitliktir. 7. sınıfta birinci dereceden bir bilinmeyenli denklemler görülür. Örnek: 2x + 3 = 7 ise x = 2'dir.",
    "tam sayı": "Tam sayılar, pozitif ve negatif sayılar ile sıfırdan oluşur. 7. sınıfta tam sayılarla toplama, çıkarma, çarpma, bölme işlemleri öğrenilir.",
    "rasyonel sayı": "Rasyonel sayılar a/b şeklinde yazılabilen sayılardır. 7. sınıfta rasyonel sayılarla işlemler, sıralama ve ondalık gösterim konuları vardır.",
    "yüzde": "Yüzde, bir sayının 100'de kaç olduğunu gösterir. 7. sınıfta yüzde hesaplamaları, indirim, kar-zarar problemleri öğrenilir.",
    "oran": "Oran, iki çokluğun birbirine bölünerek karşılaştırılmasıdır. 7. sınıfta oran problemleri ve doğru orantı konusu vardır.",
    "açı": "Açı, iki ışının ortak başlangıç noktasında oluşturduğu şekildir. Tümler açı (90°'ye tamamlayan), bütünler açı (180°'ye tamamlayan) 7. sınıf konusudur.",
    "üçgen": "Üçgenin iç açıları toplamı 180°'dir. Üçgen çeşitleri: eşkenar, ikizkenar, çeşitkenar. 7. sınıfta üçgenlerde alan hesapları da vardır.",
    "türkçe fiil": "Fiil (eylem), iş, oluş, hareket bildiren sözcüklerdir. 7. sınıfta fiillerde zaman, kişi ve yapı özellikleri öğrenilir.",
    "ingilizce simple present": "Simple present tense genel geçer durumlar ve alışkanlıklar için kullanılır. 3. tekil şahıslarda fiile -s/-es takısı eklenir. Örnek: She plays tennis.",
    "sosyal türk tarihi": "Türkler Orta Asya'da kurdukları devletlerle tarih sahnesine çıkmıştır. 1071 Malazgirt Zaferi ile Anadolu'nun kapıları Türklere açılmıştır."
}

# --------------------------------------------------------------
# BASİT CEVAP ÜRETİCİ
# --------------------------------------------------------------
def egitim_cevabi(soru: str) -> str:
    soru_lower = soru.lower()
    
    # Anahtar kelime eşlemesi
    for anahtar, cevap in BILGI_HAVUZU.items():
        if anahtar in soru_lower:
            return cevap + "\n\n📌 Başka bir konuda yardımcı olabilir miyim?"
    
    # Matematik işlemi kontrolü
    if "+" in soru_lower or "-" in soru_lower or "x" in soru_lower or "÷" in soru_lower or "/" in soru_lower or "kaç" in soru_lower:
        match = re.search(r'(\d+)\s*([+\-x÷/])\s*(\d+)', soru)
        if match:
            a = int(match.group(1))
            op = match.group(2)
            b = int(match.group(3))
            if op == '+':
                return f"{a} + {b} = {a + b}\n\n✅ İşlem bu şekilde çözülür. Başka matematik sorun var mı?"
            elif op == '-':
                return f"{a} - {b} = {a - b}\n\n✅ İşlem bu şekilde çözülür. Başka sorun varsa sorabilirsin."
            elif op in ['x', '×']:
                return f"{a} × {b} = {a * b}\n\n✅ Çarpma işleminin sonucu bu. Başka bir şey öğrenmek ister misin?"
            elif op in ['÷', '/']:
                if b != 0:
                    return f"{a} ÷ {b} = {a / b}\n\n✅ Bölme işleminin sonucu bu. Yardımcı olabileceğim başka bir şey var mı?"
    
    # Belirli bir konu bulunamazsa
    return "Bu soruyu yanıtlamak için henüz yeterli bilgim yok. 7. sınıf konularından (fotosentez, mitoz, denklemler, yüzdeler, oranlar, açılar, üçgenler, Türkçede fiiller, İngilizce zamanlar, sosyal bilgiler) birini sorabilir misin? Yardımcı olmaktan mutluluk duyarım! 🙏"

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["Selam! 7. sınıf derslerinde sana nasıl yardımcı olabilirim?", "Merhaba! Bugün hangi konuyu çalışmak istersin?", "Hey! Matematik, fen, Türkçe veya başka bir ders sorusu sorabilirsin."],
    "nasilsin": ["İyiyim, teşekkürler! Sen nasılsın? Dersler nasıl gidiyor?", "Gayet iyiyim! Sana nasıl yardımcı olabilirim?"],
    "iyi": ["Harika! O zaman bir ders sorusu sormaya ne dersin?", "Süper! Hadi öğrenmeye başlayalım. Aklındaki soruyu sor."],
    "kötü": ["Üzüldüm... Birlikte ders çalışırsak belki moralin düzelir. Bir soru sormak ister misin?", "Geçer, merak etme! Hadi bir konuyu birlikte çalışalım."],
    "teşekkür": ["Rica ederim! Başka sorun olursa buradayım.", "Ne demek! Her zaman yardımcı olmaya hazırım."],
    "kim": ["Ben 7. Sınıf Eğitim Asistanı'yım. Derslerinde sana destek olmak için buradayım!", "Yapay zeka asistanıyım, 7. sınıf müfredatındaki konularda yardım ederim."],
    "ne yapabilirsin": ["Sana 7. sınıf ders konularını anlatabilirim! Fen, matematik, Türkçe, sosyal bilgiler, İngilizce... Sorularını yanıtlayabilirim.", "Matematik işlemleri yapabilir, ders konularını açıklayabilirim. Denemek ister misin?"],
    "default": ["Anlıyorum! Ders konusunda bir sorun mu var? Matematik, fen, Türkçe, İngilizce veya sosyal bilgiler sorusu sorabilirsin.", "Bir ders sorusu sormak ister misin? Sana yardımcı olmaktan mutluluk duyarım!"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber", "selamlar"],
    "nasilsin": ["nasılsın", "nasılsınız", "iyi misin", "naber"],
    "iyi": ["iyiyim", "iyi", "güzel", "harika", "süper", "fena değil"],
    "kötü": ["kötüyüm", "kötü", "berbat", "üzgün", "mutsuz"],
    "teşekkür": ["teşekkür", "sağ ol", "mersi", "thanks"],
    "kim": ["kimsin", "nesin", "adın ne"],
    "ne yapabilirsin": ["ne yapabilirsin", "ne yaparsın", "nasıl yardım"]
}

def mesaj_turu_tespit(mesaj: str) -> str:
    m = mesaj.lower().strip()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if len(m.split()) >= 2:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur: str) -> str:
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

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

def yeni_sohbet(adi: str):
    return {"id": int(time.time()*1000), "baslik": adi, "mesajlar": []}

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
        yeni = yeni_sohbet("Yeni Sohbet")
        st.session_state.sohbetler.insert(0, yeni)
        st.session_state.aktif_id = yeni["id"]
        st.rerun()
    
    st.markdown("---")
    
    for s in st.session_state.sohbetler:
        if st.button(s["baslik"][:28], key=f"sb_{s['id']}"):
            st.session_state.aktif_id = s["id"]
            st.rerun()
    
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='margin-top: 20px; text-align: center; font-size: 13px;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA EKRANI
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>✨ Hoş Geldin!</h2><p>Sana nasıl hitap etmemi istersin?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("", placeholder="Adını yaz...", label_visibility="collapsed")
    if st.button("Başlayalım!"):
        if isim.strip():
            st.session_state.kullanici_adi = isim.strip()
            st.session_state.isim_bekleniyor = False
            if not st.session_state.sohbetler:
                yeni = yeni_sohbet("Yeni Sohbet")
                st.session_state.sohbetler.append(yeni)
                st.session_state.aktif_id = yeni["id"]
            st.rerun()
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">📚 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">7. Sınıf Eğitim Asistanı | Matematik, Fen, Türkçe, İngilizce, Sosyal Bilgiler</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Yeni bir sohbet başlatmak için sol menüdeki **➕ Yeni Sohbet** butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "📝 Cevap" if m.get("tur") == "egitim" else "💬 Sohbet"
            st.markdown(f'<div class="mesaj-asistan"><div class="asistan-tur">{tur_yazi}</div><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    girdi = st.chat_input(f"{ad}, sorunu yazabilirsin...")
    if girdi:
        msg = girdi.strip()
        if msg:
            sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
            
            if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
                sohbet["baslik"] = msg[:30] + ("..." if len(msg) > 30 else "")
            
            tur = mesaj_turu_tespit(msg)
            
            if tur == "egitim":
                st.session_state.disi_sayac = 0
                with st.spinner("Düşünüyorum..."):
                    cevap = egitim_cevabi(msg)
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "egitim"})
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice([
                        "Sohbet güzel ama biraz ders sorusu soralım mı?",
                        "Ders dışına çıktık, hadi bir soru sor.",
                        "Eğlenmek güzel ama öğrenmek de önemli! Bir ders sorusu sormaya ne dersin?"
                    ])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "diyalog", "uyari": uyari})
            
            st.rerun()
