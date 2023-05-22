import pandas as pd
import numpy as np
import json
import datetime
import plotly.express as px
import calendar
import pendulum
import streamlit as st
from utils import season, big_space, temp_color, wind_color, humidity_color, uvindex_color, frecuency_of_value, uvindex_text
from plots import hourly_plots, quartiles_plots, season_wind_rose, sun_plot, day_length_plot, update_fig
from api_requests import ms_api, vc_api
from preprocessing import today_hourly_prepocessing, today_daily_prepocessing, sun_preprocessing, format_sun_plot, monthly_agg, seasonly_agg, common_directions
st.set_page_config(layout="wide", page_icon="🌤️", page_title="Weather, today vs. past")


# Loading historical data
data = pd.read_csv(
    "weather_data_london_01012017_31122021.csv",
    index_col="date",
    dtype={"year": str, "month": str, "day": str},
)


# Getting today's date and other info needed for the labels, titles and hover info of the plots
now = pendulum.now("Europe/London")
today = datetime.date(now.year, now.month, now.day)
today_str = today.strftime("%Y-%m-%d")
today_text = today.strftime("%d %B %Y")

month_str = today.strftime("%m")
month_text = today.strftime("%B")

season_text = season(today).capitalize()

leap_year = calendar.isleap(today.year)


# API's requests and preprocessing of the data retrieved
#with open("api_keys.json") as keys:
#    key_dict = json.load(keys)
    
#RAPIDAPI_KEY = key_dict["RAPIDAPI_KEY"]
#VC_KEY = key_dict["VC_KEY"]

## Today's hourly data
try:
    response_ms_dict = ms_api(today_str, RAPIDAPI_KEY)
except:
    st.warning("The request to meteostat API fail, please try refreshing the page or come back later")

today_h_df = today_hourly_prepocessing(response_ms_dict)

## Today's daily data
try:
    response_vc_dict = vc_api(today_str, VC_KEY)
except:
    st.warning("The request to visualcrossing API fail, please try refreshing the page or come back later")

today_df = today_daily_prepocessing(response_vc_dict, today_h_df)


# Loading and preprocessing sunrise and sunset info
sun_2022 = pd.read_csv("sun_london_2022.csv", usecols=["Date", "Sunrise", "Sunset", "Day length"])
sun_2022 = sun_preprocessing(sun_2022)

today_sun_df = sun_2022[sun_2022["date"] == list(today_df.index)[0]]

sun_2022 = format_sun_plot(sun_2022, leap_year=leap_year)
today_sun_df = format_sun_plot(today_sun_df, leap_year=leap_year)


# Monthly and seasonly aggregations of the last 5 years needed for some plots and displayed text
data_group_m = monthly_agg(data)
data_group_s = seasonly_agg(data)


# Color palette
colors = px.colors.qualitative.Prism


############################################################################################################

# Streamlit

st.title("Today's vs. Past London Weather")
st.header(today_text)
st.subheader("What's the weather like today and how does it compare with similar dates in the last 5 years?")
st.markdown('We will consider that a value is normal for a certain month and element of weather if it falls\
     between the first quartile (Q1) and the third quartile (Q3) considering all the values for that element\
     and month in the last 5 years. It will be lower than usual if it falls below Q1 and higher than usual if\
     it falls above Q3. This means that, for example, in a given month, aproximately 50% of the days will have\
     normal temperature, 25% will be a bit colder than usual and 25% a bit hotter.')
font_size = str(30)

with st.expander("Temperature", expanded=True):

    row00, row01, row02, row03, row04, row05 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row00:
        st.write(' ')

    with row01:
        st.subheader("Today")
        st.write('\n')
        st.markdown('Min:')
        temp_min, text, _ = frecuency_of_value('tmin', today_df, data_group_m, month_text)
        color_temp_min = temp_color(temp_min, colors)
        html_temp_min = '<p style="color:' + color_temp_min + '; font-size: ' + font_size + 'px;">' + str(temp_min) + ' °C</p>'
        st.markdown(html_temp_min , unsafe_allow_html=True)
        if not text[:6]=='Normal':    
            st.markdown(text)

    with row02:
        big_space()
        st.markdown('Max:')
        temp_max, text, _ = frecuency_of_value('tmax', today_df, data_group_m, month_text)
        color_temp_max = temp_color(temp_max, colors)
        html_temp_max = '<p style="color:' + color_temp_max + '; font-size: ' + font_size + 'px;">' + str(temp_max) + ' °C</p>'
        st.markdown(html_temp_max, unsafe_allow_html=True)
        if not text[:6]=='Normal':
            st.markdown(text)
    
    with row03:
        big_space()
        st.markdown('Avg:')
        temp_avg, text, _ = frecuency_of_value('tavg', today_df, data_group_m, month_text)
        color_temp_avg = temp_color(temp_avg, colors)
        html_temp_avg = '<p style="color:' + color_temp_avg + '; font-size: ' + font_size + 'px;">' + str(temp_avg) + ' °C</p>'
        st.markdown(html_temp_avg , unsafe_allow_html=True)
        st.markdown(text)
        
    with row04:
        dtick_temp = 1 if int(today_df['tmax']-today_df['tmin'])<8 else 2
        temp_fig = hourly_plots(today_h_df, 'temp', 'Temperature (°C)', '°C', color_temp_avg, 'Hourly temperature', dtick_temp, today_text)
        update_fig(temp_fig)
        st.plotly_chart(temp_fig, use_container_width=True)
        
    with row05:
        st.write('\n')

    
    row10, row11, row12, row13, row14, row15 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row10:
        st.write(' ')

    with row11:
        st.subheader("Last 5 years")
        st.write('\n')
        st.write('\n')
        st.markdown('Lowest for ' + month_text + ':')
        lowest_temp = data_group_m.loc[month_str, ('tmin', 'min')]
        color_temp_min = temp_color(lowest_temp, colors)
        html_temp_min = '<p style="color:' + color_temp_min + '; font-size: ' + font_size + 'px;">' + str(lowest_temp) + ' °C</p>'
        st.markdown(html_temp_min , unsafe_allow_html=True)
 
    with row12:
        big_space()
        st.write('\n')
        st.markdown('Highest for ' + month_text + ':')
        highest_temp = data_group_m.loc[month_str, ('tmax', 'max')]
        color_temp_max = temp_color(highest_temp, colors)
        html_temp_max = '<p style="color:' + color_temp_max + '; font-size: ' + font_size + 'px;">' + str(highest_temp) + ' °C</p>'
        st.markdown(html_temp_max, unsafe_allow_html=True)
    
    with row13:
        big_space()
        st.write('\n')
        st.markdown('Average for ' + month_text + ':')
        avg_temp = data_group_m.loc[month_str, ('tavg', 'mean')]
        color_temp_avg = temp_color(avg_temp, colors)
        html_temp_avg = '<p style="color:' + color_temp_avg + '; font-size: ' + font_size + 'px;">' + str(avg_temp) + ' °C</p>'
        st.markdown(html_temp_avg , unsafe_allow_html=True)
        
    with row14:
        title = "Normal avg temperature for each month and for today"
        quartile_temp = quartiles_plots(data, data_group_m, today_df, 'tavg', '°C', 'Temperature (°C)', color_temp_avg, today, leap_year=leap_year, title = title)
        update_fig(quartile_temp)
        st.plotly_chart(quartile_temp, use_container_width=True)
         
    with row15:
        st.write('\n')

with st.expander("Humidity", expanded=False):

    row20, row21, row22, row23, row24, row25 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row20:
        st.write(' ')

    with row21:
        st.subheader("Today")
        st.write('\n')
        st.markdown('Min:')
        hum_min = today_h_df['rhum'].min()
        color_hum_min = humidity_color(hum_min, colors)
        html_hum_min = '<p style="color:' + color_hum_min + '; font-size: ' + font_size + 'px;">' + str(hum_min) + ' %</p>'
        st.markdown(html_hum_min , unsafe_allow_html=True)
        
    with row22:
        big_space()
        st.markdown('Max:')
        hum_max = today_h_df['rhum'].max()
        color_hum_max = humidity_color(hum_max, colors)
        html_hum_max = '<p style="color:' + color_hum_max + '; font-size: ' + font_size + 'px;">' + str(hum_max) + ' %</p>'
        st.markdown(html_hum_max, unsafe_allow_html=True)
    
    with row23:
        big_space()
        st.markdown('Avg:')
        hum_avg, text, _ = frecuency_of_value('humidity', today_df, data_group_m, month_text)
        color_hum_avg = humidity_color(hum_avg, colors)
        html_hum_avg = '<p style="color:' + color_hum_avg + '; font-size: ' + font_size + 'px;">' + str(hum_avg) + ' %</p>'
        st.markdown(html_hum_avg , unsafe_allow_html=True)
        st.markdown(text)
        
    with row24:
        dtick_hum = 5 if today_h_df['rhum'].max()-today_h_df['rhum'].min()<30 else 10
        hum_fig = hourly_plots(today_h_df, 'rhum', 'Humidity (%)', '%', color_hum_avg, 'Hourly humidity', dtick_hum, today_text)
        update_fig(hum_fig)
        st.plotly_chart(hum_fig, use_container_width=True)
        
    with row25:
        st.write('\n')

    
    row30, row31, row32, row33, row34 = st.columns([0.3, 1.3, 1.7, 4, 0.5])

    with row30:
        st.write(' ')

    with row31:
        st.subheader("Last 5 years")
        st.write('\n')
        st.write('\n')
        st.markdown('Average for ' + month_text + ':')
        avg_hum = data_group_m.loc[month_str, ('humidity', 'mean')]
        color_hum_avg = humidity_color(avg_hum, colors)
        html_hum_avg = '<p style="color:' + color_hum_avg + '; font-size: ' + font_size + 'px;">' + str(avg_hum) + ' %</p>'
        st.markdown(html_hum_avg , unsafe_allow_html=True)
 
    with row32:
        big_space()
        st.write('\n')
        st.markdown('Average for ' + season_text + ':')
        avg_hum = data_group_s.loc[season(today), ('humidity', 'mean')]
        color_hum_avg = humidity_color(avg_hum, colors)
        html_hum_avg = '<p style="color:' + color_hum_avg + '; font-size: ' + font_size + 'px;">' + str(avg_hum) + ' %</p>'
        st.markdown(html_hum_avg , unsafe_allow_html=True)   
        
    with row33:
        title = "Normal avg humidity for each month and for today"
        quartile_hum = quartiles_plots(data, data_group_m, today_df, 'humidity', '%', 'Humidity (%)', color_hum_avg, today, leap_year=leap_year, title = title)
        update_fig(quartile_hum)
        st.plotly_chart(quartile_hum, use_container_width=True)
        
    with row34:
        st.write('\n')

with st.expander("Wind", expanded=False):
    
    row40, row41, row42, row43, row44, row45 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row40:
        st.write(' ')

    with row41:
        st.subheader("Today")
        st.write('\n')
        st.markdown('Min:')
        wind_min = int(np.round(today_h_df['wspd'].min()))
        color_wind_min = wind_color(wind_min, colors)
        html_wind_min = '<p style="color:' + color_wind_min + '; font-size: ' + font_size + 'px;">' + str(wind_min) + ' km/h</p>'
        st.markdown(html_wind_min , unsafe_allow_html=True)
  
    with row42:
        big_space()
        st.markdown('Max:')
        wind_max = int(np.round(today_h_df['wspd'].max()))
        color_wind_max = wind_color(wind_max, colors)
        html_wind_max = '<p style="color:' + color_wind_max + '; font-size: ' + font_size + 'px;">' + str(wind_max) + ' km/h</p>'
        st.markdown(html_wind_max , unsafe_allow_html=True)

    with row43:
        big_space()
        st.markdown('Avg:')
        wind_avg, text, _ = frecuency_of_value('wspd', today_df, data_group_m, month_text)
        wind_avg = wind_avg
        color_wind_avg = wind_color(wind_avg, colors)
        html_wind_avg = '<p style="color:' + color_wind_avg + '; font-size: ' + font_size + 'px;">' + str(wind_avg) + ' km/h</p>'
        st.markdown(html_wind_avg , unsafe_allow_html=True)
        st.markdown(text)
       
    with row44:

        if today_h_df['wspd'].max()-today_h_df['wspd'].min()<8:
            dtick_wind = 1 
        elif today_h_df['wspd'].max()-today_h_df['wspd'].min()<20:
            dtick_wind = 2
        else:
            dtick_wind = 3

        wind_fig = hourly_plots(today_h_df, 'wspd', 'Wind Speed (km/h)', ' km/h', color_wind_avg, 'Hourly wind speed and direction', dtick_wind, today_text)
        update_fig(wind_fig)
        st.plotly_chart(wind_fig, use_container_width=True)

    with row45:
        st.write(' ')
    
    
    row50, row51, row52, row53, row54 = st.columns([0.3, 1.3, 1.7, 4, 0.5])

    with row50:
        st.write(' ')

    with row51:
        st.subheader("Last 5 years")
        st.write('\n')
        st.write('\n')
        st.markdown('Average for ' + month_text + ':')
        avg_wind = data_group_m.loc[month_str, ('wspd', 'mean')]
        color_wind_avg = wind_color(avg_wind, colors)
        html_wind_avg = '<p style="color:' + color_wind_avg + '; font-size: ' + font_size + 'px;">' + str(avg_wind) + ' km/h</p>'
        st.markdown(html_wind_avg , unsafe_allow_html=True)

    with row52:
        big_space()
        st.write('\n')
        st.markdown('Average for ' + season_text + ':')
        avg_wind = data_group_s.loc[season(today), ('wspd', 'mean')]
        color_wind_avg = wind_color(avg_wind, colors)
        html_wind_avg = '<p style="color:' + color_wind_avg + '; font-size: ' + font_size + 'px;">' + str(avg_wind) + ' km/h</p>'
        st.markdown(html_wind_avg , unsafe_allow_html=True)
        
    with row53:
        title = "Normal avg wind speed for each month and for today"
        quartile_wind = quartiles_plots(data, data_group_m, today_df, 'wspd', 'km/h', 'Wind Speed (km/h)', color_wind_avg, today, leap_year=leap_year, title = title)
        update_fig(quartile_wind)
        st.plotly_chart(quartile_wind, use_container_width=True)
        
    with row54:
        st.write('\n')

    row60, row61, row62, row63, row64 = st.columns([0.3, 1.3, 1.7, 4, 0.5])
    
    with row60:
        st.write(' ')

    font_size2 = str(24)

    season_df, wind_rose = season_wind_rose(data, colors[4:], season(today))
    directions, main_dir, common, i = common_directions(today_h_df, today, season_df)

    with row61:
        st.subheader("Wind Direction")
        st.write('\n')
        st.write('\n')
        st.markdown('Main directions today:')
        html_directions = '<p style="font-size: ' + font_size2 + 'px;">' + ', '.join(directions) + '</p>'
        st.markdown(html_directions, unsafe_allow_html=True)
        if main_dir in common:
            st.markdown('Normal for ' + season_text)

    with row62:
        big_space()
        st.write('\n')
        st.markdown('Most common directions in ' + season_text + ':')
        html_directions1 = '<p style="font-size: ' + font_size2 + 'px;">' + ', '.join(common[:i]) + ',</p>'
        st.markdown(html_directions1 , unsafe_allow_html=True)
        html_directions2 = '<p style="font-size: ' + font_size2 + 'px;">' + ', '.join(common[i:]) + '</p>'
        st.markdown(html_directions2 , unsafe_allow_html=True)
        
    
    with row63:
        st.plotly_chart(wind_rose, use_container_width=True)
        
    with row64:
        st.write('\n')


with st.expander("UV Index", expanded=False):

    row70, row71, row72, row73, row74, row75 = st.columns([0.3, 0.9, 1.15, 0.95, 4, 0.5])

    with row70:
        st.write(' ')

    uv_text1, uv_text2 =  uvindex_text(today_df, data_group_m, month_text)

    with row71:
        big_space()
        st.markdown('Max UV Index today:')
        uvindex = int(today_df['uvindex'].values[0])
        color_uvindex = uvindex_color(uvindex, colors)
        html_uvindex = '<p1 style="color:' + color_uvindex + '; font-size: ' + font_size + 'px;"> ' + str(uvindex) + '</p>'
        st.markdown(html_uvindex , unsafe_allow_html=True)
        st.markdown(uv_text1)
        
    with row72:
        big_space()
        st.markdown('Recomendation:')
        html_uvindex = '<p style="color:' + color_uvindex + '; font-size: ' + font_size2 + 'px;">' + uv_text2 + '</p>'
        st.markdown(html_uvindex, unsafe_allow_html=True)
    
    with row73:
        big_space()
        st.markdown('Average for ' + month_text + ':')
        avg_uv = int(data_group_m.loc[month_str, ('uvindex', 'mean')])
        color_uv_avg = uvindex_color(avg_uv, colors)
        html_uv_avg = '<p style="color:' + color_uv_avg + '; font-size: ' + font_size + 'px;">' + str(avg_uv) + '</p>'
        st.markdown(html_uv_avg , unsafe_allow_html=True)
        
    with row74:
        title = "Normal UV index for each month and for today"
        quartile_uv = quartiles_plots(data, data_group_m, today_df, 'uvindex', '', 'UV Index', color_uv_avg, today, leap_year=leap_year, title = title)
        update_fig(quartile_uv)
        st.plotly_chart(quartile_uv, use_container_width=True)
        
    with row75:
        st.write('\n')


with st.expander("More", expanded=False):
    
    row80, row81, row82, row83, row84, row85 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row80:
        st.write(' ')

    with row81:
        st.subheader("Sunrise")
        st.write('\n')
        st.write('\n')
        st.markdown('Today:')
        st.markdown('<p style="font-size: ' + font_size + 'px;">' + today_df['sunrise'].values[0][:5] + '</p>' , unsafe_allow_html=True)
        
    with row82:
        big_space()
        st.write('\n')
        st.markdown('Earliest of the year:')
        earliest_sunrise = sun_2022.loc[sun_2022.sunrise_min.idxmin(),:]
        earliest_sunrise_time = earliest_sunrise['sunrise_hover']
        st.markdown('<p style="font-size: ' + font_size + 'px;">' + earliest_sunrise_time + '</p>' , unsafe_allow_html=True)

        
    with row83:
        big_space()
        st.write('\n')
        st.markdown('Latest of the year:')
        lastest_sunrise = sun_2022.loc[sun_2022.sunrise_min.idxmax(),:]
        lastest_sunrise_time = lastest_sunrise['sunrise_hover']
        st.markdown('<p style="font-size: ' + font_size + 'px;">' + lastest_sunrise_time + '</p>' , unsafe_allow_html=True)

        
    with row84:
        title='Time of sunrise during the year and today'
        sunrise_fig = sun_plot(today_sun_df, sun_2022, 'sunrise_min', 'sunrise_hover', title, colors, 5, 355, 418)
        update_fig(sunrise_fig)
        st.plotly_chart(sunrise_fig, use_container_width=True)
        
       
    with row85:
        st.write(' ')
 
    row90, row91, row92, row93, row94, row95 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row90:
        st.write(' ')

    with row91:
        st.subheader("Sunset")
        st.write('\n')
        st.write('\n')
        st.markdown('Today:')
        st.markdown('<p style="font-size: ' + font_size + 'px;">' + today_df['sunset'].values[0][:5] + '</p>' , unsafe_allow_html=True)
 
    with row92:
        big_space()
        st.write('\n')
        st.markdown('Earliest of the year:')
        earliest_sunset = sun_2022.loc[sun_2022.sunset_min.idxmin(),:]
        earliest_sunset_time = earliest_sunset['sunset_hover']
        st.markdown('<p style="font-size: ' + font_size + 'px;">' + earliest_sunset_time + '</p>' , unsafe_allow_html=True)

        
    with row93:
        big_space()
        st.write('\n')
        st.markdown('Latest of the year:')
        lastest_sunset = sun_2022.loc[sun_2022.sunset_min.idxmax(),:]
        lastest_sunset_time = lastest_sunset['sunset_hover']
        st.markdown('<p style="font-size: ' + font_size + 'px;">' + lastest_sunset_time + '</p>' , unsafe_allow_html=True)

        
    with row94:
        title='Time of sunset during the year and today'
        sunset_fig = sun_plot(today_sun_df, sun_2022, 'sunset_min', 'sunset_hover', title, colors, 8, 1115, 1010)
        update_fig(sunset_fig)
        st.plotly_chart(sunset_fig, use_container_width=True)

    with row95:
        st.write(' ')
         
    row100, row101, row102, row103, row104, row105 = st.columns([0.3, 1, 1, 1, 4, 0.5])

    with row100:
        st.write(' ')

    with row101:
        st.subheader("Daylight")
        st.write('\n')
        st.write('\n')
        st.markdown('Today:')
        daytime = today_sun_df['durationday_h'].values[0] + ' ' + today_sun_df['durationday_m'].values[0]
        st.markdown('<p style="font-size: ' + font_size2 + 'px;">' + daytime + '</p>' , unsafe_allow_html=True)
   
    with row102:
        big_space()
        st.write('\n')
        st.markdown('Longest day:')
        longest_day = sun_2022.loc[sun_2022.durationday.idxmax(),:]
        longest_day_length = longest_day['durationday_h'] + ' ' + longest_day['durationday_m']
        st.markdown('<p style="font-size: ' + font_size2 + 'px;">' + longest_day_length, unsafe_allow_html=True)

    with row103:
        big_space()
        st.write('\n')
        st.markdown('Shortest day:')
        shortest_day = sun_2022.loc[sun_2022.durationday.idxmin(),:]
        shortest_day_length = shortest_day['durationday_h'] + ' ' + shortest_day['durationday_m']
        st.markdown('<p style="font-size: ' + font_size2 + 'px;">' + shortest_day_length, unsafe_allow_html=True)


    with row104:
        length_fig = day_length_plot(sun_2022, colors[4], today_sun_df)
        update_fig(length_fig)
        st.plotly_chart(length_fig, use_container_width=True)

    with row105:
        st.write(' ')
