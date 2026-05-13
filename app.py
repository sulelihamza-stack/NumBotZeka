import streamlit as st
import time
import re
import random
from duckduckgo_search import DDGS
from groq import Groq

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

.kaynak-kart { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 20px; padding: 6px 14px; font-size: 12px; text-decoration: none; margin-right: 8px; margin-bottom: 8px; display: inline-block; transition: all 0.3s; color: #aaa; font-weight: 500; }
.kaynak-kart:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; transform: translateY(-2px); }

.uyari-kutu { background: rgba(255,200,100,0.1); border: 1px solid rgba(255,200,100,0.3); border-radius: 15px; padding: 10px 16px; margin-top: 12px; color: #ffd966; font-size: 13px; }

.isim-ekran { max-width: 450px; margin: 100px auto; background: #1a1a2e; border-radius: 30px; padding: 40px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border: 1px solid #2a2a3e; }
.isim-ekran h2 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

[data-testid="stChatInput"] { border: 2px solid #2a2a3e !important; border-radius: 30px !important; background: #1a1a2e !important; }
[data-testid="stChatInput"] textarea { color: white !important; background: #1a1a2e !important; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, sana nasıl yardımcı olabilirim?", "👋 Merhaba! NumBot olarak derslerinde sana destek olmak için buradayım.", "🌟 Hey! NumBot'la ders çalışmaya hazır mısın?"],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın?", "🎯 Harika hissediyorum! Senden naber?", "📚 Çok iyiyim, seni bekliyordum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu sormaya ne dersin?", "⭐ Süper! Hadi öğrenmeye başlayalım.", "🚀 Harika! Enerjin yerindeyken ders çalışmak için en iyi zaman!"],
    "kötü": ["😔 Üzgünüm... Birlikte ders çalışırsak belki moralin düzelir.", "💪 Geçer, merak etme! Hadi bir soru çözelim.", "🌈 Her şey geçer! Öğrenmek insanı mutlu eder."],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek! Her zaman yardımcı olmaya hazırım.", "🎓 Estağfurullah! Öğrenmek için soru sormaya devam!"],
    "kim": ["🤖 Ben NumBot! 7. sınıf derslerinde sana yardımcı olmak için tasarlanmış bir yapay zekayım.", "🧠 NumBot - 7. sınıf eğitim asistanın!", "✨ Ben NumBot, yapay zeka destekli eğitim asistanın."],
    "ne yapabilirsin": ["🔍 Sana 7. sınıf konularını anlatabilirim! Matematik, fen, Türkçe, İngilizce, sosyal bilgiler... Sorularını yanıtlayabilirim.", "📚 Her ders sorusunu cevaplayabilirim. Ayrıca internette araştırıp kaynak ve video önerebilirim!"],
    "sıkıldım": ["😊 Sıkılmak normal! Hadi bir soru sor, belki ilginç bir şey keşfederiz.", "🎮 Ders çalışmak bazen sıkıcı gelebilir ama küçük bir soruyla başlayalım."],
    "default": ["💭 Ders konusunda bir sorun mu var? Matematik, fen, Türkçe, İngilizce veya sosyal bilgiler sorusu sorabilirsin.", "📖 Bir ders sorusu sormak ister misin? Sana yardımcı olmaktan mutluluk duyarım!"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber", "selamlar", "hello", "hi"],
    "nasilsin": ["nasılsın", "nasılsınız", "iyi misin", "ne yapıyorsun"],
    "iyi": ["iyiyim", "iyi", "güzel", "harika", "süper", "fena değil"],
    "kötü": ["kötüyüm", "kötü", "berbat", "üzgün", "mutsuz"],
    "teşekkür": ["teşekkür", "teşekkürler", "sağ ol", "mersi", "thanks"],
    "kim": ["kimsin", "nesin", "adın ne", "sen kimsin"],
    "ne yapabilirsin": ["ne yapabilirsin", "ne yaparsın", "nasıl yardım", "yeteneklerin neler"],
    "sıkıldım": ["sıkıldım", "bıktım", "canım sıkılıyor", "sıkıcı"]
}

# --------------------------------------------------------------
# EĞİTİM ANAHTAR KELİMELERİ (TÜM DERSLER)
# --------------------------------------------------------------
EGITIM_ANAHTAR = [
    # MATEMATİK
    "tam sayı", "tam sayılar", "denklem", "eşitsizlik", "oran", "orantı", "yüzde", "faiz",
    "rasyonel sayı", "ondalık", "kesir", "üs", "köklü", "cebir", "bilinmeyen", "formül",
    "açı", "üçgen", "dikdörtgen", "kare", "çokgen", "çember", "daire", "alan", "çevre", "hacim", "veri", "grafik", "olasılık",
    "çarpan", "kat", "bölen", "bölme", "çarpma", "toplama", "çıkarma", "işlem",
    
    # TÜRKÇE
    "zarf", "zarflar", "zamir", "zamirler", "fiil", "fiiller", "isim", "sıfat", "edat", "bağlaç", 
    "noktalama", "yazım", "ek", "kök", "cümle", "paragraf", "anlam", "sözcük",
    
    # FEN BİLİMLERİ
    "fotosentez", "mitoz", "mayoz", "solunum", "sindirim", "dolaşım", "boşaltım",
    "hücre", "organel", "çekirdek", "dna", "kalıtım", "gen", "kromozom",
    "basınç", "elektrik", "akım", "gerilim", "direnç", "manyetizma", "ısı", "sıcaklık",
    
    # SOSYAL BİLGİLER
    "tarih", "coğrafya", "iklim", "harita", "nüfus", "vatandaşlık", "cumhuriyet", "devlet",
    "uygarlık", "savaş", "antlaşma", "bölge", "göç", "ekonomi",
    
    # İNGİLİZCE
    "simple present", "present continuous", "past tense", "future tense",
    "pronoun", "verb", "noun", "adjective", "adverb",
    
    # GENEL
    "nedir", "nasıl", "ne zaman", "nerede", "açıkla", "anlat", "öğret", "çöz",
    "tanım", "örnek", "konu", "ders", "neden", "nedenleri", "sonuçları"
]

def mesaj_turu_tespit(mesaj: str) -> str:
    m = mesaj.lower().strip()
    # Önce eğitim kontrolü
    if any(k in m for k in EGITIM_ANAHTAR) or len(m.split()) >= 3:
        return "egitim"
    # Sonra diyalog kontrolü
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    return "diyalog:default"

def diyalog_cevap(tur: str) -> str:
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

# --------------------------------------------------------------
# KONU BAŞLIĞINI ÇIKAR
# --------------------------------------------------------------
def konu_basligi_cikar(soru: str) -> str:
    soru_lower = soru.lower()
    # Matematik
    if "tam sayı" in soru_lower:
        return "Tam Sayılar"
    if "denklem" in soru_lower:
        return "Denklemler"
    if "oran" in soru_lower:
        return "Oran ve Orantı"
    if "yüzde" in soru_lower:
        return "Yüzdeler"
    # Türkçe
    if "zarf" in soru_lower:
        return "Zarflar (Dilbilgisi)"
    if "zamir" in soru_lower:
        return "Zamirler"
    if "fiil" in soru_lower:
        return "Fiiller"
    if "isim" in soru_lower:
        return "İsimler"
    # Fen
    if "fotosentez" in soru_lower:
        return "Fotosentez"
    if "mitoz" in soru_lower:
        return "Mitoz Bölünme"
    if "hücre" in soru_lower:
        return "Hücre ve Organeller"
    # Yoksa ilk 30 karakter
    return soru[:30] + ("..." if len(soru) > 30 else "")

# --------------------------------------------------------------
# DUCKDUCKGO ARAMA
# --------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def duckduckgo_ara(sorgu: str, n: int = 6):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(f"{sorgu} 7. sınıf", region="tr-tr", max_results=n))
    except Exception as e:
        return []

# --------------------------------------------------------------
# GROQ İLE EĞİTİM CEVABI
# --------------------------------------------------------------
def groq_egitim_cevabi(soru: str):
    # DuckDuckGo'da ara
    kaynaklar = duckduckgo_ara(soru, n=5)
    
    arama_metni = ""
    if kaynaklar:
        for r in kaynaklar:
            if r.get("body"):
                arama_metni += r.get("body", "") + "\n\n"
    
    if not arama_metni:
        return "🔍 Üzgünüm, internette bu konuda kaynak bulamadım. Lütfen sorunu daha açık yaz veya farklı bir konu sor.", []
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        sistem_mesaji = """Sen NumBot'sun, 7. sınıf öğrencilerine yardım eden bir eğitim asistanısın.

ÖNEMLİ KURALLAR:
1. "Tam sayılar" MATEMATİK konusudur (pozitif, negatif sayılar, sayı doğrusu, işlemler)
2. "Zarflar" TÜRKÇE dilbilgisi konusudur (fiillerin durumunu, zamanını, miktarını belirten kelimeler)
3. SAKIN bu iki konuyu birbirine karıştırma!
4. Verilen arama sonuçlarına göre soruyu cevapla.
5. Cevabı 7. sınıf seviyesinde, anlaşılır Türkçe yaz.
6. Örneklerle destekle.
7. Madde işaretleri kullan."""
        
        kullanici_mesaji = f"Soru: {soru}\n\nİnternetten bulduğum bilgiler:\n{arama_metni[:4500]}"
        
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem_mesaji},
                {"role": "user", "content": kullanici_mesaji}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        cevap = yanit.choices[0].message.content.strip()
        
        # Kaynak linklerini ekle
        if kaynaklar:
            cevap += "\n\n---\n📚 **Kaynaklar:**\n"
            for k in kaynaklar[:4]:
                if k.get("url") and k.get("title"):
                    cevap += f"• [{k.get('title')}]({k.get('url')})\n"
        
        return cevap, kaynaklar
        
    except Exception as e:
        return f"❌ Bağlantı hatası. Lütfen daha sonra tekrar dene.", []

# --------------------------------------------------------------
# YOUTUBE LİNKİ
# --------------------------------------------------------------
def video_linki(soru: str) -> str:
    sorgu = soru.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query=7.+sınıf+{sorgu}"

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

def sohbeti_sil(sohbet_id):
    st.session_state.sohbetler = [s for s in st.session_state.sohbetler if s["id"] != sohbet_id]
    if st.session_state.aktif_id == sohbet_id:
        st.session_state.aktif_id = st.session_state.sohbetler[0]["id"] if st.session_state.sohbetler else None
    st.rerun()

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
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(f"📄 {s['baslik'][:25]}", key=f"sb_{s['id']}"):
                st.session_state.aktif_id = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                sohbeti_sil(s["id"])
    
    st.markdown("---")
    st.caption("🤖 NumBot | 7. Sınıf Eğitim Asistanı")
    
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='margin-top: 10px; text-align: center; padding: 10px; background: rgba(102,126,234,0.1); border-radius: 15px;'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# İSİM SORMA EKRANI
# --------------------------------------------------------------
if st.session_state.isim_bekleniyor:
    st.markdown('<div class="isim-ekran"><h2>🤖 Hoş Geldin!</h2><p>Ben NumBot, sana nasıl hitap edebilirim?</p></div>', unsafe_allow_html=True)
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
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">NumBot | İnternette Araştırma Yapar | Kaynak ve Video Önerir</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Yeni bir sohbet başlatmak için sol menüdeki **➕ Yeni Sohbet** butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "📝 NumBot (Eğitim)" if m.get("tur") == "egitim" else "💬 NumBot (Sohbet)"
            st.markdown(f'<div class="mesaj-asistan"><div class="asistan-tur">{tur_yazi}</div><div class="cevap-kutu">{m["icerik"]}</div>', unsafe_allow_html=True)
            
            if m.get("kaynaklar"):
                src_html = '<div style="margin-top: 10px;">'
                for i, k in enumerate(m["kaynaklar"][:3], 1):
                    if k.get("url"):
                        src_html += f'<a class="kaynak-kart" href="{k["url"]}" target="_blank">🔗 Kaynak {i}</a> '
                src_html += '</div>'
                st.markdown(src_html, unsafe_allow_html=True)
            
            if m.get("video_link"):
                st.markdown(f'<div style="margin-top: 10px;"><a class="kaynak-kart" href="{m["video_link"]}" target="_blank" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white;">🎬 YouTube\'da Ara</a></div>', unsafe_allow_html=True)
            
            if m.get("uyari"):
                st.markdown(f'<div class="uyari-kutu">⚠️ {m["uyari"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    girdi = st.chat_input(f"{ad}, sorunu yazabilirsin...")
    if girdi:
        msg = girdi.strip()
        if msg:
            sohbet["mesajlar"].append({"rol": "kullanici", "icerik": msg})
            
            if sohbet["baslik"] == "Yeni Sohbet" and len(sohbet["mesajlar"]) == 1:
                sohbet["baslik"] = konu_basligi_cikar(msg)
            
            tur = mesaj_turu_tespit(msg)
            
            if tur == "egitim":
                st.session_state.disi_sayac = 0
                with st.spinner("🔍 NumBot internette araştırıyor..."):
                    cevap, kaynaklar = groq_egitim_cevabi(msg)
                    video_link = video_linki(msg)
                sohbet["mesajlar"].append({
                    "rol": "asistan", "icerik": cevap,
                    "kaynaklar": kaynaklar, "video_link": video_link, "tur": "egitim"
                })
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice([
                        "💡 Sohbet güzel ama biraz ders sorusu soralım mı?",
                        "📖 Ders dışına çıktık, hadi bir soru sor.",
                        "🎯 NumBot olarak asıl görevim derslerinde sana yardımcı olmak!"
                    ])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "diyalog", "uyari": uyari})
            
            st.rerun()
