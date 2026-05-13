import streamlit as st
import time
import re
import random
from groq import Groq

# --------------------------------------------------------------
# GROQ API ANAHTARI
# --------------------------------------------------------------
GROQ_API_KEY = "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"

st.set_page_config(page_title="NumBot - 7. Sınıf Eğitim Asistanı", page_icon="🤖", layout="wide")

# --------------------------------------------------------------
# SİYAH TEMA (DARK MODE)
# --------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* Ana arka plan - SİYAH */
.stApp {
    background: #000000 !important;
}

[data-testid="stAppViewContainer"] {
    background: #000000 !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: #000000 !important;
}

/* Sidebar - Koyu gri */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important;
    border-right: 1px solid #2a2a3e !important;
}

[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

.sb-baslik {
    font-size: 1.2rem;
    font-weight: 700;
    padding: 15px 16px;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    margin: 10px;
    color: white !important;
}

/* Sidebar butonları */
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e0e0e0 !important;
    border-radius: 10px !important;
    transition: all 0.3s !important;
}

[data-testid="stSidebar"] button:hover {
    background: rgba(255,255,255,0.15) !important;
    transform: translateX(5px);
}

/* Ana başlık */
.ana-baslik {
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 20px 0 10px 0;
}

.ana-alt {
    font-size: 0.9rem;
    color: #888;
    text-align: center;
    margin-bottom: 30px;
}

/* Sohbet baloncukları */
.mesaj-kullanici {
    display: flex;
    justify-content: flex-end;
    margin: 15px 0;
    animation: fadeIn 0.5s;
}

.mesaj-kullanici span {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 20px;
    border-radius: 25px 25px 5px 25px;
    max-width: 70%;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    font-size: 15px;
    line-height: 1.5;
}

.mesaj-asistan {
    margin: 15px 0;
    animation: fadeIn 0.5s;
}

.asistan-tur {
    font-size: 11px;
    color: #888;
    margin-bottom: 5px;
    padding-left: 15px;
    font-weight: 600;
    letter-spacing: 1px;
}

.cevap-kutu {
    background: #1a1a2e;
    border-radius: 25px 25px 25px 5px;
    padding: 16px 22px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    line-height: 1.7;
    color: #e0e0e0;
    font-size: 15px;
    border: 1px solid #2a2a3e;
}

/* Uyarı kutusu */
.uyari-kutu {
    background: rgba(255,200,100,0.1);
    border: 1px solid rgba(255,200,100,0.3);
    border-radius: 15px;
    padding: 10px 16px;
    margin-top: 12px;
    color: #ffd966;
    font-size: 13px;
    font-weight: 500;
}

/* İsim ekranı */
.isim-ekran {
    max-width: 450px;
    margin: 100px auto;
    background: #1a1a2e;
    border-radius: 30px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    animation: slideUp 0.6s;
    border: 1px solid #2a2a3e;
}

.isim-ekran h2 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.isim-ekran p {
    color: #aaa;
}

/* Chat input */
[data-testid="stChatInput"] {
    border: 2px solid #2a2a3e !important;
    border-radius: 30px !important;
    background: #1a1a2e !important;
    color: white !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
    background: #1a1a2e !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
}

/* Text input */
.stTextInput input {
    background: #1a1a2e !important;
    border: 1px solid #2a2a3e !important;
    color: white !important;
    border-radius: 10px !important;
}

.stTextInput input:focus {
    border-color: #667eea !important;
}

/* Animasyonlar */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(50px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1a1a2e;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #764ba2;
}

/* Markdown ve diğer metinler */
.markdown-text-container p, div, span {
    color: #e0e0e0;
}

/* Info mesajları */
.stAlert {
    background: #1a1a2e !important;
    border: 1px solid #2a2a3e !important;
    color: #e0e0e0 !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #667eea !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# DİYALOG SİSTEMİ (NumBot)
# --------------------------------------------------------------
DIYALOG_KALIPLARI = {
    "selam": ["✨ Selam! Ben NumBot, sana nasıl yardımcı olabilirim?", "👋 Merhaba! NumBot olarak derslerinde sana destek olmak için buradayım.", "🌟 Hey! NumBot'la ders çalışmaya hazır mısın?"],
    "nasilsin": ["💫 İyiyim, teşekkürler! Sen nasılsın? Dersler nasıl gidiyor?", "🎯 Harika hissediyorum! Senden naber?", "📚 Çok iyiyim, seni bekliyordum!"],
    "iyi": ["🎉 Ne güzel! O zaman bir ders sorusu sormaya ne dersin?", "⭐ Süper! Hadi öğrenmeye başlayalım.", "🚀 Harika! Enerjin yerindeyken ders çalışmak için en iyi zaman!"],
    "kötü": ["😔 Üzgünüm... Birlikte ders çalışırsak belki moralin düzelir.", "💪 Geçer, merak etme! Hadi bir soru çözelim.", "🌈 Her şey geçer! Öğrenmek insanı mutlu eder."],
    "teşekkür": ["🤗 Rica ederim! Başka sorun olursa buradayım.", "💖 Ne demek! Her zaman yardımcı olmaya hazırım.", "🎓 Estağfurullah! Öğrenmek için soru sormaya devam!"],
    "kim": ["🤖 Ben NumBot! 7. sınıf derslerinde sana yardımcı olmak için tasarlanmış bir yapay zekayım.", "🧠 NumBot - 7. sınıf eğitim asistanın! Sorularını yanıtlamak için buradayım.", "✨ Ben NumBot, yapay zeka destekli eğitim asistanın. Matematik, fen, Türkçe ve daha fazlası!"],
    "ne yapabilirsin": ["🔍 Sana 7. sınıf konularını anlatabilirim! Matematik, fen, Türkçe, İngilizce, sosyal bilgiler... Sorularını yanıtlayabilirim.", "📚 Her ders sorusunu cevaplayabilirim. Ayrıca örneklerle açıklarım. Denemek ister misin?"],
    "sıkıldım": ["😊 Sıkılmak normal! Hadi bir soru sor, belki ilginç bir şey keşfederiz.", "🎮 Ders çalışmak bazen sıkıcı gelebilir ama küçük bir soruyla başlayalım."],
    "default": ["💭 Ders konusunda bir sorun mu var? Matematik, fen, Türkçe, İngilizce veya sosyal bilgiler sorusu sorabilirsin.", "📖 Bir ders sorusu sormak ister misin? Sana yardımcı olmaktan mutluluk duyarım!"]
}

DIYALOG_ANAHTAR = {
    "selam": ["selam", "merhaba", "hey", "naber", "selamlar", "hello", "hi"],
    "nasilsin": ["nasılsın", "nasılsınız", "iyi misin", "ne yapıyorsun", "naber"],
    "iyi": ["iyiyim", "iyi", "güzel", "harika", "süper", "fena değil", "idare eder"],
    "kötü": ["kötüyüm", "kötü", "berbat", "üzgün", "mutsuz", "keyifsiz"],
    "teşekkür": ["teşekkür", "teşekkürler", "sağ ol", "mersi", "thanks", "eyvallah"],
    "kim": ["kimsin", "nesin", "adın ne", "sensın", "sen kimsin"],
    "ne yapabilirsin": ["ne yapabilirsin", "ne yaparsın", "nasıl yardım", "neler yaparsın", "yeteneklerin neler"],
    "sıkıldım": ["sıkıldım", "bıktım", "canım sıkılıyor", "sıkıcı"]
}

EGITIM_ANAHTAR = [
    "nedir", "nasıl", "ne zaman", "nerede", "açıkla", "anlat", "öğret", "çöz",
    "formül", "hesapla", "farkı", "tanım", "örnek", "konu", "ders", "neden",
    "matematik", "fen", "tarih", "coğrafya", "ingilizce", "türkçe", "sosyal",
    "fotosentez", "mitoz", "denklem", "oran", "yüzde", "açı", "üçgen", "kare"
]

def mesaj_turu_tespit(mesaj: str) -> str:
    m = mesaj.lower().strip()
    for tur, kelimeler in DIYALOG_ANAHTAR.items():
        if any(k in m for k in kelimeler):
            return f"diyalog:{tur}"
    if any(k in m for k in EGITIM_ANAHTAR) or len(m.split()) >= 3:
        return "egitim"
    return "diyalog:default"

def diyalog_cevap(tur: str) -> str:
    anahtar = tur.split(":")[1] if ":" in tur else "default"
    return random.choice(DIYALOG_KALIPLARI.get(anahtar, DIYALOG_KALIPLARI["default"]))

# --------------------------------------------------------------
# GROQ İLE EĞİTİM CEVABI
# --------------------------------------------------------------
def groq_egitim_cevabi(soru: str) -> str:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        sistem_mesaji = """Sen NumBot'sun, 7. sınıf öğrencilerine yardım eden bir eğitim asistanısın.
        Kendi bilgilerini kullanarak soruyu cevapla.
        Cevabın şu özellikleri taşımalı:
        - 7. sınıf seviyesinde, anlaşılır Türkçe
        - 3-5 paragraf veya madde işaretleriyle
        - Örneklerle desteklenmiş
        - Müfredata uygun
        - Gereksiz detaylardan kaçın
        - Kendini NumBot olarak tanıtma, sadece cevap ver"""
        
        yanit = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistem_mesaji},
                {"role": "user", "content": f"7. sınıf öğrencisine şu soruyu cevapla: {soru}"}
            ],
            max_tokens=600,
            temperature=0.5
        )
        
        return yanit.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ Bağlantı hatası oluştu. Lütfen daha sonra tekrar dene.\n\nHata: {str(e)}"

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
    st.caption("🤖 NumBot v1.0 | 7. Sınıf Eğitim Asistanı")
    
    if st.session_state.kullanici_adi:
        st.markdown(f"<div style='margin-top: 10px; text-align: center; padding: 10px; background: rgba(102,126,234,0.1); border-radius: 15px; border: 1px solid rgba(102,126,234,0.3);'>👤 {st.session_state.kullanici_adi}</div>", unsafe_allow_html=True)

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
        else:
            st.warning("Lütfen adını yaz.")
    st.stop()

# --------------------------------------------------------------
# ANA ALAN
# --------------------------------------------------------------
ad = st.session_state.kullanici_adi or "Öğrenci"
st.markdown(f'<div class="ana-baslik">🤖 Merhaba, {ad}!</div>', unsafe_allow_html=True)
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Yapay Zeka Destekli Eğitim Asistanı</div>', unsafe_allow_html=True)

sohbet = aktif_sohbet()

if sohbet is None:
    st.info("💡 Yeni bir sohbet başlatmak için sol menüdeki **➕ Yeni Sohbet** butonuna tıklayın.")
else:
    for m in sohbet["mesajlar"]:
        if m["rol"] == "kullanici":
            st.markdown(f'<div class="mesaj-kullanici"><span>{m["icerik"]}</span></div>', unsafe_allow_html=True)
        else:
            tur_yazi = "📝 NumBot" if m.get("tur") == "egitim" else "💬 NumBot"
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
                with st.spinner("🤖 NumBot düşünüyor ve cevap hazırlıyor..."):
                    cevap = groq_egitim_cevabi(msg)
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "egitim"})
            else:
                st.session_state.disi_sayac += 1
                cevap = diyalog_cevap(tur)
                uyari = None
                if st.session_state.disi_sayac >= 3:
                    uyari = random.choice([
                        "💡 Sohbet güzel ama biraz ders sorusu soralım mı?",
                        "📖 Ders dışına çıktık, hadi bir soru sor.",
                        "🎯 NumBot olarak asıl görevim derslerinde sana yardımcı olmak. Bir ders sorusu sormaya ne dersin?"
                    ])
                    st.session_state.disi_sayac = 0
                sohbet["mesajlar"].append({"rol": "asistan", "icerik": cevap, "tur": "diyalog", "uyari": uyari})
            
            st.rerun()
