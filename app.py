import streamlit as st
import random
import math

st.set_page_config(page_title="NumNum Zeka", page_icon="🎯")
st.markdown("""
<style>
    .stApp { background-color: #000000; }
    .stMarkdown, .stText, div, p, span { color: #ffffff !important; }
    .stButton button { background-color: #333333; color: white; border-radius: 10px; width: 100%; }
    .stSelectbox label, .stMetric label { color: white !important; }
    .stChatInput textarea { background-color: #1a1a1a; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 NumNum Zeka - 7. Sınıf")

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []
    st.session_state.aktif_soru = None
    st.session_state.aktif_cevap = None
    st.session_state.aktif_siklar = None
    st.session_state.secili_ders = None
    st.session_state.puan = 0
    st.session_state.dogru = 0
    st.session_state.yanlis = 0

# ============================================================
# MATEMATİK - 12 KONU (HER KONUDA 10+ SORU TİPİ)
# ============================================================
def mat_tam():
    tip = random.choice([1,2,3,4,5,6,7,8])
    if tip == 1:
        b = random.randint(-60,-10); t = b; h = []
        for _ in range(random.randint(4,7)):
            a = random.randint(5,40)
            if random.choice([0,1])==0: t+=a; h.append(f"{a} m yükseliyor")
            else: t-=a; h.append(f"{a} m dalıyor")
        m = f"🐟 Dalgıç **{b} m**'de iken " + ", ".join(h); d = str(t)
    elif tip == 2:
        b = random.randint(-20,-5); t = b; h = []
        for _ in range(random.randint(4,7)):
            a = random.randint(5,30)
            if random.choice([0,1])==0: t+=a; h.append(f"{a}°C artıyor")
            else: t-=a; h.append(f"{a}°C düşüyor")
        m = f"🌡️ Termometre **{b}°C** iken " + ", ".join(h); d = str(t)
    elif tip == 3:
        s = random.randint(-50,50); t = s; h = []
        for _ in range(random.randint(4,7)):
            a = random.randint(5,40)
            if random.choice([0,1])==0: t+=a; h.append(f"+{a}")
            else: t-=a; h.append(f"-{a}")
        m = f"📱 Ekran **{s}** iken " + ", ".join(h); d = str(t)
    elif tip == 4:
        b = random.randint(-5,5); t = b; h = []
        for _ in range(random.randint(4,7)):
            a = random.randint(3,12)
            if random.choice([0,1])==0: t+=a; h.append(f"{a} kat yukarı")
            else: t-=a; h.append(f"{a} kat aşağı")
        m = f"🏢 Asansör **{b}. kat** iken " + ", ".join(h); d = str(t)
    elif tip == 5:
        b = random.randint(200,1000); t = b; h = []
        for _ in range(random.randint(4,7)):
            a = random.randint(50,300)
            if random.choice([0,1])==0: t+=a; h.append(f"{a} TL yatırıyor")
            else: t-=a; h.append(f"{a} TL çekiyor")
        m = f"💰 Hesap **{b} TL** iken " + ", ".join(h); d = str(t)
    elif tip == 6:
        b = random.randint(500,2500); t = b; h = []
        for _ in range(random.randint(4,7)):
            a = random.randint(100,600)
            if random.choice([0,1])==0: t+=a; h.append(f"{a} m çıkıyor")
            else: t-=a; h.append(f"{a} m iniyor")
        m = f"⛰️ Dağcı **+{b} m**'de iken " + ", ".join(h); d = str(t)
    else:
        b = random.randint(100,500); t = b
        for _ in range(random.randint(3,6)):
            t += random.randint(150,400)
        m = f"💼 Başlangıç maaşı **{b} TL**, her ay {random.randint(150,400)} TL zam. {random.randint(3,6)} ay sonra maaş?"; d = str(t)
    y = [str(int(d)+random.choice([5,7,9,11])), str(int(d)-random.choice([5,7,9,11])), str(int(d)+random.choice([3,4,6]))]
    s = [d] + y; random.shuffle(s)
    return m + f"\n\n**Sonuç kaç?**", d, s

def mat_ras():
    tip = random.choice([1,2,3,4,5])
    if tip == 1:
        p1=random.randint(1,12); pd1=random.randint(2,12); p2=random.randint(1,12); pd2=random.randint(2,12)
        if p1/pd1 > p2/pd2: d=">"
        elif p1/pd1 < p2/pd2: d="<"
        else: d="="
        m = f"{p1}/{pd1} __ {p2}/{pd2}"; s=[">","<","=","≠"]; random.shuffle(s); return m, d, s
    elif tip == 2:
        p=random.randint(1,12); pd=random.randint(2,12); v=p/pd; d=f"{v:.2f}"
        m = f"{p}/{pd} ondalık gösterimi?"; s=[d, f"{v+0.1:.2f}", f"{v-0.1:.2f}", f"{v+0.05:.2f}"]; random.shuffle(s); return m, d, s
    elif tip == 3:
        p=random.randint(1,8); pd=random.randint(2,8)
        m = f"Pastanın {p}/{pd}'i yenmiş. Kalan 6 kişiye paylaştırılırsa kişi başı?"; k=1-(p/pd); son=k/6
        pay=int(son*100); payda=100
        for i in range(2,20):
            if pay%i==0 and payda%i==0: pay//=i; payda//=i
        d=f"{pay}/{payda}" if payda!=1 else str(pay); s=[d, f"{pay+1}/{payda}", f"{pay-1}/{payda}", f"{pay}/{payda+1}"]; random.shuffle(s); return m, d, s
    else:
        p=random.randint(1,9); pd=random.randint(2,9); carp=random.randint(2,5); yp=p*carp; ypd=pd*carp
        d=str(yp+ypd); m=f"{p}/{pd} kesrini {carp} ile genişletince pay+payda=?"; s=[d, str(int(d)+random.randint(5,15)), str(int(d)-random.randint(5,15)), str(int(d)+random.randint(1,4))]; random.shuffle(s); return m, d, s

def mat_ras_is():
    p1=random.randint(1,8); pd1=random.randint(2,8); p2=random.randint(1,8); pd2=random.randint(2,8)
    islem=random.choice(["+","-","x","/"])
    if islem=="+": sp=p1*pd2+p2*pd1; spd=pd1*pd2
    elif islem=="-": sp=p1*pd2-p2*pd1; spd=pd1*pd2
    elif islem=="x": sp=p1*p2; spd=pd1*pd2
    else: sp=p1*pd2; spd=pd1*p2
    eb=math.gcd(sp,spd); sp//=eb; spd//=eb
    d=f"{sp}/{spd}" if spd!=1 else str(sp)
    m = f"{p1}/{pd1} {islem} {p2}/{pd2} = ?"
    s = [d, f"{sp+1}/{spd}", f"{sp-1}/{spd}", f"{sp}/{spd+1}"]; random.shuffle(s)
    return m, d, s

def mat_ceb():
    tip = random.choice([1,2,3,4])
    if tip == 1:
        a=random.randint(1,5); b=random.randint(-8,8); c=random.randint(1,5); d=random.randint(-8,8); islem=random.choice(["+","-"])
        if islem=="+": son=f"{a+c}x+{b+d}"
        else: son=f"{a-c}x+{b-d}"
        m = f"({a}x{b:+d}) {islem} ({c}x{d:+d}) = ?"
        s = [son, f"{a+c+1}x+{b+d}", f"{a+c}x+{b+d+1}", f"{a+c-1}x+{b+d}"]; random.shuffle(s); return m, son, s
    elif tip == 2:
        a=random.randint(2,6); b=random.randint(1,10); x=random.randint(1,5); son=a*x+b
        m = f"{a}x+{b} ifadesinin x={x} için değeri?"; d=str(son)
        s=[d, str(son+random.randint(2,6)), str(son-random.randint(2,6)), str(son+random.randint(1,2))]; random.shuffle(s); return m, d, s
    else:
        a=random.randint(2,5); b=random.randint(1,8); d=f"{4*a}x+{4*b}"
        m = f"Bir kenarı ({a}x+{b}) cm olan karenin çevresi?"; s=[d, f"{4*a+1}x+{4*b}", f"{4*a}x+{4*b+1}", f"{4*a-1}x+{4*b}"]; random.shuffle(s); return m, d, s

def mat_denk():
    tip = random.choice([1,2,3,4])
    if tip == 1:
        a=random.randint(2,6); b=random.randint(2,15); c=random.randint(2,6); d=random.randint(2,15)
        if a==c: a=c+1; coz=(d-b)/(a-c)
        dogru = str(int(coz)) if coz==int(coz) else f"{coz:.1f}"
        m = f"{a}x+{b} = {c}x+{d} → x=?"
    elif tip == 2:
        a=random.randint(2,7); b=random.randint(1,10); c=random.randint(2,7); d=random.randint(1,8)
        coz = (a*b + d)/(a-c) if a!=c else random.randint(1,10)
        dogru = str(int(coz)) if coz==int(coz) else f"{coz:.1f}"
        m = f"{a}(x-{b}) = {c}x+{d} → x=?"
    else:
        a=random.randint(1,5); b=random.randint(1,10); dogru=str(b)
        m = f"Bir sayının {a} katının {b} fazlası, {a+1} katına eşit. Sayı kaç?"
    y = [str(float(dogru)+i) for i in [-3,-2,2,3] if float(dogru)+i != float(dogru)][:3]
    s = [dogru] + y; random.shuffle(s)
    return m, dogru, s

def mat_oran():
    tip = random.choice([1,2,3])
    if tip == 1:
        a=random.randint(2,10); b=random.randint(2,10); k=random.randint(2,6); x=b*k; d=str(x)
        m = f"{a}/{b} = {a*k}/x → x=?"
        s = [d, str(x+random.randint(1,3)), str(x-random.randint(1,3)), str(x+random.randint(4,6))]; random.shuffle(s); return m, d, s
    else:
        k=random.randint(3,8); e=random.randint(3,8); toplam=random.randint(40,80); kiz=int(k/(k+e)*toplam); d=str(kiz)
        m = f"Sınıfta kız/erkek oranı {k}/{e}, mevcut {toplam} → kız sayısı?"
        s = [d, str(kiz+random.randint(2,5)), str(kiz-random.randint(2,5)), str(kiz+random.randint(1,3))]; random.shuffle(s); return m, d, s

def mat_yuz():
    tip = random.choice([1,2,3])
    s=random.randint(100,500); y=random.choice([10,15,20,25,30,40,50])
    if tip == 1:
        son=int(s*y/100); d=str(son)
        m = f"{s} TL'nin %{y} indirimi?"
    elif tip == 2:
        son=int(s*(100-y)/100); d=str(son)
        m = f"{s} TL'ye %{y} indirimli fiyat?"
    else:
        son=int(s*(100+y)/100); d=str(son)
        m = f"{s} TL'ye %{y} zam yapılırsa yeni fiyat?"
    s = [d, str(son+random.randint(3,8)), str(son-random.randint(3,8)), str(son+random.randint(1,2))]; random.shuffle(s)
    return m, d, s

def mat_aci():
    a=random.randint(30,150); tip=random.choice(["tümler","bütünler"])
    if tip=="tümler": d=str(90-a); m=f"{a}°'nin tümleri?"
    else: d=str(180-a); m=f"{a}°'nin bütünleri?"
    s = [d, str(int(d)+random.randint(5,15)), str(int(d)-random.randint(5,15)), str(int(d)+random.randint(1,4))]; random.shuffle(s)
    return m, d, s

def mat_cok():
    k=random.randint(3,8); tip=random.choice(["iç","dış","köşegen"])
    if tip=="iç": d=str((k-2)*180); m=f"{k} kenarlı iç açı toplamı?"
    elif tip=="dış": d=str(int(360/k)); m=f"Düzgün {k} kenarlı dış açı?"
    else: d=str(k*(k-3)//2); m=f"{k} kenarlı köşegen sayısı?"
    s = [d, str(int(d)+random.randint(10,30)), str(int(d)-random.randint(10,30)), str(int(d)+random.randint(5,9))]; random.shuffle(s)
    return m, d, s

def mat_cem():
    r=random.randint(3,15); tip=random.choice(["çevre","alan","çap"]); pi=3
    if tip=="çevre": d=str(2*pi*r); m=f"Yarıçap {r} cm çember çevresi? (π=3)"
    elif tip=="alan": d=str(pi*r*r); m=f"Yarıçap {r} cm daire alanı? (π=3)"
    else: d=str(2*r); m=f"Yarıçap {r} cm çemberin çapı?"
    s = [d, str(int(d)+random.randint(5,15)), str(int(d)-random.randint(5,15)), str(int(d)+random.randint(1,4))]; random.shuffle(s)
    return m, d, s

def mat_veri():
    v=[random.randint(10,90) for _ in range(5)]; ort=sum(v)//5; med=sorted(v)[2]
    tip=random.choice(["ortalama","medyan","açıklık"])
    if tip=="ortalama": d=str(ort); m=f"{v} ortalaması?"
    elif tip=="medyan": d=str(med); m=f"{v} medyanı?"
    else: d=str(max(v)-min(v)); m=f"{v} açıklığı?"
    s = [d, str(int(d)+random.randint(2,6)), str(int(d)-random.randint(2,6)), str(int(d)+random.randint(1,2))]; random.shuffle(s)
    return m, d, s

def mat_cis():
    c=random.choice(["küp","dikdörtgen prizma","küre","silindir","kare prizma"])
    if c=="küp": return "Küpün kaç ayrıtı vardır?", "12", ["8","10","12","14"]
    elif c=="dikdörtgen prizma": return "Dikdörtgen prizmanın kaç yüzü vardır?", "6", ["4","5","6","8"]
    elif c=="küre": return "Kürenin kaç köşesi vardır?", "0", ["0","1","2","4"]
    elif c=="silindir": return "Silindirin yan yüzeyi açılınca hangi şekil olur?", "Dikdörtgen", ["Kare","Üçgen","Dikdörtgen","Daire"]
    else: return "Kare prizmanın kaç ayrıtı vardır?", "12", ["8","10","12","14"]

# ============================================================
# FEN BİLİMLERİ - HER KONUDA 7+ SORU
# ============================================================
def fen_gunes():
    sorular = [
        ("Güneş sisteminin en büyük gezegeni?", "Jüpiter", ["Mars","Satürn","Jüpiter","Uranüs"]),
        ("Dünya'nın doğal uydusu?", "Ay", ["Mars","Ay","Venüs","Jüpiter"]),
        ("Güneş'e en yakın gezegen?", "Merkür", ["Venüs","Merkür","Dünya","Mars"]),
        ("Halkalarıyla ünlü gezegen?", "Satürn", ["Jüpiter","Satürn","Uranüs","Neptün"]),
        ("En sıcak gezegen?", "Venüs", ["Merkür","Venüs","Dünya","Mars"]),
        ("Güneş sistemi kaç gezegenden oluşur?", "8", ["6","7","8","9"]),
        ("Kızıl gezegen olarak bilinen?", "Mars", ["Merkür","Venüs","Dünya","Mars"]),
    ]
    return random.choice(sorular)

def fen_hucre():
    sorular = [
        ("Mitoz bölünme sonucu kaç hücre oluşur?", "2", ["1","2","4","8"]),
        ("Hücrenin yönetim merkezi?", "Çekirdek", ["Mitokondri","Çekirdek","Ribozom","Koful"]),
        ("Mayoz bölünme nerede olur?", "Üreme ana hücrelerinde", ["Vücut hücrelerinde","Üreme ana hücrelerinde","Sinir hücrelerinde","Kas hücrelerinde"]),
        ("Hücrenin enerji üreten organeli?", "Mitokondri", ["Mitokondri","Ribozom","Lizozom","Golgi"]),
        ("Protein sentezi nerede yapılır?", "Ribozom", ["Mitokondri","Ribozom","Çekirdek","Koful"]),
        ("Bitki hücresinde bulunmayan organel?", "Sentriyol", ["Mitokondri","Ribozom","Sentriyol","Koful"]),
    ]
    return random.choice(sorular)

def fen_kuvvet():
    k=random.randint(5,20); v=random.randint(2,10); ke=int(0.5*k*v*v)
    sorular = [
        (f"Kütlesi {k} kg, hızı {v} m/s olan cismin kinetik enerjisi?", str(ke), [str(ke+5), str(ke-5), str(ke+10), str(ke-10)]),
        ("Bir cismin hareket durumunu değiştiren etki?", "Kuvvet", ["Enerji","Kuvvet","İş","Güç"]),
        ("Potansiyel enerji nelere bağlıdır?", "Kütle ve yükseklik", ["Kütle ve hız","Kütle ve yükseklik","Hız ve yükseklik","Sadece kütle"]),
        ("Sürtünme kuvveti hangi yönde etki eder?", "Harekete zıt yönde", ["Hareket yönünde","Harekete zıt yönde","Dikey yönde","Yatay yönde"]),
        ("Bir cismin sahip olduğu hareket enerjisine ne denir?", "Kinetik enerji", ["Potansiyel enerji","Kinetik enerji","Mekanik enerji","Isı enerjisi"]),
    ]
    return random.choice(sorular)

def fen_madde():
    sorular = [
        ("Homojen karışımlara ne denir?", "Çözelti", ["Süspansiyon","Emülsiyon","Çözelti","Kolloid"]),
        ("Bir elementin en küçük yapı taşı?", "Atom", ["Molekül","Atom","Hücre","Tanecik"]),
        ("Heterojen karışıma örnek?", "Ayran", ["Tuzlu su","Şekerli su","Ayran","Hava"]),
        ("Yoğunluğu 0,9 ve 1,1 olan sıvılar eşit hacimde karışırsa son yoğunluk?", "1,0", ["0,9","1,0","1,1","2,0"]),
        ("Saf maddeler kaç grupta incelenir?", "2", ["1","2","3","4"]),
    ]
    return random.choice(sorular)

def fen_isik():
    sorular = [
        ("Işığın geri dönmesine ne denir?", "Yansıma", ["Kırılma","Yansıma","Soğurma","Dağılma"]),
        ("Işığın doğrultu değiştirmesine ne denir?", "Kırılma", ["Yansıma","Kırılma","Soğurma","Girişim"]),
        ("Işığın en hızlı yayıldığı ortam?", "Boşluk", ["Boşluk","Hava","Su","Cam"]),
        ("Aynalar hangi prensiple çalışır?", "Yansıma", ["Kırılma","Yansıma","Soğurma","Dağılma"]),
        ("Mercekler hangi prensiple çalışır?", "Kırılma", ["Yansıma","Kırılma","Soğurma","Dağılma"]),
    ]
    return random.choice(sorular)

def fen_ureme():
    sorular = [
        ("Kurbağa gelişimine ne denir?", "Başkalaşım", ["Metamorfoz","Başkalaşım","Döllenme","Büyüme"]),
        ("Bitkilerde tohum oluşumu için gerekli olay?", "Tozlaşma", ["Döllenme","Tozlaşma","Çimlenme","Fotosentez"]),
        ("Memelilerde yavruları besleyen bez?", "Süt bezi", ["Ter bezi","Yağ bezi","Süt bezi","Salya bezi"]),
        ("İnsanda döllenme nerede olur?", "Fallop tüpü", ["Rahim","Yumurtalık","Fallop tüpü","Vajina"]),
        ("Kelebek gelişimi hangi gruptadır?", "Başkalaşım", ["Metamorfoz","Başkalaşım","Döllenme","Büyüme"]),
    ]
    return random.choice(sorular)

def fen_elektrik():
    r1=random.randint(2,5); r2=random.randint(2,5); r_seri=r1+r2; r_par=round((r1*r2)/(r1+r2),1)
    sorular = [
        (f"{r1}Ω ve {r2}Ω direnç seri bağlanırsa eşdeğer direnç?", str(r_seri), [str(r_seri+1), str(r_seri-1), str(r_seri+2), str(r_seri-2)]),
        (f"{r1}Ω ve {r2}Ω direnç paralel bağlanırsa eşdeğer direnç?", str(r_par), [str(r_par+0.5), str(r_par-0.5), str(r_par+1), str(r_par-1)]),
        ("Bir ampulün parlaklığını artırmak için ne yapılır?", "Pil sayısı artırılır", ["Pil sayısı azaltılır","Direnç eklenir","Pil sayısı artırılır","Kablo uzatılır"]),
        ("Devrede akımı kontrol eden eleman?", "Anahtar", ["Pil","Direnç","Anahtar","Ampul"]),
        ("Devrede akımın geçtiği yol?", "Devre", ["Kablo","Devre","Pil","Ampul"]),
    ]
    return random.choice(sorular)

# ============================================================
# TÜRKÇE - 8 KONU
# ============================================================
def tur_fiil():
    f = random.choice(["gelmek","gitmek","bakmak","yazmak","okumak","koşmak","söylemek"])
    d = f.replace("mek","").replace("mak","") + "yor"
    return f"'{f}' fiilinin şimdiki zaman 2. tekil kişi çekimi?", d, [d, d+"m", d+"k", d+"n"]

def tur_zarf():
    sorular = [
        ("'Hızlı koştu' cümlesindeki zarf?", "hızlı", ["hızlı","koştu","o","güzel"]),
        ("'Çok güzel olmuş' cümlesindeki zarf?", "çok", ["çok","güzel","olmuş","o"]),
        ("'Yarın geleceğim' cümlesindeki zarf?", "yarın", ["yarın","geleceğim","ben","gün"]),
        ("'Dikkatlice dinledi' cümlesindeki zarf?", "dikkatlice", ["dikkatlice","dinledi","o","sessizce"]),
        ("'İçeri girdi' cümlesindeki zarf?", "içeri", ["içeri","girdi","o","hızla"]),
    ]
    return random.choice(sorular)

def tur_anlam():
    sorular = [
        ("'Keşke daha çok çalışsaydım.' cümlesindeki anlam?", "pişmanlık", ["pişmanlık","özlem","kararlılık","şart"]),
        ("'Bu işi yapabilir misin?' anlamı?", "rica/istek", ["emir","rica/istek","koşul","olasılık"]),
        ("'Yağmur yağsa da topraklar ıslansa.' anlamı?", "özlem", ["özlem","pişmanlık","koşul","kararlılık"]),
        ("'Sınavı kazandım çünkü çok çalıştım.' anlamı?", "neden-sonuç", ["amaç-sonuç","neden-sonuç","koşul","karşılaştırma"]),
    ]
    return random.choice(sorular)

def tur_paragraf():
    sorular = [
        ("'Ne kadar bilirsen bil, anlatabildiğin kadarsın.' ana fikri?", "Bilginin aktarımı önemlidir", ["Bilgi her şey değildir","Anlatmak zordur","Bilginin aktarımı önemlidir","Sessizlik erdemdir"]),
        ("'Teknoloji hayatımızı kolaylaştırsa da bizi tembelleştiriyor.' ana fikri?", "Teknoloji tembelleştiriyor", ["Teknoloji yararlıdır","Teknoloji tembelleştiriyor","Teknoloji gereksizdir","Teknoloji zararlıdır"]),
        ("'Kitap okumak zihnin jimnastiğidir.' ana fikri?", "Kitap okumak zihni geliştirir", ["Kitap okumak zaman kaybıdır","Kitap okumak zihni geliştirir","Sadece çocuklar okumalı","Kitap okumak sıkıcıdır"]),
    ]
    return random.choice(sorular)

def tur_yazim():
    sorular = [
        ("Aşağıdakilerden hangisi doğru?", "herkes", ["herkez","herkes","herkeş","herkese"]),
        ("'Herşey' doğru yazımı?", "Her şey", ["Herşey","Her şey","Her-şey","Her şe'y"]),
        ("'Birşey' doğru yazımı?", "Bir şey", ["Birşey","Bir şey","Bir-şey","Bir şe'y"]),
        ("'Türkiye'nin başkenti ...' boşluk?", "Ankara", ["İstanbul","Ankara","İzmir","Bursa"]),
    ]
    return random.choice(sorular)

def tur_noktalama():
    sorular = [
        ("Sıralı cümleleri ayırmak için hangi işaret?", "Noktalı virgül", ["Virgül","Nokta","Noktalı virgül","İki nokta"]),
        ("Alıntı cümlelerden önce hangi işaret?", "İki nokta", ["Virgül","Nokta","Noktalı virgül","İki nokta"]),
        ("Ünlem işareti hangi durumda kullanılır?", "Sevinç, heyecan, korku", ["Soru sorarken","Sevinç, heyecan, korku","Alıntı yaparken","Sıralama yaparken"]),
        ("Soru işareti hangi durumda kullanılır?", "Soru cümlelerinde", ["Sevinçte","Şaşkınlıkta","Soru cümlelerinde","Alıntıda"]),
    ]
    return random.choice(sorular)

def tur_sozcuk():
    sorular = [
        ("'Soğuk' zıt anlamlısı?", "sıcak", ["sıcak","buzlu","donuk","serin"]),
        ("Eş sesli kelime örneği?", "yüz", ["kalem","silgi","yüz","defter"]),
        ("'Yüzmek' mecaz anlamda hangi cümlede?", "Paralar içinde yüzüyor", ["Denizde yüzdü","Paralar içinde yüzüyor","Yüzmeyi sever","Nehirde yüzdü"]),
        ("'Ağız' kelimesi hangi cümlede mecaz anlamda?", "Ağız alışkanlığı", ["Ağız ve diş sağlığı","Ağız alışkanlığı","Ağzını açtı","Ağzı sulandı"]),
    ]
    return random.choice(sorular)

def tur_cumle():
    sorular = [
        ("'Kitap okumayı çok severim.' yüklemin türüne göre?", "İsim cümlesi", ["Fiil cümlesi","İsim cümlesi","Devrik cümle","Birleşik cümle"]),
        ("'Hava çok soğudu.' olumlu mu olumsuz mu?", "Olumlu", ["Olumlu","Olumsuz","Soru","Ünlem"]),
        ("'Ah, bu kadar da olmaz!' cümle türü?", "Ünlem cümlesi", ["İsim cümlesi","Fiil cümlesi","Ünlem cümlesi","Soru cümlesi"]),
        ("'Sınav bitti, herkes sevindi.' cümle yapısı?", "Birleşik cümle", ["Basit cümle","Birleşik cümle","Sıralı cümle","Bağlı cümle"]),
    ]
    return random.choice(sorular)

# ============================================================
# SOSYAL BİLGİLER - 7 KONU
# ============================================================
def sos_iletisim():
    sorular = [
        ("Duygu,düşünce ve bilgilerin aktarılması?", "İletişim", ["Empati","İletişim","Hoşgörü","Saygı"]),
        ("Karşısındakinin duygularını anlamaya çalışma?", "Empati", ["Sempati","Empati","Özgecilik","Fedakarlık"]),
        ("Sözsüz iletişim örneği?", "Jest ve mimikler", ["Konuşmak","Jest ve mimikler","Mektup","Telefon"]),
        ("İletişimde geri bildirim nedir?", "Alınan mesaja cevap", ["Mesajı göndermek","Alınan mesaja cevap","Mesajı kodlamak","Mesajı iletmek"]),
    ]
    return random.choice(sorular)

def sos_tarih():
    sorular = [
        ("İlk Türk devletlerinden biri?", "Asya Hun Devleti", ["Osmanlı","Asya Hun","Bizans","Roma"]),
        ("Osmanlı'da Lale Devri yeniliği?", "Matbaa", ["Matbaa","Fetih","Anayasa","Cumhuriyet"]),
        ("İstanbul'un fethi hangi padişah?", "Fatih Sultan Mehmet", ["Yavuz Sultan Selim","Kanuni","Fatih Sultan Mehmet","II. Mahmut"]),
        ("Milli Mücadele'nin başladığı yer?", "Samsun", ["İstanbul","Ankara","Samsun","İzmir"]),
        ("TBMM hangi tarihte açıldı?", "23 Nisan 1920", ["19 Mayıs 1919","23 Nisan 1920","29 Ekim 1923","30 Ağustos 1922"]),
    ]
    return random.choice(sorular)

def sos_nufus():
    sorular = [
        ("Bir ülkede yaşayan insan sayısı?", "Nüfus", ["Nüfus yoğunluğu","Nüfus","Göç","Demografi"]),
        ("Türkiye'nin en kalabalık şehri?", "İstanbul", ["Ankara","İzmir","İstanbul","Bursa"]),
        ("Nüfus yoğunluğu en az olan bölge?", "Doğu Anadolu", ["Marmara","Doğu Anadolu","Akdeniz","Ege"]),
        ("Göç veren bölgelerimizden biri?", "Doğu Anadolu", ["Marmara","Ege","Doğu Anadolu","Akdeniz"]),
    ]
    return random.choice(sorular)

def sos_bilim():
    sorular = [
        ("Matematik, fizik, kimya gibi disiplinler?", "Bilim", ["Teknoloji","Sanat","Bilim","Edebiyat"]),
        ("Teknolojinin olumlu etkisi?", "İletişim kolaylığı", ["Kirlilik","Trafik","İletişim kolaylığı","Sosyal izolasyon"]),
        ("İcat ile keşif farkı?", "İcat yoktan var eder, keşif var olanı bulur", ["İcat var olanı bulur","Keşif yoktan var eder","İcat yoktan var eder, keşif var olanı bulur","İkisi aynı"]),
        ("Bilimsel yöntemin ilk basamağı?", "Gözlem", ["Deney","Gözlem","Hipotez","Sonuç"]),
    ]
    return random.choice(sorular)

def sos_ekonomi():
    sorular = [
        ("İhtiyaçları karşılamak için yapılan faaliyet?", "Üretim", ["Tüketim","Üretim","Pazarlama","Reklam"]),
        ("Gelir ve gider arasındaki fark?", "Kâr", ["Zarar","Kâr","Bütçe","Tasarruf"]),
        ("Vergi neden alınır?", "Kamu hizmetleri için", ["İhracat","Kamu hizmetleri","İthalat","Savunma"]),
        ("Bütçe nedir?", "Gelir-gider planı", ["Gelir tablosu","Gider tablosu","Gelir-gider planı","Kâr tablosu"]),
    ]
    return random.choice(sorular)

def sos_kultur():
    sorular = [
        ("Toplumun maddi manevi değerler bütünü?", "Kültür", ["Medeniyet","Kültür","Gelenek","Görenek"]),
        ("UNESCO Türkiye'den bir miras?", "Kapadokya", ["Ankara","İstanbul","Kapadokya","Antalya"]),
        ("Somut olmayan kültürel miras?", "Hacivat Karagöz", ["Pamukkale","Efes","Hacivat Karagöz","Ayasofya"]),
        ("Kültürel farklılıklara saygı neden önemlidir?", "Toplumsal barış için", ["Ekonomi için","Toplumsal barış için","Ticaret için","Savaş için"]),
    ]
    return random.choice(sorular)

def sos_demokrasi():
    sorular = [
        ("Halkın kendini yönettiği yönetim?", "Demokrasi", ["Monarşi","Oligarşi","Demokrasi","Teokrasi"]),
        ("Seçme ve seçilme yaşı?", "18", ["16","17","18","20"]),
        ("Demokrasinin temel ilkesi?", "Milli egemenlik", ["Kuvvetler birliği","Milli egemenlik","Tek parti","Diktatörlük"]),
        ("Hukukun üstünlüğü ne demektir?", "Kanunlar herkese eşit uygulanır", ["Zenginler farklı","Yöneticiler ayrıcalıklı","Kanunlar herkese eşit uygulanır","Halk yargılanmaz"]),
    ]
    return random.choice(sorular)

# ============================================================
# DERS BİRLEŞTİRME
# ============================================================
tum_dersler = {
    "Matematik": {
        "Tam Sayılar": mat_tam, "Rasyonel Sayılar": mat_ras, "Rasyonel İşlemler": mat_ras_is,
        "Cebirsel İfadeler": mat_ceb, "Denklemler": mat_denk, "Oran-Orantı": mat_oran,
        "Yüzdeler": mat_yuz, "Açılar": mat_aci, "Çokgenler": mat_cok,
        "Çember": mat_cem, "Veri Analizi": mat_veri, "Cisimler": mat_cis
    },
    "Fen Bilimleri": {
        "Güneş Sistemi": fen_gunes, "Hücre": fen_hucre, "Kuvvet": fen_kuvvet,
        "Karışımlar": fen_madde, "Işık": fen_isik, "Üreme": fen_ureme, "Elektrik": fen_elektrik
    },
    "Türkçe": {
        "Fiiller": tur_fiil, "Zarflar": tur_zarf, "Cümlede Anlam": tur_anlam,
        "Paragraf": tur_paragraf, "Yazım": tur_yazim, "Noktalama": tur_noktalama,
        "Sözcük": tur_sozcuk, "Cümle Türleri": tur_cumle
    },
    "Sosyal Bilgiler": {
        "İletişim": sos_iletisim, "Tarih": sos_tarih, "Nüfus": sos_nufus,
        "Bilim": sos_bilim, "Ekonomi": sos_ekonomi, "Kültür": sos_kultur, "Demokrasi": sos_demokrasi
    }
}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 📊 SKOR")
    c1, c2 = st.columns(2)
    c1.metric("✅ Doğru", st.session_state.dogru)
    c2.metric("❌ Yanlış", st.session_state.yanlis)
    st.metric("🏆 Puan", st.session_state.puan)
    st.markdown("---")
    
    if st.session_state.secili_ders is None:
        sec_ders = st.selectbox("📚 Ders Seç", list(tum_dersler.keys()))
        if st.button("🚀 BAŞLA", use_container_width=True):
            st.session_state.secili_ders = sec_ders
            st.rerun()
    else:
        st.success(f"**{st.session_state.secili_ders}**")
        konular = list(tum_dersler[st.session_state.secili_ders].keys())
        sec_konu = st.selectbox("📌 Konu Seç", konular)
        if st.button("🎲 YENİ SORU", use_container_width=True):
            fonk = tum_dersler[st.session_state.secili_ders][sec_konu]
            m, d, s = fonk()
            st.session_state.aktif_soru = m
            st.session_state.aktif_cevap = d
            st.session_state.aktif_siklar = s
            st.session_state.mesajlar.append({
                "rol": "asistan",
                "icerik": f"**{st.session_state.secili_ders} - {sec_konu}**\n\n{m}\n\nA) {s[0]}\nB) {s[1]}\nC) {s[2]}\nD) {s[3]}"
            })
            st.rerun()
        if st.button("🔄 DERS DEĞİŞTİR", use_container_width=True):
            st.session_state.secili_ders = None
            st.session_state.aktif_soru = None
            st.rerun()

# ============================================================
# ANA ALAN
# ============================================================
if st.session_state.secili_ders is None:
    st.info("🎓 **Başlamak için sol panelden ders ve konu seçin!**")
else:
    for msg in st.session_state.mesajlar:
        with st.chat_message(msg["rol"]):
            st.markdown(msg["icerik"])
    
    if st.session_state.aktif_soru:
        cevap = st.chat_input("Cevabını yaz (A, B, C, D):")
        if cevap:
            st.session_state.mesajlar.append({"rol": "kullanici", "icerik": cevap})
            harf_map = {"A":0, "B":1, "C":2, "D":3}
            if cevap.strip().upper() in harf_map:
                kullanici_sec = st.session_state.aktif_siklar[harf_map[cevap.strip().upper()]]
            else:
                kullanici_sec = cevap.strip()
            if kullanici_sec == st.session_state.aktif_cevap:
                st.session_state.dogru += 1
                st.session_state.puan += 10
                yanit = f"✅ **DOĞRU!** +10 puan\n\n**Doğru:** {st.session_state.dogru} | **Yanlış:** {st.session_state.yanlis} | **Puan:** {st.session_state.puan}"
            else:
                st.session_state.yanlis += 1
                yanit = f"❌ **YANLIŞ!** Doğru cevap: **{st.session_state.aktif_cevap}**\n\n**Doğru:** {st.session_state.dogru} | **Yanlış:** {st.session_state.yanlis} | **Puan:** {st.session_state.puan}"
            st.session_state.mesajlar.append({"rol": "asistan", "icerik": yanit})
            st.session_state.aktif_soru = None
            st.session_state.aktif_cevap = None
            st.session_state.aktif_siklar = None
            st.rerun()
