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
# GROQ API ANAHTARI
# --------------------------------------------------------------
GROQ_API_KEY = "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"

st.set_page_config(page_title="NumBot - 7. Sınıf Eğitim Asistanı", page_icon="🤖", layout="wide")

# --------------------------------------------------------------
# SİYAH TEMA (CSS)
# --------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp, [data-testid="stAppViewContainer"] { background: #000000 !important; }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid #2a2a3e !important; }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }

.sb-baslik { font-size: 1.2rem; font-weight: 700; padding: 15px 16px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin: 10px; color: white !important; }

[data-testid="stSidebar"] button { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #e0e0e0 !important; border-radius: 10px !important; transition: all 0.3s !important; }
[data-testid="stSidebar"] button:hover { background: rgba(255,255,255,0.15) !important; transform: translateX(5px); }

.ana-baslik { font-size: 2rem; font-weight: 700; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 20px 0 10px 0; }
.ana-alt { font-size: 0.9rem; color: #888; text-align: center; margin-bottom: 30px; }

.mesaj-kullanici { display: flex; justify-content: flex-end; margin: 15px 0; animation: fadeIn 0.5s; }
.mesaj-kullanici span { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 20px; border-radius: 25px 25px 5px 25px; max-width: 70%; box-shadow: 0 4px 15px rgba(102,126,234,0.3); font-size: 15px; line-height: 1.5; }

.mesaj-asistan { margin: 15px 0; animation: fadeIn 0.5s; }
.asistan-tur { font-size: 11px; color: #888; margin-bottom: 5px; padding-left: 15px; font-weight: 600; letter-spacing: 1px; }
.cevap-kutu { background: #1a1a2e; border-radius: 25px 25px 25px 5px; padding: 16px 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); line-height: 1.7; color: #e0e0e0; font-size: 15px; border: 1px solid #2a2a3e; }

.kaynak-alan { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
.kaynak-kart { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 20px; padding: 6px 14px; font-size: 12px; text-decoration: none; transition: all 0.3s; color: #aaa; font-weight: 500; display: inline-block; }
.kaynak-kart:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; transform: translateY(-2px); }

.uyari-kutu { background: rgba(255,200,100,0.1); border: 1px solid rgba(255,200,100,0.3); border-radius: 15px; padding: 10px 16px; margin-top: 12px; color: #ffd966; font-size: 13px; }

.video-oneri a { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 6px 14px; border-radius: 20px; text-decoration: none; font-size: 12px; color: white; display: inline-block; margin-top: 10px; transition: all 0.3s; }
.video-oneri a:hover { transform: scale(1.05); }

[data-testid="stChatInput"] { border: 2px solid #2a2a3e !important; border-radius: 30px !important; background: #1a1a2e !important; }
[data-testid="stChatInput"] textarea { color: white !important; background: #1a1a2e !important; }

.isim-ekran { max-width: 450px; margin: 100px auto; background: #1a1a2e; border-radius: 30px; padding: 40px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border: 1px solid #2a2a3e; }
.isim-ekran h2 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
.isim-ekran p { color: #aaa; }

.stTextInput input { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; color: white !important; border-radius: 10px !important; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

#MainMenu, footer, header { visibility: hidden; }
hr { border-color: #2a2a3e; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, sana nasıl yardımcı olabilirim?", "👋 Merhaba! NumBot derslerinde sana destek olmak için burada."],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu sormaya ne dersin?", "⭐ Süper! Hadi öğrenmeye başlayalım."],
    "kötü": ["😔 Üzgünüm... Birlikte ders çalışırsak belki moralin düzelir.", "💪 Geçer, merak etme!"],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek!"],
    "günaydın": ["🌅 Günaydın! Verimli bir gün geçirmeni dilerim.", "☀️ Günaydın! Yeni bilgiler öğrenmeye hazır mısın?"],
    "iyi geceler": ["🌙 İyi geceler! Yarın görüşürüz.", "⭐ İyi geceler! Öğrendiklerini tekrar etmeyi unutma."],
    "kim": ["🤖 Ben NumBot! 7. sınıf yapay zeka eğitim asistanın.", "🧠 NumBot - eğitim asistanın!"],
    "ne yapabilirsin": ["🔍 Sana 7. sınıf konularını anlatabilirim! Matematik, fen, Türkçe, İngilizce, sosyal bilgiler... Sorularını yanıtlayabilirim.", "📚 Her ders sorusunu araştırıp cevaplarım. Kaynak ve video da öneririm."],
    "sıkıldım": ["😊 Sıkılmak normal! Hadi bir soru sor, belki ilginç bir şey keşfederiz.", "🎮 Ders çalışmak bazen sıkıcı gelebilir ama küçük bir soruyla başlayalım."],
    "default": ["💭 Ders konusunda bir sorun mu var? Matematik, fen, Türkçe, İngilizce veya sosyal bilgiler sorusu sorabilirsin.", "📖 Bir ders sorusu sormak ister misin? Sana yardımcı olmaktan mutluluk duyarım!"]
}

DERS_DISI_UYARI = [
    "💡 Sohbet güzel ama biraz ders sorusu soralım mı?",
    "📖 Ders dışına çıktık, hadi bir soru sor.",
    "🎯 NumBot olarak asıl görevim derslerinde sana yardımcı olmak!"
]

DIYALOG_ANAHTAR = {
    "selam": ["selam","merhaba","hey","naber","selamlar","hello","hi"],
    "nasilsin": ["nasılsın","nasılsınız","iyi misin","ne yapıyorsun"],
    "iyi": ["iyiyim","iyi","güzel","harika","süper","fena değil"],
    "kötü": ["kötüyüm","kötü","berbat","üzgün","mutsuz"],
    "teşekkür": ["teşekkür","teşekkürler","sağ ol","mersi","thanks"],
    "günaydın": ["günaydın","iyi sabahlar","sabah"],
    "iyi geceler": ["iyi geceler","iyi akşamlar"],
    "kim": ["kimsin","nesin","adın ne","sen kimsin"],
    "ne yapabilirsin": ["ne yapabilirsin","ne yaparsın","nasıl yardım","yeteneklerin neler"],
    "sıkıldım": ["sıkıldım","bıktım","canım sıkılıyor","sıkıcı"]
}

EGITIM_ANAHTAR = [
    "nedir","nasıl","ne zaman","nerede","açıkla","anlat","öğret","formül","hesapla","çöz","farkı","tanım","örnek","konu","ders",
    "matematik","fen","tarih","coğrafya","ingilizce","türkçe","sosyal",
    "tam sayı","denklem","oran","yüzde","kesir","açı","üçgen","alan","çevre",
    "zarf","zamir","fiil","isim","sıfat","noktalama","cümle",
    "fotosentez","mitoz","hücre","dna","basınç","elektrik"
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
# KALICI HAFIZA (JSON) – SOHBETLER JSON DOSYASINDA SAKLANIR
# --------------------------------------------------------------
SOHBETLER_DOSYA = "sohbetler.json"

def sohbetleri_yukle():
    if os.path.exists(SOHBETLER_DOSYA):
        with open(SOHBETLER_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sohbetleri_kaydet(sohbetler):
    with open(SOHBETLER_DOSYA, "w", encoding="utf-8") as f:
        json.dump(sohbetler, f, ensure_ascii=False, indent=2)

def yeni_sohbet_olustur(sohbet_adi: str) -> dict:
    return {"id": int(time.time()*1000), "baslik": sohbet_adi, "mesajlar": [], "olusturma_zamani": time.time()}

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
    st.markdown('<div class="sb-baslik">💬 Sohbetler</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("➕", key="yeni_sohbet_btn", help="Yeni sohbet"):
            yeni = yeni_sohbet_olustur("Yeni Sohbet")
            st.session_state.sohbetler.insert(0, yeni)
            st.session_state.aktif_id = yeni["id"]
            sohbetleri_kaydet(st.session_state.sohbetler)
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
                    sohbetleri_kaydet(st.session_state.sohbetler)
                    st.session_state.duzenlenen_sohbet_id = None
                    st.rerun()
    if st.session_state.duzenlenen_sohbet_id:
        duzenlenen = next((s for s in st.session_state.sohbetler if s["id"]==st.session_state.duzenlenen_sohbet_id), None)
        if duzenlenen:
            yeni_ad = st.text_input("Yeni ad:", value=duzenlenen["baslik"], key="edit_input")
            if st.button("Kaydet"):
                duzenlenen["baslik"] = yeni_ad.strip() or "İsimsiz Sohbet"
                sohbetleri_kaydet(st.session_state.sohbetler)
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
            if st.button("İptal"):
                st.session_state.duzenlenen_sohbet_id = None
                st.rerun()
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='margin-top:20px;text-align:center;padding:10px;background:rgba(102,126,234,0.1);border-radius:15px;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA EKRANI
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>🤖 Hoş Geldin!</h2><p>Ben NumBot, sana nasıl hitap edebilirim?</p></div>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        isim = st.text_input("", placeholder="Adını yaz...", key="isim_girdi", label_visibility="collapsed")
        if st.button("🎉 Başlayalım!", key="isim_btn"):
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
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">NumBot | İnternetten Anlık, Groq ile Sentezlenmiş Cevaplar | Kaynak ve Video Önerir</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()
if sohbet is None:
    st.info("💡 Başlamak için yeni bir sohbet oluşturun (sol menüdeki ➕ butonu).", icon="💬")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "📝 Cevap" if m.get("tur")=="egitim" else "💬 Sohbet"
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
                st.markdown(f'<div class="video-oneri">🎬 <a href="{m["video_link"]}" target="_blank">YouTube\'da ara →</a></div>', unsafe_allow_html=True)
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    girdi = st.chat_input(f"{ad}, sorunu yazabilirsin...")
    if girdi:
        mesaj = girdi.strip()
        if not mesaj:
            st.stop()
        sohbet["mesajlar"].append({"rol": "kullanici", "icerik": mesaj})
        if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
            sohbet["baslik"] = mesaj[:30] + ("..." if len(mesaj)>30 else "")
            sohbetleri_kaydet(st.session_state.sohbetler)
        tur = mesaj_turu_tespit(mesaj)
        if tur == "egitim":
            st.session_state.disi_sayac = 0
            with st.spinner("🔍 Araştırılıyor ve analiz ediliyor..."):
                cevap, kaynaklar, gorsel_url, video_link = cevap_olustur(mesaj)
            sohbet["mesajlar"].append({"rol":"asisten","icerik":cevap,"kaynaklar":kaynaklar,"tur":"egitim","gorsel":gorsel_url,"video_link":video_link})
        else:
           :
            st.session_state.d st.session_state.disi_sisi_sayac += ayac += 1
            ce1
            cevapvap = di = diyalogyalog_cevap_cevap(tur(tur)
)
            uyari =            uyari = None
 None
            if            if st.session_state.d st.session_state.disi_sayacisi_sayac >=  >= 3:
3:
                u                uyariyari = random = random.choice(DERS_DISI_U.choice(DERS_DISI_UYARIYARI)
               )
                st.session_state.d st.session_state.disi_sayac = isi_sayac = 0
0
            sohbet            sohbet["mesajlar"].append({"rol["mesajlar"].append({"rol":"as":"asistan","istan","icerikicerik":cevap":cevap,"k,"kaynakaynaklar":lar":[],"[],"tur":"tur":"diydiyalog","alog","uyariuyari":uy":uyari})
        sohbetari})
        sohbetleri_kleri_kayaydet(st.session_statedet(st.session_state.sohbet.sohbetler)
ler)
        st.rerun()
