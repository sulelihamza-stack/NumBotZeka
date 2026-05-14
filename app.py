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

# --------------------------------------------------------------
# KÜTÜPHANE KONTROLLERİ
# --------------------------------------------------------------
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

# --------------------------------------------------------------
# API KEY (Güvenli sıralama)
# --------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    GROQ_API_KEY = "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"
    st.warning("⚠️ API anahtarı kod içinde (güvenlik riski) - sadece test için.")

st.set_page_config(page_title="7. Sınıf Eğitim Asistanı", page_icon="📚", layout="wide")

# --------------------------------------------------------------
# TEMA CSS (TAMAMI)
# --------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap');
html, body, [data-testid="stAppViewContainer"] { background-color: #ffffff !important; color: #1e1e1e; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e0e0e0 !important; }
[data-testid="stSidebar"] > div { padding: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.sb-baslik { font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 600; color: #2c3e50; padding: 10px 16px 8px 16px; border-bottom: 1px solid #e0e0e0; margin-bottom: 8px; text-align: center; }
.yeni-sohbet-btn { background: #ffffff; border: 1px solid #d0d0d0; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; color: #2c3e50; cursor: pointer; margin: 0 auto 10px auto; transition: all 0.2s; }
.stButton > button { background: #ffffff !important; color: #2c3e50 !important; border: 1px solid #d0d0d0 !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; font-size: 14px !important; padding: 6px 14px !important; transition: all 0.2s !important; width: 100% !important; }
.stButton > button:hover { background: #e9ecef !important; border-color: #adb5bd !important; }
.ana-baslik { font-family: 'Inter', sans-serif; font-size: 1.4rem; font-weight: 600; color: #2c3e50; text-align: center; padding: 16px 0 4px 0; }
.ana-alt { font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #6c757d; text-align: center; margin-bottom: 16px; }
.mesaj-kullanici { display: flex; justify-content: flex-end; margin: 10px 0 4px 0; }
.mesaj-kullanici span { background: #007bff; color: white; padding: 10px 16px; border-radius: 18px 18px 4px 18px; max-width: 75%; line-height: 1.5; }
.mesaj-asistan { margin: 4px 0 16px 0; }
.asistan-tur { font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; border-left: 2px solid #007bff; padding-left: 8px; }
.cevap-kutu { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px 18px 18px 18px; padding: 16px 20px; line-height: 1.75; }
.kaynak-alan { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
.kaynak-kart { background: #ffffff; border: 1px solid #dee2e6; border-radius: 6px; padding: 4px 10px; font-size: 12px; text-decoration: none; transition: border-color 0.2s; }
.kaynak-kart:hover { border-color: #007bff; color: #007bff; }
.uyari-kutu { background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; padding: 10px 14px; margin-top: 8px; color: #856404; }
.goruntu-oneri { margin-top: 12px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.goruntu-oneri img { max-width: 200px; border-radius: 12px; border: 1px solid #ddd; }
.video-oneri a { background: #f1f1f1; padding: 6px 12px; border-radius: 20px; text-decoration: none; font-size: 13px; }
[data-testid="stChatInput"] { background: #ffffff !important; border: 1px solid #ced4da !important; border-radius: 14px !important; }
.isim-ekran { max-width: 420px; margin: 14vh auto 0 auto; background: #ffffff; border: 1px solid #dee2e6; border-radius: 16px; padding: 36px 40px; text-align: center; }
#MainMenu, footer, header { visibility: hidden; }
hr { border-color: #e9ecef; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["Selam! Nasılsın? Bugün hangi konuda çalışmak istiyorsun?", "Hey, merhaba!", "Selam! Hazır mısın?"],
    "nasilsin": ["İyiyim, teşekkür ederim! Sen nasılsın?", "Gayet iyiyim!", "Harika hissediyorum!"],
    "iyi": ["Ne güzel! O zaman hadi bir şeyler öğrenelim mi?", "Süper!", "Harika!"],
    "kötü": ["Üzgünüm bunu duyduğuma... Birlikte ders çalışalım mı?", "Geçer, merak etme!"],
    "teşekkür": ["Rica ederim!", "Ne demek!", "Estağfurullah!"],
    "günaydın": ["Günaydın! Bugün ne öğrenmek istiyorsun?", "Günaydın! Yeni gün, yeni bilgiler!"],
    "iyi geceler": ["İyi geceler! Yarın görüşürüz!", "İyi geceler!"],
    "kim": ["Ben 7. Sınıf Eğitim Asistanı'yım!", "Bir yapay zeka asistanıyım."],
    "ne yapabilirsin": ["Sana 7. sınıf ders konularında yardım ederim!", "Her ders sorusunu cevaplarım."],
    "sıkıldım": ["Hadi bir soru sor, belki ilginç bir şey öğreniriz.", "Sıkılmak normal, dene!"],
    "default": ["Anlıyorum! Bir ders sorusu sormak ister misin?", "Hmm, ders ile ilgili bir soru sorsana!"]
}
DERS_DISI_UYARI = ["Hadi biraz ders çalışalım!", "Bir ders sorusu sorabilir misin?", "Ders asistanıyım, biraz ders konuşalım!"]
DIYALOG_ANAHTAR = {
    "selam": ["selam","merhaba","hey","naber"], "nasilsin": ["nasılsın","nasılsınız","iyi misin"],
    "iyi": ["iyiyim","iyi","güzel","harika"], "kötü": ["kötüyüm","kötü","berbat","üzgün"],
    "teşekkür": ["teşekkür","sağ ol","mersi"], "günaydın": ["günaydın","iyi sabahlar"],
    "iyi geceler": ["iyi geceler","iyi akşamlar"], "kim": ["kimsin","nesin","adın ne"],
    "ne yapabilirsin": ["ne yapabilirsin","ne yaparsın","nasıl yardım"], "sıkıldım": ["sıkıldım","bıktım"]
}
EGITIM_ANAHTAR = ["nedir","nasıl","açıkla","anlat","öğret","formül","hesapla","çöz","tanım","konu","ders","matematik","fen","tarih"]

def mesaj_turu_tespit(mesaj):
    m = mesaj.lower().strip()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if any(k in m for k in EGITIM_ANAHTAR) or len(m.split())>=4:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur):
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

# --------------------------------------------------------------
# MATEMATİK YAKALAMA (KRİTİK: 61+6=67)
# --------------------------------------------------------------
def basit_matematik(soru):
    soru = soru.lower().replace("?", "").replace("kaç", "").replace("eder", "")
    match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', soru)
    if match:
        a = float(match.group(1)); op = match.group(2); b = float(match.group(3))
        if op == '+': return f"{int(a)} + {int(b)} = {int(a+b)}"
        if op == '-': return f"{int(a)} - {int(b)} = {int(a-b)}"
        if op == '*': return f"{int(a)} × {int(b)} = {int(a*b)}"
        if op == '/': return f"{int(a)} ÷ {int(b)} = {a/b:.2f}" if b!=0 else "Sıfıra bölünemez."
    return None

# --------------------------------------------------------------
# KAYNAK GÜVENİLİRLİĞİ
# --------------------------------------------------------------
def guvenilirlik_puani(url):
    url = url.lower()
    if any(d in url for d in [".gov.tr",".edu.tr","meb","eba"]): return 10
    if any(d in url for d in ["wikipedia","britannica","khanacademy"]): return 8
    return 1

def kaynaklari_sirala(kaynaklar):
    for k in kaynaklar: k["guven"] = guvenilirlik_puani(k["url"])
    kaynaklar.sort(key=lambda x: x["guven"], reverse=True)
    return kaynaklar

# --------------------------------------------------------------
# ARAMA ve SAYFA ÇEKME
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def ddg_ara_cached(sorgu, n=6):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(sorgu, region="tr-tr", max_results=n))
    except Exception as e:
        st.error(f"Arama hatası: {e}")
        return []

def sayfa_metni_al(url, max_k=4000):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=7, headers=headers)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","nav","footer","header"]):
            tag.decompose()
        texts = [el.get_text(" ", strip=True) for el in soup.find_all(["p","li","h2","h3","h4"])]
        return " ".join(t for t in texts if len(t)>35)[:max_k]
    except:
        return ""

def sayfalari_paralel_cek(url_list):
    metinler = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(sayfa_metni_al, url) for url in url_list]
        for f in as_completed(futures):
            txt = f.result()
            if txt:
                metinler.append(txt)
            time.sleep(0.1)
    return metinler

# --------------------------------------------------------------
# FALLBACK ÖZETLEME (TF‑IDF)
# --------------------------------------------------------------
def cumlelere_bol(metin):
    return [c.strip() for c in re.split(r'(?<=[.!?])\s+', metin) if len(c.strip())>30]

def tfidf_ozetle(soru, ham_metin, max_cumle=6):
    cumleler = cumlelere_bol(ham_metin)
    if not cumleler:
        return "İlgili içerik bulunamadı."
    dokumanlar = [soru] + cumleler
    vec = TfidfVectorizer(stop_words="turkish", max_features=500)
    tfidf = vec.fit_transform(dokumanlar)
    soru_vec = tfidf[0:1]
    cumle_vecs = tfidf[1:]
    sim = cosine_similarity(soru_vec, cumle_vecs).flatten()
    idx = np.argsort(sim)[::-1][:max_cumle]
    secilen = [cumleler[i] for i in idx if sim[i]>0.1]
    if not secilen:
        secilen = cumleler[:max_cumle]
    goruldu = set()
    temiz = []
    for c in secilen:
        k = c[:60].lower()
        if k not in goruldu:
            goruldu.add(k)
            if len(c)>300:
                c = c[:297]+"..."
            temiz.append(c)
    return "\n\n".join(temiz)

# --------------------------------------------------------------
# GROQ SENTEZ
# --------------------------------------------------------------
def groq_sentezle(soru, ham_metin):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = "Sen 7. sınıf öğrencisine yardım eden bir eğitim asistanısın. Verilen metni kullan, 3-5 paragraf/madde halinde sade Türkçe cevap ver. Kaynak URL yazma."
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":sistem},{"role":"user","content":f"Soru: {soru}\n\nMetin: {ham_metin[:4000]}"}],
            max_tokens=600, temperature=0.4
        )
        return yanit.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Groq hatası: {e}")
        return None

# --------------------------------------------------------------
# GÖRSEL / VİDEO
# --------------------------------------------------------------
def konu_icin_gorsel(soru):
    try:
        with DDGS() as ddgs:
            res = list(ddgs.images(soru, max_results=1))
            return res[0]["image"] if res else None
    except:
        return None

def konu_icin_video_linki(soru):
    return f"https://www.youtube.com/results?search_query=7.+sınıf+{soru.replace(' ','+')}"

# --------------------------------------------------------------
# ANA CEVAP ÜRETİMİ (Önbellekli)
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def cevap_olustur(soru):
    # Önce matematik yakala
    mat = basit_matematik(soru)
    if mat:
        return mat, [], None, ""

    sonuclar = ddg_ara_cached(f"{soru} 7. sınıf", n=6)
    if len(sonuclar)<3:
        sonuclar += ddg_ara_cached(f"{soru} nedir açıkla", n=4)
    if not sonuclar:
        return "İnternet erişim sorunu.", [], None, ""

    ham_parcalar = [r.get("body","") for r in sonuclar if r.get("body")]
    url_list = [r["href"] for r in sonuclar[:4] if r.get("href")]
    if url_list:
        ham_parcalar.extend(sayfalari_paralel_cek(url_list))
    kaynaklar = [{"url": r["href"], "baslik": r.get("title","")} for r in sonuclar[:6] if r.get("href")]
    kaynaklar = kaynaklari_sirala(kaynaklar)
    if not ham_parcalar:
        return "İçerik alınamadı.", kaynaklar[:5], None, ""
    ham_metin = "\n\n".join(ham_parcalar)
    sentez = groq_sentezle(soru, ham_metin)
    if not sentez:
        sentez = tfidf_ozetle(soru, ham_metin)
    gorsel = konu_icin_gorsel(soru)
    vlink = konu_icin_video_linki(soru)
    return sentez, kaynaklar[:5], gorsel, vlink

# --------------------------------------------------------------
# SOHBET YÖNETİMİ (JSON)
# --------------------------------------------------------------
SOHBETLER_DOSYA = "sohbetler.json"
def sohbetleri_yukle():
    if os.path.exists(SOHBETLER_DOSYA):
        with open(SOHBETLER_DOSYA,"r",encoding="utf-8") as f:
            return json.load(f)
    return []
def sohbetleri_kaydet(sohbetler):
    with open(SOHBETLER_DOSYA,"w",encoding="utf-8") as f:
        json.dump(sohbetler, f, ensure_ascii=False, indent=2)
def yeni_sohbet_olustur(baslik):
    return {"id": int(time.time()*1000), "baslik": baslik, "mesajlar": [], "olusturma": time.time()}
def aktif_sohbet():
    for s in st.session_state.sohbetler:
        if s["id"] == st.session_state.aktif_id:
            return s
    return None

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
if "ilk_mesaj_gosterildi" not in st.session_state:
    st.session_state.ilk_mesaj_gosterildi = False
if "duzenlenen_sohbet_id" not in st.session_state:
    st.session_state.duzenlenen_sohbet_id = None

# --------------------------------------------------------------
# SIDEBAR (Yeni sohbet butonu direkt)
# --------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-baslik">Sohbetler</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("➕", key="yeni_sohbet_btn"):
            yeni = yeni_sohbet_olustur("Yeni Sohbet")
            st.session_state.sohbetler.insert(0, yeni)
            st.session_state.aktif_id = yeni["id"]
            sohbetleri_kaydet(st.session_state.sohbetler)
            st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    for s in st.session_state.sohbetler:
        aktif = (s["id"]==st.session_state.aktif_id)
        baslik = s["baslik"][:30] + "..." if len(s["baslik"])>30 else s["baslik"]
        col_ism, col_but = st.columns([4,1])
        with col_ism:
            if st.button(f"{'▸ ' if aktif else '  '}{baslik}", key=f"sb_{s['id']}"):
                st.session_state.aktif_id = s["id"]
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
        with col_but:
            if st.button("✏️", key=f"edit_{s['id']}"):
                st.session_state.duzenlenen_sohbet_id = s["id"]
                st.rerun()
            with st.popover("🗑️"):
                st.write(f"**{s['baslik']}** silinsin mi?")
                if st.button("Evet, sil", key=f"del_{s['id']}"):
                    st.session_state.sohbetler = [x for x in st.session_state.sohbetler if x["id"]!=s["id"]]
                    if st.session_state.aktif_id == s["id"] and st.session_state.sohbetler:
                        st.session_state.aktif_id = st.session_state.sohbetler[0]["id"]
                    sohbetleri_kaydet(st.session_state.sohbetler)
                    st.session_state.duzenlenen_sohbet_id = None
                    st.rerun()
    if st.session_state.duzenlenen_sohbet_id:
        duz = next((s for s in st.session_state.sohbetler if s["id"]==st.session_state.duzenlenen_sohbet_id), None)
        if duz:
            yeni_ad = st.text_input("Yeni ad:", value=duz["baslik"], key="edit_input")
            if st.button("Kaydet"):
                duz["baslik"] = yeni_ad.strip() or "İsimsiz Sohbet"
                sohbetleri_kaydet(st.session_state.sohbetler)
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
            if st.button("İptal"):
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='position:absolute;bottom:16px;text-align:center;width:100%;font-size:13px;color:#6c757d;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>Hoş Geldin!</h2><p>Sana nasıl hitap edeyim?</p></div>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        isim = st.text_input("Adın:", placeholder="Adını yaz...", key="isim_girdi", label_visibility="collapsed")
        if st.button("Devam Et"):
            if isim.strip():
                st.session_state.kullanici_adi = isim.strip()
                st.session_state.isim_bekleniyor = False
                if not st.session_state.sohbetler:
                    yeni = yeni_sohbet_olustur("Yeni Sohbet")
                    st.session_state.sohbetler.append(yeni)
                    st.session_state.aktif_id = yeni["id"]
                    sohbetleri_kaydet(st.session_state.sohbetler)
                st.rerun()
            else:
                st.warning("Lütfen adını yaz.")
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">2026 MEB Müfredatı · İnternetten anlık, Groq + TF‑IDF, görsel/video önerileri</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

sohbet = aktif_sohbet()
if sohbet is None:
    if not st.session_state.ilk_mesaj_gosterildi:
        st.info("Başlamak için yeni bir sohbet oluşturun (sol menüdeki ➕ butonu).", icon="💬")
        st.session_state.ilk_mesaj_gosterildi = True
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "Cevap" if m.get("tur")=="egitim" else "Sohbet"
            st.markdown(f'<div class="mesaj-asistan"><div class="asistan-tur">{tur_yazi}</div><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                html = '<div class="kaynak-alan">'
                for i,k in enumerate(m["kaynaklar"],1):
                    rozet = " 🛡️" if k.get("guven",0)>=8 else ""
                    html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">{i}. {k["baslik"][:42]}{rozet}</a>'
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
            if m.get("gorsel"):
                st.image(m["gorsel"], width=200)
            if m.get("video_link"):
                st.markdown(f'🎬 <a href="{m["video_link"]}" target="_blank">YouTube’da ara</a>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    girdi = st.chat_input(f"Bir şeyler yaz, {ad}...")
    if girdi:
        mesaj = girdi.strip()
        if not mesaj:
            st.stop()
        sohbet["mesajlar"].append({"rol":"kullanici","icerik":mesaj})
        if sohbet["baslik"]=="Yeni Sohbet" and len(sohbet["mesajlar"])==1:
            sohbet["baslik"] = mesaj[:30]+("..." if len(mesaj)>30 else "")
            sohbetleri_kaydet(st.session_state.sohbetler)
        tur = mesaj_turu_tespit(mesaj)
        uyari = None
        if tur == "egitim":
            st.session_state.disi_sayac = 0
            with st.spinner("Araştırılıyor..."):
                cevap, kaynaklar, gorsel, vlink = cevap_olustur(mesaj)
            sohbet["mesajlar"].append({"rol":"asistan","icerik":cevap,"kaynaklar":kaynaklar,"tur":"egitim","uyari":None,"gorsel":gorsel,"video_link":vlink})
        else:
            st.session_state.disi_sayac += 1
            cevap = diyalog_cevap(tur)
            if st.session_state.disi_sayac >= 3:
                uyari = random.choice(DERS_DISI_UYARI)
                st.session_state.disi_sayac = 0
            sohbet["mesajlar"].append({"rol":"asistan","icerik":cevap,"kaynaklar":[],"tur":"diyalog","uyari":uyari,"gorsel":None,"video_link":None})
        sohbetleri_kaydet(st.session_state.sohbetler)
        st.rerun()
