import streamlit as st
import json
import pandas as pd
import plotly.express as px
from calculator import hesapla_capex, hesapla_opex, hesapla_aep, hesapla_lcoe
from streamlit_folium import st_folium
import folium
from geopy.distance import geodesic
import joblib
import numpy as np

# Sayfa ayarı
st.set_page_config(page_title="Offshore Rüzgar Ekonomik Analizi", layout="wide")
st.title("🗺️ Haritalı Offshore Rüzgar Enerji Analizi")

# JSON verisini yükle
with open("ruzgar_enerjisi_verisi (1).json") as f:
    regions = json.load(f)

# Model dosyalarını yükle
model = joblib.load("bolge_tahmin_modeli.pkl")
classes = np.load("label_encoder_classess.npy", allow_pickle=True)

# En yakın şehri bulan fonksiyon
def en_yakin_sehir(koordinat, sehirler):
    min_sehir = None
    min_mesafe = float("inf")
    for r in sehirler:
        sehir_koordinat = (r["lat"], r["lon"])
        uzaklik = geodesic(koordinat, sehir_koordinat).km
        if uzaklik < min_mesafe:
            min_mesafe = uzaklik
            min_sehir = r
    return min_sehir

# Harita başlat
st.subheader("🌍 Haritadan Nokta Seçin")
m = folium.Map(location=[41.0, 29.0], zoom_start=6)
folium.LatLngPopup().add_to(m)
map_data = st_folium(m, width=700, height=500)

secilen_sehir = None
tahmin_edilen_bolge = None

if map_data and map_data["last_clicked"]:
    secilen_koordinat = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    
    # ✅ Model tahmini yapılır
    bolge_tahmini_index = model.predict([secilen_koordinat])[0]
    tahmin_edilen_bolge = classes[bolge_tahmini_index]
    st.info(f"🧠 Model Tahmini: **{tahmin_edilen_bolge}** bölgesi")
    
    # ✅ En yakın şehir bulunur
    secilen_sehir = en_yakin_sehir(secilen_koordinat, regions)
    
    if secilen_sehir:
        st.success(f"📌 Seçilen Noktaya En Yakın Şehir: **{secilen_sehir['city']}** ({secilen_sehir['bolge']})")
        mesafe_default = secilen_sehir["mesafe_kiyiya"]
    else:
        st.warning("Haritadan geçerli bir nokta seçiniz.")
        mesafe_default = 15
else:
    st.info("Haritadan bir nokta seçerseniz model tahmini ve şehir bilgisi görüntülenir.")
    mesafe_default = 15

# Kullanıcı girişi
st.subheader("🔢 Proje Parametreleri")
kapasite_mw = st.number_input("Toplam Kurulu Güç (MW)", min_value=10, max_value=1000, value=100)
kapasite_faktoru = st.slider("Kapasite Faktörü", 0.1, 0.7, value=0.42)
derinlik = st.number_input("Deniz Derinliği (m)", value=25.0)
mesafe = st.number_input("Kıyıya Uzaklık (km)", value=float(mesafe_default))

# Hesaplama seçeneği
st.subheader("⚙️ Karşılaştırma Modu Seç")
mod_sec = st.radio("Hangi değerler şehre özel olsun?", 
                   ["Sadece mesafe kullanıcıdan", "Derinlik ve mesafe şehirden"])

# Hesapla
if st.button("📊 Hesapla") and tahmin_edilen_bolge:
    bolge_sehirleri = [r for r in regions if r["bolge"] == tahmin_edilen_bolge]

    opex = hesapla_opex(kapasite_mw)
    aep = hesapla_aep(kapasite_mw, kapasite_faktoru)

    data = []

    for r in bolge_sehirleri:
        if mod_sec == "Sadece mesafe kullanıcıdan":
            derinlik_r = derinlik
            mesafe_r = mesafe
        else:
            derinlik_r = r["derinlik"]
            mesafe_r = r["mesafe_kiyiya"]

        capex_r = hesapla_capex(kapasite_mw, derinlik_r, mesafe_r)
        lcoe_r = hesapla_lcoe(capex_r, opex, aep)

        data.append({
            "Şehir": r["city"],
            "Derinlik (m)": derinlik_r,
            "Mesafe (km)": mesafe_r,
            "LCOE": lcoe_r,
            "AEP (MWh)": aep
        })

    df = pd.DataFrame(data)

    st.subheader(f"📉 {tahmin_edilen_bolge} Bölgesi Şehir LCOE Karşılaştırması")
    fig = px.bar(df, x="Şehir", y="LCOE", color="Şehir", text_auto=".2f", title="LCOE Karşılaştırması")
    st.plotly_chart(fig)

    en_uygun = df.sort_values(by="LCOE").iloc[0]
    st.success(f"✅ En Uygun Şehir: **{en_uygun['Şehir']}** (LCOE: ${en_uygun['LCOE']:.2f} / MWh)")
    st.dataframe(df.sort_values(by="LCOE"), use_container_width=True)
