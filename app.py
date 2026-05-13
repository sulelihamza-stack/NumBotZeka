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
    st.error("❌ 'duckduckgo-search' kütüphanesi eksik.\nTerminal: pip install duckduckgo-search")
    st.stop()

try:
    from groq import Groq
except ImportError:
    st.error("❌ 'groq' kütüphanesi eksik.\nTerminal: pip install groq")
    st.stop()

# --------------------------------------------------------------
# GROQ API ANAHTARI (DOĞRUDAN KOD İÇİNDE)
# --------------------------------------------------------------
GROQ_API_KEY = "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"

st.set_page_config(page_title="7. Sınıf Eğitim Asistanı", page_icon="📚", layout="wide")

# --------------------------------------------------------------
# TEMA (CSS) – Aynı
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
.yeni-sohbet-btn:hover { background: #e9ecef; border-color: #adb5bd; }
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
.sohbet-aksiyon { display: flex; gap: 5px; justify-content: flex-end; margin-top: -28px; margin-bottom: 8px; }
.sohbet-aksiyon button { background: none !important; border: none !important; font-size: 16px !important; padding: 0 5px !important; width: auto !important; color: #6c757d; }
.sohbet-aksiyon button:hover { color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ (aynen)
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["Selam! Nasılsın? Bugün hangi konuda çalışmak istiyorsun?", "Hey, merhaba! Sana nasıl yardımcı olabilirim?", "Selam! Bugün birlikte harika şeyler öğrenebiliriz!"],
    "nasilsin": ["İyiyim, teşekkür ederim! Sen nasılsın?", "Gayet iyiyim! Derse hazır mısın?", "Harika hissediyorum! Nasılsın sen?"],
    "iyi": ["Ne güzel! O zaman hadi bir şeyler öğrenelim mi?", "Süper! Enerjin yerindeyken ders çalışalım!", "Harika! Hangi konuyu merak ediyorsun?"],
    "kötü": ["Üzgünüm... Birlikte ders çalışırsak belki neşelenirsin, dener misin?", "Geçer, merak etme! Birlikte öğrenelim mi?"],
    "teşekkür": ["Rica ederim! Başka sorun olursa buradayım.", "Ne demek! Her zaman yardımcı olmaya hazırım."],
    "günaydın": ["Günaydın! Umarım güzel bir gün geçiriyorsundur. Bugün ne öğrenmek istersin?", "Günaydın! Yeni bilgiler için hazır mısın?"],
    "iyi geceler": ["İyi geceler! Bugün çok şey öğrendin, tebrikler. Yarın görüşürüz!", "İyi geceler! Öğrendiklerini tekrar etmeyi unutma!"],
    "kim": ["Ben 7. Sınıf Eğitim Asistanı'yım! Ders konularında yardımcı olurum.", "Yapay zeka asistanıyım. Sorularını yanıtlamak için buradayım."],
    "ne yapabilirsin": ["Sana 7. sınıf ders konularında detaylı cevaplar verebilirim! Fotosentez, matematik, tarih... Sor!", "Her ders sorusunu araştırıp sana anlaşılır şekilde cevaplarım."],
    "sıkıldım": ["Anlıyorum, ama çalışmadan olmaz! Hadi bir soru sor, belki ilginç bir şey öğreniriz.", "Sıkılmak normal! Merak ettiğin bir konuyu sormaya ne dersin?"],
    "default": ["Anlıyorum! Ders konusunda bir sorun varsa yardımcı olabilirim.", "Hmm, tam anlayamadım. Bir ders sorusu sormak ister misin?", "İlginç! Bunu biraz açar mısın ya da ders sorusu sor?"]
}
DERS_DISI_UYARI = ["Seninle sohbet etmek güzel ama çok fazla ders dışına çıktık! Hadi bir ders sorusu soralım.", "Fark ettim ki epeydir ders konuşmuyoruz. Asıl görevim seni öğretmek!", "Sohbetimiz güzel ama ders asistanı olarak seni çok oyaladım! Hadi bir soru sor."]
DIYALOG_ANAHTAR = {
    "selam": ["selam","merhaba","hey","naber","selamlar"],
    "nasilsin": ["nasılsın","nasılsınız","iyi misin","ne yapıyorsun"],
    "iyi": ["iyiyim","iyi","güzel","harika","süper","fena değil"],
    "kötü": ["kötüyüm","kötü","berbat","üzgün","mutsuz"],
    "teşekkür": ["teşekkür","sağ ol","mersi","thanks"],
    "günaydın": ["günaydın","iyi sabahlar"],
    "iyi geceler": ["iyi geceler","iyi akşamlar"],
    "kim": ["kimsin","nesin","adın ne"],
    "ne yapabilirsin": ["ne yapabilirsin","ne yaparsın","nasıl yardım"],
    "sıkıldım": ["sıkıldım","bıktım","canım sıkılıyor"]
}
EGITIM_ANAHTAR = ["nedir","nasıl","ne zaman","nerede","açıkla","anlat","öğret","formül","hesapla","çöz","farkı","tanım","örnek","konu","ders","matematik","fen","tarih"]

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
# KAYNAK GÜVENİLİRLİĞİ
# --------------------------------------------------------------
def guvenilirlik_puani(url: str) -> int:
    u = url.lower()
    if any(d in u for d in [".gov.tr", ".edu.tr", "meb", "eba"]): return 10
    if any(d in u for d in ["wikipedia", "britannica", "khanacademy"]): return 8
    if "ders" in u or "egitim" in u: return 5
    return 1

def kaynaklari_sirala(kaynaklar: list[dict]) -> list[dict]:
    for k in kaynaklar:
        k["guven"] = guvenilirlik_puani(k["url"])
    kaynaklar.sort(key=lambda x: x["guven"], reverse=True)
    return kaynaklar

# --------------------------------------------------------------
# ARAMA + ÖNBELK
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def ddg_ara_cached(sorgu: str, n: int = 6) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(sorgu, region="tr-tr", max_results=n))
    except Exception as e:
        st.error(f"Arama hatası: {e}")
        return []

def sayfa_metni_al(url: str, max_k: int = 4000) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=7)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","nav","footer","header","aside","form"]):
            tag.decompose()
        parcalar = [el.get_text(" ", strip=True) for el in soup.find_all(["p","li","h2","h3","h4"])]
        return " ".join(p for p in parcalar if len(p)>35)[:max_k]
    except:
        return ""

def sayfalari_paralel_cek(url_list: list[str]) -> list[str]:
    metinler = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(sayfa_metni_al, url): url for url in url_list}
        for future in as_completed(future_to_url):
            metin = future.result()
            if metin:
                metinler.append(metin)
            time.sleep(0.1)
    return metinler

# --------------------------------------------------------------
# FALLBACK ÖZETLEME (TF‑IDF)
# --------------------------------------------------------------
def cumlelere_bol(metin: str) -> list[str]:
    return [c.strip() for c in re.split(r'(?<=[.!?])\s+', metin) if len(c.strip())>30]

def tfidf_ozetle(soru: str, ham_metin: str, max_cumle: int = 6) -> str:
    cumleler = cumlelere_bol(ham_metin)
    if not cumleler:
        return "İlgili içerik bulunamadı."
    dokumanlar = [soru] + cumleler
    vectorizer = TfidfVectorizer(stop_words="turkish", max_features=500)
    tfidf_mat = vectorizer.fit_transform(dokumanlar)
    soru_vec = tfidf_mat[0:1]
    cumle_vecs = tfidf_mat[1:]
    benzerlikler = cosine_similarity(soru_vec, cumle_vecs).flatten()
    en_iyi_idxler = np.argsort(benzerlikler)[::-1][:max_cumle]
    secilen = [cumleler[i] for i in en_iyi_idxler if benzerlikler[i]>0.1]
    if not secilen:
        secilen = cumleler[:max_cumle]
    goruldu = set()
    temiz = []
    for c in secilen:
        kisalt = c[:60].lower()
        if kisalt not in goruldu:
            goruldu.add(kisalt)
            if len(c)>300: c=c[:297]+"..."
            temiz.append(c)
    return "\n\n".join(temiz)

# --------------------------------------------------------------
# GROQ SENTEZ
# --------------------------------------------------------------
def groq_sentezle(soru: str, ham_metin: str) -> str:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sistem = (
            "Sen 7. sınıf öğrencilerine yardımcı olan bir eğitim asistanısın. "
            "Verilen ham içeriğe göre soruyu cevapla. Gereksiz reklam ve navigasyon metinlerini yok say. "
            "Kendi cümlelerinle, sade ve anlaşılır Türkçe yaz. Cevabı 3-5 kısa paragraf veya madde halinde ver. "
            "Kaynak URL veya site adı kesinlikle yazma."
        )
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem},
                {"role": "user", "content": f"Soru: {soru}\n\nHam içerik:\n{ham_metin[:4000]}"}
            ],
            max_tokens=600,
            temperature=0.4,
        )
        return yanit.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Groq hatası: {e} → Fallback kullanılıyor.")
        return None

# --------------------------------------------------------------
# GÖRSEL / VİDEO
# --------------------------------------------------------------
def konu_icin_gorsel(soru: str) -> str | None:
    try:
        with DDGS() as ddgs:
            sonuclar = list(ddgs.images(soru, max_results=1))
            return sonuclar[0]["image"] if sonuclar else None
    except:
        return None

def konu_icin_video_linki(soru: str) -> str:
    return f"https://www.youtube.com/results?search_query=7.+sınıf+{soru.replace(' ','+')}"

# --------------------------------------------------------------
# CEVAP OLUŞTUR (ANA)
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def cevap_olustur(soru: str):
    sonuclar = ddg_ara_cached(f"{soru} 7. sınıf", n=6)
    if len(sonuclar) < 3:
        sonuclar += ddg_ara_cached(f"{soru} nedir açıkla detaylı", n=4)
    if not sonuclar:
        return "Üzgünüm, şu an internet erişiminde sorun var.", [], None, ""
    ham_parcalar = [r.get("body","") for r in sonuclar if r.get("body")]
    url_listesi = [r["href"] for r in sonuclar[:4] if r.get("href")]
    if url_listesi:
        sayfa_metinleri = sayfalari_paralel_cek(url_listesi)
        ham_parcalar.extend(sayfa_metinleri)
    kaynaklar = []
    for r in sonuclar[:6]:
        url = r.get("href","")
        if url:
            kaynaklar.append({"url": url, "baslik": r.get("title", url)})
    kaynaklar = kaynaklari_sirala(kaynaklar)
    if not ham_parcalar:
        return "İçerik çıkarılamadı, lütfen tekrar dene.", kaynaklar[:5], None, ""
    ham_metin = "\n\n".join(ham_parcalar)
    sentez = groq_sentezle(soru, ham_metin)
    if not sentez:
        sentez = tfidf_ozetle(soru, ham_metin)
    gorsel_url = konu_icin_gorsel(soru)
    video_link = konu_icin_video_linki(soru)
    return sentez, kaynaklar[:5], gorsel_url, video_link

# --------------------------------------------------------------
# OTURUM (SESSION) BAŞLAT – JSON KULLANILMAZ
# --------------------------------------------------------------
def yeni_sohbet_olustur(sohbet_adi: str) -> dict:
    return {"id": int(time.time()*1000), "baslik": sohbet_adi, "mesajlar": [], "olusturma_zamani": time.time()}

# Session state
if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = None
if "isim_bekleniyor" not in st.session_state:
    st.session_state.isim_bekleniyor = True
if "sohbetler" not in st.session_state:
    # Başlangıçta boş liste, örnek bir sohbet eklenebilir ama boş da olabilir
    st.session_state.sohbetler = []
if "aktif_id" not in st.session_state:
    st.session_state.aktif_id = None
if "disi_sayac" not in st.session_state:
    st.session_state.disi_sayac = 0
if "duzenlenen_sohbet_id" not in st.session_state:
    st.session_state.duzenlenen_sohbet_id = None

def aktif_sohbet():
    for s in st.session_state.sohbetler:
        if s["id"] == st.session_state.aktif_id:
            return s
    return None

# --------------------------------------------------------------
# SIDEBAR: sohbet listesi, yeni sohbet (direkt), silme/düzenleme
# --------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-baslik">Sohbetler</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("➕", key="yeni_sohbet_btn", help="Yeni sohbet"):
            yeni = yeni_sohbet_olustur("Yeni Sohbet")
            st.session_state.sohbetler.insert(0, yeni)
            st.session_state.aktif_id = yeni["id"]
            st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    for s in st.session_state.sohbetler:
        aktif = (s["id"] == st.session_state.aktif_id)
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
                if st.button("Evet", key=f"del_{s['id']}"):
                    st.session_state.sohbetler = [x for x in st.session_state.sohbetler if x["id"] != s["id"]]
                    if st.session_state.aktif_id == s["id"]:
                        st.session_state.aktif_id = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
                    st.session_state.duzenlenen_sohbet_id = None
                    st.rerun()
    if st.session_state.duzenlenen_sohbet_id:
        duzenlenen = next((s for s in st.session_state.sohbetler if s["id"]==st.session_state.duzenlenen_sohbet_id), None)
        if duzenlenen:
            yeni_ad = st.text_input("Yeni ad:", value=duzenlenen["baslik"], key="edit_input")
            if st.button("Kaydet"):
                duzenlenen["baslik"] = yeni_ad.strip() or "İsimsiz Sohbet"
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
            if st.button("İptal"):
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='position:absolute;bottom:16px;left:0;right:0;text-align:center;font-size:13px;color:#6c757d;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA EKRANI
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>Hoş Geldin!</h2><p>Sana nasıl hitap edeyim?</p></div>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        isim = st.text_input("Adın:", placeholder="Adını yaz...", key="isim_girdi", label_visibility="collapsed")
        if st.button("Devam Et", key="isim_btn"):
            if isim.strip():
                st.session_state.kullanici_adi = isim.strip()
                st.session_state.isim_bekleniyor = False
                # Başlangıçta bir sohbet yoksa oluştur
                if not st.session_state.sohbetler:
                    yeni = yeni_sohbet_olustur("Yeni Sohbet")
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
st.markdown(f'<div class="ana-baslik">Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">2026 MEB Müfredatı · İnternetten anlık, Groq ile sentezlenmiş cevaplar</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

sohbet = aktif_sohbet()
if sohbet is None:
    st.info("Başlamak için yeni bir sohbet oluşturun (sol menüdeki ➕ butonu).", icon="💬")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "Cevap" if m.get("tur")=="egitim" else "Sohbet"
            st.markdown(f'<div class="mesaj-asistan"><div class="asistan-tur">{tur_yazi}</div><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            if m.get("kaynaklar"):
                kaynak_html = '<div class="kaynak-alan">'
                for i,k in enumerate(m["kaynaklar"],1):
                    rozet = " 🛡️" if k.get("guven",0)>=8 else ""
                    kaynak_html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">{i}. {k["baslik"][:42]}{rozet}</a>'
                kaynak_html += "</div>"
                st.markdown(kaynak_html, unsafe_allow_html=True)
            if m.get("gorsel"):
                st.image(m["gorsel"], width=200, caption="Konuyla ilgili görsel")
            if m.get("video_link"):
                st.markdown(f'<div class="video-oneri">🎬 <a href="{m["video_link"]}" target="_blank">YouTube’da ara →</a></div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    girdi = st.chat_input(f"Bir şeyler yaz, {ad}...")
    if girdi:
        mesaj = girdi.strip()
        if not mesaj:
            st.stop()
        sohbet["mesajlar"].append({"rol": "kullanici", "icerik": mesaj})
        if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
            sohbet["baslik"] = mesaj[:30] + ("..." if len(mesaj)>30 else "")
        tur = mesaj_turu_tespit(mesaj)
        if tur == "egitim":
            st.session_state.disi_sayac = 0
            with st.spinner("Araştırılıyor ve analiz ediliyor..."):
                cevap, kaynaklar, gorsel_url, video_link = cevap_olustur(mesaj)
            sohbet["mesajlar"].append({"rol":"asistan","icerik":cevap,"kaynaklar":kaynaklar,"tur":"egitim","gorsel":gorsel_url,"video_link":video_link})
        else:
            st.session_state.disi_sayac += 1
            cevap = diyalog_cevap(tur)
            uyari = None
            if st.session_state.disi_sayac >= 3:
                uyari = random.choice(DERS_DISI_UYARI)
                st.session_state.disi_sayac = 0
            sohbet["mesajlar"].append({"rol":"asistan","icerik":cevap,"kaynaklar":[],"tur":"diyalog","uyari":uyari})
        st.rerun()
