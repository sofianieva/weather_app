# :partly_sunny: Today's vs. Past London Weather app :partly_sunny:

Web app that compares today's weather in London with the weather on similar dates from the past 5 years. The project features data retrieval from public API's, cleaning, exploration and an interactive visualization with plotly and streamlit. It's hosted on AWS, so if you want to use it just go to http://35.88.156.189:8501/

In this repo you can find:
- [data_preprocessing_and_eda notebook](https://github.com/sofianieva/weather_app/blob/main/data_preprocessing_and_eda.ipynb) used to generate one of the dataset needed (weather_data_london_01012017_31122021) from datasets downloaded from https://meteostat.net/ and https://www.visualcrossing.com/  
- Dataset sun_london_2022 downloaded from https://www.sunrise-and-sunset.com/en/sun/united-kingdom/london/2022
- Files .py with the streamlit code and functions to run the app

If you would like to clone the repo and run the app locally, first you would need to generate your own API keys for meteostat (RapidAPI) and vissualcrosing. Just go to their pages, choose their free tier and save the keys in a api_keys.json file containing {"RAPIDAPI_KEY": YourKey, "VC_KEY": YourKey}. Then use the comand "streamlit run main.py" in command line.

Dependecies: pandas, numpy, json, datetime, plotly, calendar, pendulum, streamlit, requests
