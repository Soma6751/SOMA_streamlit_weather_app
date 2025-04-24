import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import datetime 

API_KEY=st.secrets["openweather"]["api_key"]
BASE_URL_ACTUAL="https://api.openweathermap.org/data/2.5/weather?q="
BASE_URL_FORECAST="https://api.openweathermap.org/data/2.5/forecast?q="

@st.cache_data(ttl=3600)
def actual_wheather_in_city(city):
    print(f"Actual city : {city}")

    url = f"{BASE_URL_ACTUAL}{city}&appid={API_KEY}&units=metric"
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



st.title("Robot Dreams Python - Weather Map & Data Visualization App")
st.subheader("Made by Soma")

city = st.text_input("Enter City name: ", "Budapest")

data = actual_wheather_in_city(city)

if data:
 
    st.header(f"Current Weather in {city}")

    kpi1, kpi2, kpi3 = st.columns(3)

    #KPI
    with kpi1:
        st.metric(label="Temperature(°C)", value=f"{data['main']['temp']}°C")
    with kpi2:
        st.metric(label="Humidity (%)", value=f"{data['main']['humidity']}%")
    with kpi3:
        st.metric(label="Wind speed (m/s)", value=f"{data['wind']['speed']}m/s")

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
           
            df_temp = pd.DataFrame([df["dt_txt"], df["main"]])
            
            # Első sor az előrejelzés időpontja szövegesen
            first_row = df_temp.iloc[0]

            # Második sor dictionary-ből a hőmérséklet értékek
            second_row = df_temp.iloc[1].apply(lambda x: x["temp"])

            # Harmadik sor az érzett hőmérsékleti értékek
            third_row = df_temp.iloc[1].apply(lambda y: y["feels_like"])

            # Új DataFrame összeállítása
            df_graf = pd.DataFrame({
                'timetext': first_row.values,
                'temperature': second_row.values,
                'feels_like': third_row.values
                })      
            st.title("Temperature Trends (Next 5 days)") 
            st.line_chart(df_graf.set_index('timetext'))               
    else:
        st.error("No data available for forecast. Check the city name!")


else:
    st.error("No data available for actual weather. Check the city name!")


