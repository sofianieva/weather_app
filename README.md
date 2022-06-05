## :partly_sunny: Today's vs. Past London Weather app :partly_sunny:

Web app that compares today's weather in London with the weather on similar dates from the past 5 years. The project features data retrieval from public API's, cleaning, exploration and an interactive visualization with plotly and streamlit. It's hosted on AWS, so if you want to use it just go to http://35.88.156.189:8501/ (the layout is not optimised for mobile phones)

In this repo you can find:
- [data_preprocessing_and_eda notebook](https://github.com/sofianieva/weather_app/blob/main/data_preprocessing_and_eda.ipynb) used to generate one of the dataset needed (weather_data_london_01012017_31122021) from datasets downloaded from https://meteostat.net/ and https://www.visualcrossing.com/  
- Dataset sun_london_2022 downloaded from https://www.sunrise-and-sunset.com/en/sun/united-kingdom/london/2022
- Files .py with the streamlit code and functions to run the app

If you would like to clone the repo and run the app locally, first you would need to generate your own API keys for meteostat (RapidAPI) and vissualcrosing. Just go to their pages, choose their free tier and save the keys in a api_keys.json file containing {"RAPIDAPI_KEY": YourKey, "VC_KEY": YourKey}. Then use the comand "streamlit run main.py" in command line.

Dependencies: pandas, numpy, json, datetime, plotly, calendar, pendulum, streamlit, requests

Future improvements:
- Add feature to be able to choose units of measurement, i.e., °C or °F, Km/h or mph or knots, etc.
- Do it for other cities 
- Add cloud and rain information
- Analise other methods to determine common/uncommon weather

Personal motivation for developing this project: One of the first things I do when I wake up is check what's the weather going to be like. I just love to see numbers that contain valuable information to help me decide what to wear. Then I realised, when I moved to a new city around a year ago, that it wasn't enough for me to just check today's weather, I also wanted information about what the weather was usually like at that time of the year. For example, suppose it's cold today, is it an unusually cold day in summer or is summer over and I have to rearrange my wardrobe? I realised I couldn't answer this because I had never experienced a summer there before!. So, yes, I might be a bit obsessed with the weather, but with this app, next time I move to a new city I'll make sure I have all the info I want from day one :)
