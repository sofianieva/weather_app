import requests
import json
import streamlit as st


 # API request (hourly data)
@st.cache
def ms_api(today_str, RAPIDAPI_KEY):
    url = "https://meteostat.p.rapidapi.com/stations/hourly"
    querystring = {"station": "03672", "start": today_str, "end": today_str}
    headers = {
        "X-RapidAPI-Host": "meteostat.p.rapidapi.com",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_dict = json.loads(response.text)
    return response_dict


# API request (dayly data)
@st.cache
def vc_api(today_str, VC_KEY):
    _ = today_str
    params = {
        "key": VC_KEY,
        "include": "days",
        "elements": "datetime,humidity,uvindex,sunrise,sunset",
    }
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/today"

    response = requests.get(url, params=params)
    response_dict = json.loads(response.text)
    return response_dict