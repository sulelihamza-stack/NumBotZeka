import streamlit as st
import time
import re
import random
import json
import os
from duckduckgo_search import DDGS

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
    # MATEMATİK
    "tam sayı": "📚 **Tam Sayılar - 7. Sınıf Matematik**\n\nTam sayılar pozitif, negatif ve sıfırdan oluşur.\n\n**Toplama:** Aynı işaretli toplanır, işaret aynı kalır. (+3)+(+5)=+8, (-3)+(-5)=-8\n**Çıkarma:** Çıkarılanın işareti değişir. (+5)-(-3)=+8\n**Çarpma/Bölme:** Aynı işaretli → pozitif, farklı işaretli → negatif. (-4)×(-2)=+8, (-4)×(+2)=-8\n\nÖrnek: Dalgıç -15 m'de iken 8 m yükselirse (-15)+(+8)=-7 m olur.",
    "denklem": "📚 **Denklemler - 7. Sınıf Matematik**\n\nDenklem, içinde bilinmeyen bulunan eşitliktir.\nÖrnek: 2x+3=7 → 2x=4 → x=2\n\nDenklem çözerken bilinmeyenleri bir tarafa, sayıları diğer tarafa toplarız.",
    "oran": "📚 **Oran ve Orantı - 7. Sınıf Matematik**\n\nOran, iki çokluğun birbirine bölünerek karşılaştırılmasıdır.\nÖrnek: 3/5 = 6/10 → doğru orantı\n\nBir sınıfta kızların erkeklere oranı 2/3 ise 12 kız varsa erkek sayısı 18'dir.",
    "yüzde": "📚 **Yüzdeler - 7. Sınıf Matematik**\n\nYüzde, bir sayının 100'de kaç olduğunu gösterir.\nÖrnek: 200 TL'nin %25'i = 200 × 25/100 = 50 TL indirim.\nİndirimli fiyat = 200 - 50 = 150 TL.",
    
    # TÜRKÇE
    "zarf": "📚 **Zarflar (Belirteçler) - 7. Sınıf Türkçe**\n\nZarflar, fiilleri zaman, durum, miktar, yer-yön, soru yönünden belirtir.\n\n**Türleri:**\n1. Durum: hızlı koştu, güzel yazdı\n2. Zaman: yarın gelecek, şimdi gidiyor\n3. Miktar: çok okudu, az yedi\n4. Yer-Yön: içeri girdi, ileri gitti\n5. Soru: nasıl geldi?, ne zaman gitti?",
    "fiil": "📚 **Fiiller (Eylemler) - 7. Sınıf Türkçe**\n\nFiiller, iş, oluş, hareket bildirir.\n\n**Anlam Özellikleri:**\n- İş fiili: kitabı okudu (nesne alır)\n- Oluş fiili: havalar soğudu (kendiliğinden)\n- Durum fiili: bebek uyuyor (nesne almaz)\n\n**Haber Kipleri:** geldi, gelmiş, geliyor, gelecek, gelir",
    "noktalama": "📚 **Noktalama İşaretleri - 7. Sınıf Türkçe**\n\n**Nokta (.):** Cümle sonu, kısaltmalarda (Dr., Alb.)\n**Virgül (,):** Eş görevli kelimeleri ayırır, ara sözlerde\n**Soru işareti (?):** Soru cümlelerinde\n**Ünlem (!):** Sevinç, korku, şaşkınlık bildiren cümlelerde\n**İki nokta (:):** Açıklama yapılacaksa, alıntılarda",
    
    # FEN
    "fotosentez": "📚 **Fotosentez - 7. Sınıf Fen Bilimleri**\n\nFotosentez, bitkilerin güneş ışığıyla karbondioksit ve sudan besin (glikoz) ve oksijen üretmesidir.\n\nDenklem: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂\n\nSadece gündüz gerçekleşir. Kloroplastta olur.",
    "mitoz": "📚 **Mitoz Bölünme - 7. Sınıf Fen Bilimleri**\n\nMitoz, bir hücrenin iki yeni hücreye bölünmesidir.\n\n**Evreleri:** İnterfaz, Profaz, Metafaz, Anafaz, Telofaz\n\n1 hücre → 2 hücre, kromozom sayısı değişmez. Tek hücrelilerde üreme, çok hücrelilerde büyüme ve onarım sağlar.",
    "mayoz": "📚 **Mayoz Bölünme - 7. Sınıf Fen Bilimleri**\n\nMayoz, üreme hücrelerinin oluştuğu bölünme şeklidir.\n\n1 hücre → 4 yavru hücre, kromozom sayısı yarıya iner. Sadece üreme organlarında görülür.",
    "elektrik": "📚 **Elektrik Devreleri - 7. Sınıf Fen Bilimleri**\n\nBasit elektrik devresi: pil, lamba, anahtar, bağlantı kablosu.\n\nOhm Yasası: Gerilim (V) = Akım (I) × Direnç (R)\n\nSeri bağlı devrede akım aynı, gerilimler toplanır. Paralel bağlı devrede gerilim aynı, akımlar toplanır.",
    
    # SOSYAL BİLGİLER
    "üretim": "📚 **Üretim, Dağıtım, Tüketim - 7. Sınıf Sosyal Bilgiler**\n\n**Üretim:** Doğadaki kaynakları kullanarak ürün/hizmet oluşturma (tarım, sanayi, madencilik)\n**Dağıtım:** Üretilen ürünlerin tüketiciye ulaştırılması (taşıma, lojistik, e-ticaret)\n**Tüketim:** Üretilen ürünlerin kullanılması\n\nÖrnek: Çiftçi buğday üretir → un fabrikası dağıtır → fırın ekmek yapar → tüketici satın alır.",
    "tarih": "📚 **Türk Tarihinde Yolculuk - 7. Sınıf Sosyal Bilgiler**\n\nOrta Asya'da kurulan ilk Türk devletleri: Asya Hun, Göktürk, Uygur.\n\n1071 Malazgirt Zaferi ile Anadolu'nun kapıları Türklere açıldı.\n\nOsmanlı Devleti 1299'da kuruldu, 1453'te İstanbul fethedildi.",
    "coğrafya": "📚 **Türkiye'nin Bölgeleri - 7. Sınıf Sosyal Bilgiler**\n\nTürkiye 7 coğrafi bölgeye ayrılır:\n- Karadeniz (çay, fındık)\n- Akdeniz (turizm, narenciye)\n- Ege (zeytin, tütün)\n- Marmara (sanayi, ulaşım)\n- İç Anadolu (tahıl)\n- Doğu Anadolu (hayvancılık)\n- Güneydoğu Anadolu (pamuk, petrol)",
    
    # İNGİLİZCE
    "simple present": "📚 **Simple Present Tense - 7. Sınıf İngilizce**\n\nGenel geçer durumlar ve alışkanlıklar için kullanılır.\n\n(+) I/You/We/They play. He/She/It plays.\n(-) I/You/We/They don't play. He/She/It doesn't play.\n(?) Do you play? Does she play?\n\nÖrnek: She plays tennis every Sunday.",
    "present continuous": "📚 **Present Continuous Tense - 7. Sınıf İngilizce**\n\nŞu anda gerçekleşen olaylar için kullanılır.\n\n(+) I am playing. He is playing. They are playing.\n(-) I am not playing.\n(?) Are you playing?\n\nÖrnek: She is watching TV now."
}

def offline_cevap(soru):
    soru_lower = soru.lower()
    for anahtar, cevap in KONU_HAVUZU.items():
        if anahtar in soru_lower:
            return cevap
    return None

# --------------------------------------------------------------
# İNTERNETTEN ARAMA (DUCKDUCKGO)
# --------------------------------------------------------------
def internetten_ara(soru):
    try:
        sorgu = f"{soru} 7 sınıf konu anlatımı site:meb.gov.tr OR site:eba.gov.tr OR site:derslig.com OR site:morpakampus.com OR site:okulistik.com OR site:tongucakademi.com"
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(sorgu, region="tr-tr", max_results=3))
            if sonuclar:
                metin = ""
                kaynaklar = []
                for s in sonuclar[:2]:
                    if s.get("body"):
                        metin += s["body"] + "\n\n"
                    if s.get("href"):
                        kaynaklar.append(s["href"])
                if metin:
                    return metin[:2000], kaynaklar
    except Exception as e:
        pass
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
    "ne yapabilirsin": ["📚 Tüm 7. sınıf derslerinde sana yardımcı olabilirim! Matematik, Türkçe, Fen, Sosyal, İngilizce...", "🔍 İnternette araştırma yapıp güvenilir kaynaklardan cevap bulurum."],
    "default": ["💭 Ders sorusu sorabilir misin? Matematik, Türkçe, Fen, Sosyal, İngilizce sorularını cevaplayabilirim.", "📖 Sana bir konuyu anlatmamı ister misin?"]
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
    # Önce internetten dene
    internet_cevap, kaynaklar = internetten_ara(soru)
    if internet_cevap:
        kaynak_metni = "\n\n📚 **Kaynaklar:**\n" + "\n".join(kaynaklar) if kaynaklar else ""
        return internet_cevap + kaynak_metni
    
    # İnternet yoksa offline havuzdan dene
    offline = offline_cevap(soru)
    if offline:
        return offline
    
    # Hiçbiri yoksa
    return "📚 Bu konuda henüz bilgim yok. Lütfen farklı bir soru sor veya konuyu daha açık yaz. Bildiğim konular: Zarflar, Tam Sayılar, Denklemler, Yüzdeler, Fotosentez, Mitoz, Mayoz, Elektrik Devreleri, Üretim-Dağıtım-Tüketim, Türk Tarihi, Türkiye'nin Bölgeleri, Simple Present Tense."

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
    st.caption("🔍 İnternette araştırma yapar, güvenilir kaynaklardan bilgi verir.")
    
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
st.markdown('<div class="ana-alt">NumBot | 7. Sınıf Yapay Zeka Eğitim Asistanı | İnternette Araştırma Yapar</div>', unsafe_allow_html=True)

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
                with st.spinner("🔍 NumBot internette güvenilir kaynaklarda araştırıyor..."):
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
