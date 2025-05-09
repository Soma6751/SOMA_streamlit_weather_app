import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import base64

API_KEY=st.secrets["openweather"]["api_key"]
BASE_URL_ACTUAL="https://api.openweathermap.org/data/2.5/weather?q="
BASE_URL_FORECAST="https://api.openweathermap.org/data/2.5/forecast?q="

@st.cache_data(ttl=3600)
def actual_wheather_in_city(city):
    print(f"Actual city : {city}")

    url = f"{BASE_URL_ACTUAL}{city}&appid={API_KEY}&units=metric&lang=hu"
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Hibás adatok: {response.status_code} - {response.text}")


@st.cache_data(ttl=86400)
def forecast_wheather_in_city(city):
    print(f"Actual city : {city}")

    url = f"{BASE_URL_FORECAST}{city}&appid={API_KEY}&units=metric"
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Hibás adatok: {response.status_code} - {response.text}")


# SAJÁT FEJLÉC

# Kép beolvasása és base64-re kódolása
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Kép konvertálása base64-re
image_path = "logo.png" 
img_base64 = get_base64_of_image(image_path)

# HTML a cím + jobb oldali kép kombinációjához
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1 style="margin: 0;">Hunter Forecast</h1>
        <img src="data:image/png;base64,{img_base64}" width="300">
    </div>
    """,
    unsafe_allow_html=True
)


# SAJÁT TÁBLÁZAT FORMÁZÁS

# HTML + CSS stílus
css = """
<style>
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-family: Verdana, sans-serif;
    font-size: 16px;
}
.custom-table th, .custom-table td {
    border: 1px solid #000;
    padding: 5px;
    text-align: right;
}
.custom-table th {
    background-color: #eee;
    color: black;
}
.custom-table tr:nth-child(even) {
    background-color: #f0f0f0;
}
.custom-table tr:hover {
    background-color: #eee;
}
</style>
"""

st.subheader("Made by Soma")

city = st.text_input("Add meg a helyiség nevét: ", "Budapest")

data = actual_wheather_in_city(city)

if data:
 
    st.header(f"Aktuális adatok {city}")
    
    kpi1, kpi2, kpi3 = st.columns(3)

    #KPI
    with kpi1:
        st.metric(label="Hőmérséklet (°C)", value=f"{data['main']['temp']}°C")
    with kpi2:
        st.metric(label="Páratartalom (%)", value=f"{data['main']['humidity']}%")
    with kpi3:
        st.metric(label="Hőérzet (°C)", value=f"{data['main']['feels_like']}°C")

    kpi4, kpi5, kpi6 = st.columns(3)
    with kpi4:
        st.metric(label="Szélsebesség (m/s)", value=f"{data['wind']['speed']}m/s")
    with kpi5:
        st.metric(label="Szélirány (fok)", value=f"{data['wind']['deg']}°")
    with kpi6:
        st.metric(label="Légnyomás (hPa)", value=f"{data['main']['grnd_level']}hPa")

    kpi7, kpi8, kpi9 = st.columns(3)
    with kpi7:
        st.metric(label="Felhősödés (%)", value=f"{data['clouds']['all']}%")
    with kpi8:
        st.metric(label="Égbolt", value=f"{data['weather'][0]['description']}")
    with kpi9:
        st.metric(label="Látótávolság (m)", value=f"{data['visibility']}m")

    # térkép
    df_map = pd.DataFrame({
        'lat': [data["coord"]["lat"]],
        'lon': [data["coord"]["lon"]]
    })
    st.map(df_map)

    # Előrejelzés - FORECAST
    forecast_data = forecast_wheather_in_city(city)

    
    if forecast_data:
        if 'list' in forecast_data:
            
            df = pd.DataFrame(forecast_data["list"])
           
            df_temp = pd.DataFrame([df["dt_txt"], df["main"], df["weather"], df["clouds"], df["wind"], df["visibility"]])
            
            # Első oszlop az előrejelzés időpontja szövegesen
            col01 = pd.to_datetime(df_temp.iloc[0]).dt.strftime("%m-%d %H")

            # Második oszlop dictionary-ből a hőmérséklet értékek
            col02 = df_temp.iloc[1].apply(lambda x: x["temp"])

            # Harmadik oszlop Páratartalom
            col03 = df_temp.iloc[1].apply(lambda y: y["humidity"])

            # Negyedik oszlop az érzett hőmérsékleti értékek
            col04 = df_temp.iloc[1].apply(lambda y: y["feels_like"])

            # Szélsebesség
            col05 = df_temp.iloc[4].apply(lambda y: y["speed"])

            # Szélirány
            col06 = df_temp.iloc[4].apply(lambda y: y["deg"])

            # Légnyomás
            col07 = df_temp.iloc[1].apply(lambda y: y["grnd_level"])

            # Felhősödés
            col08 = df_temp.iloc[3].apply(lambda y: y["all"])

            
            # Új DataFrame összeállítása
            df_graf = pd.DataFrame({
                'Időpont': col01.values,
                'Hőmérs.': col02.values,
                'Pára': col03.values,
                'Hőérzet': col04.values,
                'Szélseb.': col05.values,
                'irány': col06.values,
                'Légnyomás': col07.values,
                'Felhő': col08.values,
                'Látás': df_temp.iloc[5].values
                
                })      
            st.title("Előrejelzés a következő 5 napra") 
            # st.dataframe(df_graf)               
            # DataFrame -> HTML (index elhagyása)
            html_table = df_graf.to_html(classes="custom-table", index=False, escape=False)

            # Megjelenítés Streamlit-ben
            st.markdown(css + html_table, unsafe_allow_html=True)

                         
    else:
        st.error("No data available for forecast. Check the city name!")


else:
    st.error("No data available for actual weather. Check the city name!")


