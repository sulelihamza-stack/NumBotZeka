import streamlit as st
import requests
import time
import re
import random
from duckduckgo_search import DDGS
from groq import Groq

# --------------------------------------------------------------
# GROQ API ANAHTARI (KENDİ ANAHTARINIZI YAZIN)
# --------------------------------------------------------------
GROQ_API_KEY = "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"

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
.kaynak-kart { background: #fff; border: 1px solid #dee2e6; border-radius: 6px; padding: 3px 8px; font-size: 12px; text-decoration: none; margin-right: 5px; display: inline-block; }
.kaynak-kart:hover { border-color: #007bff; color: #007bff; }
.uyari-kutu { background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; padding: 8px 12px; margin-top: 8px; color: #856404; font-size: 13px; }
.video-oneri a { background: #f1f1f1; padding: 4px 10px; border-radius: 20px; text-decoration: none; font-size: 13px; color: #333; }
.video-oneri a:hover { background: #e9ecef; }
.isim-ekran { max-width: 400px; margin: 100px auto; background: white; border: 1px solid #dee2e6; border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.chat-input { border-radius: 14px; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["Selam! Nasılsın? Hangi konuda yardım edebilirim?", "Merhaba! Ders çalışmaya hazır mısın?", "Hey! Sana nasıl yardımcı olabilirim?"],
    "nasilsin": ["İyiyim, teşekkürler! Sen nasılsın?", "Gayet iyiyim! Dersler nasıl gidiyor?", "Harika hissediyorum! Senden naber?"],
    "iyi": ["Ne güzel! O zaman bir soru sormaya ne dersin?", "Süper! Hadi öğrenmeye başlayalım.", "Harika! Bugün hangi konuyu çalışmak istersin?"],
    "kötü": ["Üzgünüm... Birlikte ders çalışırsak belki neşelenirsin, dener misin?", "Geçer, merak etme! Ders sorusu sormak ister misin?", "Üzülme, öğrenmek insanı mutlu eder. Bir soru sor bakalım."],
    "teşekkür": ["Rica ederim! Başka sorun olursa buradayım.", "Ne demek! Her zaman yardımcı olmaya hazırım.", "Estağfurullah! Öğrenmek için sor sormaya devam."],
    "günaydın": ["Günaydın! Verimli bir gün geçirmeni dilerim.", "Günaydın! Yeni bilgiler öğrenmeye ne dersin?", "Sabah sabah ders çalışmak harika! Hazır mısın?"],
    "iyi geceler": ["İyi geceler! Yarın görüşürüz.", "İyi geceler! Öğrendiklerini tekrar etmeyi unutma.", "Uykudan önce bir soru çözmek ister misin?"],
    "kim": ["Ben 7. Sınıf Eğitim Asistanı'yım.", "Yapay zeka asistanıyım, derslerinde sana yardımcı olurum.", "Adım NumNum, 7. sınıf konularında sana destek olmak için buradayım."],
    "ne yapabilirsin": ["Sana 7. sınıf konularını anlatabilirim, sorularını cevaplayabilirim.", "Her ders sorusunu araştırıp cevaplarım. Fen, matematik, Türkçe, sosyal, ingilizce...", "İnternette araştırma yapıp sana özet bir cevap hazırlarım."],
    "sıkıldım": ["Hadi bir soru sor, belki ilginç bir şey öğreniriz.", "Sıkılmak normal, ama öğrenmek eğlencelidir. Soru sor!", "Ders çalışmak bazen sıkıcı gelebilir ama küçük bir soruyla başlayalım."],
    "default": ["Anlıyorum! Ders konusunda bir sorun mu var?", "Bir ders sorusu sormak ister misin?", "Hmm, tam anlayamadım. Matematik, fen veya başka bir ders sorusu sorabilirsin."]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber", "selamlar"],
    "nasilsin": ["nasılsın", "nasılsınız", "iyi misin", "ne yapıyorsun", "naber"],
    "iyi": ["iyiyim", "iyi", "güzel", "harika", "süper", "fena değil"],
    "kötü": ["kötüyüm", "kötü", "berbat", "üzgün", "mutsuz", "keyifsiz"],
    "teşekkür": ["teşekkür", "sağ ol", "mersi", "thanks", "eyvallah"],
    "günaydın": ["günaydın", "iyi sabahlar", "sabah"],
    "iyi geceler": ["iyi geceler", "iyi akşamlar"],
    "kim": ["kimsin", "nesin", "adın ne", "sensın"],
    "ne yapabilirsin": ["ne yapabilirsin", "ne yaparsın", "nasıl yardım", "neler yaparsın"],
    "sıkıldım": ["sıkıldım", "bıktım", "canım sıkılıyor", "sıkıcı"]
}

EGITIM_ANAHTAR = [
    "nedir", "nasıl", "ne zaman", "nerede", "açıkla", "anlat", "öğret",
    "formül", "hesapla", "çöz", "farkı", "tanım", "örnek", "konu",
    "ders", "matematik", "fen", "tarih", "coğrafya", "ingilizce", "türkçe",
    "fotosentez", "mitoz", "denklem", "oran", "yüzde", "açı", "üçgen"
]

def mesaj_turu_tespit(mesaj: str) -> str:
    m = mesaj.lower().strip()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if any(k in m for k in EGITIM_ANAHTAR) or len(m.split()) >= 4:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur: str) -> str:
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

# --------------------------------------------------------------
# ARAMA (DuckDuckGo)
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def ddg_ara(sorgu: str, n: int = 6):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(sorgu, region="tr-tr", max_results=n))
    except Exception as e:
        st.error(f"Arama hatası: {e}")
        return []

# --------------------------------------------------------------
# BASİT ÖZETLEME (GROQ ÇALIŞMAZSA)
# --------------------------------------------------------------
def basit_ozetle(soru: str, metin_parcalari: list, max_cumle: int = 5) -> str:
    if not metin_parcalari:
        return "İlgili içerik bulunamadı."
    
    tum_cumleler = []
    for p in metin_parcalari:
        cumleler = re.split(r'(?<=[.!?])\s+', p)
        tum_cumleler.extend([c.strip() for c in cumleler if len(c.strip()) > 35])
    
    if not tum_cumleler:
        return "Yeterli açıklama bulunamadı."
    
    stopwords = {"nedir", "nasıl", "ne", "bir", "ve", "ile", "bu", "şu", "o", "da", "de", "mi", "mı", "mu", "mü", "ki", "ise", "için", "gibi", "kadar", "üzere", "ancak", "fakat"}
    soru_kelimeler = set(re.findall(r'\b[a-zçğıöşü]{3,}\b', soru.lower()))
    soru_kelimeler -= stopwords
    
    if not soru_kelimeler:
        return "\n\n".join(tum_cumleler[:max_cumle])
    
    puanli = []
    for c in tum_cumleler:
        puan = 0
        c_lower = c.lower()
        for kelime in soru_kelimeler:
            if kelime in c_lower:
                puan += 2
        if len(c) > 100:
            puan += 1
        if len(c) < 40:
            puan -= 1
        puanli.append((puan, c))
    
    puanli.sort(key=lambda x: (x[0], len(x[1])), reverse=True)
    secilen = [c for p, c in puanli[:max_cumle] if p > 0]
    
    if not secilen:
        secilen = tum_cumleler[:max_cumle]
    
    goruldu = set()
    benzersiz = []
    for c in secilen:
        if c[:60] not in goruldu:
            goruldu.add(c[:60])
            benzersiz.append(c)
    
    return "\n\n".join(benzersiz)

# --------------------------------------------------------------
# GROQ SENTEZ
# --------------------------------------------------------------
def groq_sentezle(soru: str, ham_metin: str) -> str | None:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = (
            "Sen 7. sınıf öğrencisine yardım eden bir eğitim asistanısın. "
            "Verilen metne göre soruyu cevapla. Sade ve anlaşılır Türkçe kullan, 3-5 paragraf veya madde halinde yaz. "
            "Kaynak adı yazma, gereksiz detaylardan kaçın. Cevabı öğrencinin anlayacağı seviyede tut."
        )
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
        st.warning(f"Groq hatası: {e} → Basit özetleme kullanılıyor.")
        return None

# --------------------------------------------------------------
# GÖRSEL / VİDEO
# --------------------------------------------------------------
def konu_icin_gorsel(soru: str) -> str | None:
    try:
        with DDGS() as ddgs:
            res = list(ddgs.images(soru, max_results=1))
            return res[0]["image"] if res else None
    except:
        return None

def konu_icin_video_linki(soru: str) -> str:
    return f"https://www.youtube.com/results?search_query=7.+sinif+{soru.replace(' ', '+')}"

# --------------------------------------------------------------
# ANA CEVAP ÜRETİCİ
# --------------------------------------------------------------
def cevap_olustur(soru: str):
    sonuclar = ddg_ara(f"{soru} 7. sınıf", n=6)
    if len(sonuclar) < 3:
        sonuclar += ddg_ara(f"{soru} nedir açıkla", n=4)
    
    if not sonuclar:
        return "Üzgünüm, internette bir şey bulamadım.", [], None, ""
    
    ozetler = [r.get("body", "") for r in sonuclar if r.get("body") and len(r.get("body", "")) > 50]
    
    kaynaklar = []
    for r in sonuclar[:5]:
        url = r.get("href")
        if url:
            kaynaklar.append({"url": url, "baslik": r.get("title", url)[:60]})
    
    if not ozetler:
        return "Arama sonucu metin yok.", kaynaklar, None, ""
    
    ham_metin = "\n\n".join(ozetler)
    
    cevap = groq_sentezle(soru, ham_metin)
    if not cevap:
        cevap = basit_ozetle(soru, ozetler)
    
    gorsel = konu_icin_gorsel(soru)
    video = konu_icin_video_linki(soru)
    
    return cevap, kaynaklar[:4], gorsel, video

# --------------------------------------------------------------
# SOHBET YÖNETİMİ (SESSION STATE)
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
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            if st.button(s["baslik"][:28], key=f"sb_{s['id']}"):
                st.session_state.aktif_id = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                st.session_state.sohbetler = [x for x in st.session_state.sohbetler if x["id"] != s["id"]]
                if st.session_state.aktif_id == s["id"]:
                    st.session_state.aktif_id = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
                st.rerun()
    
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='margin-top: 20px; text-align: center; font-size: 13px; color: #6c757d;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA EKRANI
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>✨ Hoş Geldin! ✨</h2><p>Sana nasıl hitap etmemi istersin?</p></div>', unsafe_allow_html=True)
    isim = st.text_input("", placeholder="Adını yaz...", label_visibility="collapsed")
    if st.button("🎉 Başlayalım!", use_container_width=True):
        if isim.strip():
            st.session_state.kullanici_adi = isim.strip()
            st.session_state.isim_bekleniyor = False
            if not st.session_state.sohbetler:
                yeni = yeni_sohbet("Yeni Sohbet")
                st.session_state.sohbetler.append(yeni)
                st.session_state.aktif_id = yeni["id"]
            st.rerun()
        else:
            st.warning("Lütfen adını yaz.")
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">📚 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">7. Sınıf Eğitim Asistanı | İnternetten anlık, Groq ile sentezlenmiş cevaplar</div>', unsafe_allow_html=True)

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
            
            if m.get("kaynaklar"):
                src_html = '<div style="margin-top: 8px;">📌 <strong>Kaynaklar:</strong><br>'
                for i, k in enumerate(m["kaynaklar"], 1):
                    src_html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">🔗 {i}. {k["baslik"][:45]}</a> '
                src_html += '</div>'
                st.markdown(src_html, unsafe_allow_html=True)
            
            if m.get("gorsel"):
                st.image(m["gorsel"], width=200, caption="Konuyla ilgili görsel")
            
            if m.get("video_link"):
                st.markdown(f'<div class="video-oneri">🎬 <a href="{m["video_link"]}" target="_blank">YouTube\'da bu konuyu ara →</a></div>', unsafe_allow_html=True)
            
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
                with st.spinner("🔍 Araştırılıyor ve cevap hazırlanıyor..."):
                    cevap, kaynaklar, gorsel, vlink = cevap_olustur(msg)
                sohbet["mesajlar"].append({
                    "rol": "asistan", "icerik": cevap,
                    "kaynaklar": kaynaklar, "tur": "egitim",
                    "gorsel": gorsel, "video_link": vlink
                })
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
                sohbet["mesajlar"].append({
                    "rol": "asistan", "icerik": cevap,
                    "tur": "diyalog", "uyari": uyari
                })
            
            st.rerun()
