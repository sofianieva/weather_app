import numpy as np
import streamlit as st

def wdir_bin(direction):
    wdir_bins=[0, 11.25, 33.75, 
               56.25, 78.75, 101.25,
               123.75, 146.25, 168.75, 
               191.25, 213.75, 236.25, 
               258.75, 281.25, 303.75, 
               326.25, 348.75, 360.00]
    wdir_labels=['North', 'NNE', 'NE', 
                 'ENE', 'East', 'ESE', 
                 'SE', 'SSE', 'South', 
                 'SSW', 'SW', 'WSW', 
                 'West', 'WNW', 'NW', 
                 'NNW', 'North']
    i = np.digitize(direction, wdir_bins) - 1
    return wdir_labels[i]


def season(date):
    now = (date.month, date.day)
    ret = "winter"
    if (3, 21) <= now < (6, 21):
        ret = "spring"
    elif (6, 21) <= now < (9, 21):
        ret = "summer"
    elif (9, 21) <= now < (12, 21):
        ret = "fall"
    return ret


def hour(min):
    return str(min // 60).zfill(2)


def minute(min):
    return str(min - 60 * int(hour(min))).zfill(2)


# Since I'll be plotting data from different years on top of each other, I need to drop the original years 
# and add a common one when plotting, so the ticks will generate automatically and correctly.
# For now the program is only working for 2022, but if I make it more general I'll need to take into account leap years
def ticks_year(leap_year=False):
    if leap_year == True:
        year = "1972-"
    else:
        year = "1970-"
    return year


def big_space(n=5):
    for _ in range(n):
        st.write("\n")


# Functions that generate some of the text and colors displayed in the app
def temp_color(temp, colors):
    if temp < 0:
        color = colors[1]
    elif 0 <= temp < 10:
        color = colors[2]
    elif 10 <= temp < 20:
        color = colors[4]
    elif 20 <= temp < 30:
        color = colors[5]
    else:
        color = colors[6]
    return color


def wind_color(wind, colors):
    if wind < 5:
        color = colors[2]
    elif 5 <= wind < 15:
        color = colors[4]
    elif 15 <= wind < 25:
        color = colors[5]
    else:
        color = colors[6]
    return color


def humidity_color(humidity, colors):
    if humidity < 60:
        color = colors[5]
    elif 60 <= humidity < 85:
        color = colors[4]
    else:
        color = colors[2]
    return color


def uvindex_color(uvindex, colors):
    if uvindex in [1, 2]:
        color = colors[4]
    elif uvindex in [3, 4, 5]:
        color = colors[5]
    elif uvindex in [6, 7]:
        color = colors[6]
    elif uvindex in [8, 9, 10]:
        color = colors[7]
    else:
        color = colors[8]
    return color


def frecuency_of_value(element, today_df, data_group_m, month_text):
    today = today_df.copy().reset_index()
    month = today["month"].values[0]
    value = today[element].values[0]
    q25 = data_group_m.loc[month, (element, "q25")]
    q75 = data_group_m.loc[month, (element, "q75")]
    text = ""
    if q25 <= value <= q75:
        text = "Normal for " + month_text
    elif value < q25:
        text = "Lower than usual  \n for " + month_text
    else:
        text = "Higher than usual  \n for " + month_text
    extra = ""
    if element in ["tavg", "tmin", "tmax"]:
        extra = " °C"
    elif element == "humidity":
        extra = " %"
    elif element == "wspd":
        extra == " km/h"
    return value, text, extra


def uvindex_text(today_df, data_group_m, month_text):
    month = today_df["month"].values[0]
    uvindex = int(today_df["uvindex"].values[0])
    first_q = data_group_m.loc[month, ("uvindex", "q25")]
    third_q = data_group_m.loc[month, ("uvindex", "q75")]
    if first_q <= uvindex <= third_q:
        text1 = "Normal for  \n " + month_text
    elif uvindex < first_q:
        text1 = "Lower than  \n usual for " +  month_text
    else:
        text1 = "Higher than  \n usual for " + month_text
    if uvindex in [1, 2]:
        text2 = "Low.<br>No protection<br>is needed"
    elif uvindex in [3, 4, 5]:
        text2 = "Moderate.<br>Some protection<br>is needed"
    elif uvindex in [6, 7]:
        text2 = "High.<br>Protection is<br>essential"
    elif uvindex in [8, 9, 10]:
        text2 = "Very high.<br>Extra protection<br>is needed"
    elif uvindex in [11]:
        text2 = "Extreme.<br>Avoid going<br>outdoor"
    return text1, text2