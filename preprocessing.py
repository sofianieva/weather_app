import pandas as pd
import numpy as np
from utils import wdir_bin, season, ticks_year, hour, minute


def today_hourly_prepocessing(response_ms_dict):
    today_h_df = pd.DataFrame(response_ms_dict["data"])
    today_h_df.drop(columns=["dwpt", "prcp", "snow", "wpgt", "pres", "tsun", "coco"], inplace=True)
    today_h_df["wdir"] = today_h_df["wdir"].apply(wdir_bin)
    today_h_df["time"] = today_h_df["time"].apply(lambda x: x.split(" ")[1][:5])
    return today_h_df

def today_daily_prepocessing(response_vc_dict, today_h_df):
    today_df = pd.DataFrame(response_vc_dict["days"])
    today_df.rename(columns={"datetime": "date"}, inplace=True)
    hours = (
        pd.to_datetime(today_df["sunset"]) - pd.to_datetime(today_df["sunrise"])
    ).apply(lambda x: x.components.hours)
    minutes = (
        pd.to_datetime(today_df["sunset"]) - pd.to_datetime(today_df["sunrise"])
    ).apply(lambda x: x.components.minutes)
    today_df["durationday"] = hours * 60 + minutes
    today_df["year"] = today_df["date"].apply(lambda x: x.split("-")[0])
    today_df["month"] = today_df["date"].apply(lambda x: x.split("-")[1])
    today_df["day"] = today_df["date"].apply(lambda x: x.split("-")[2])
    today_df["tavg"] = round(today_h_df["temp"].mean(), 1)
    today_df["tmin"] = today_h_df["temp"].min()
    today_df["tmax"] = today_h_df["temp"].max()
    today_df["wdir"] = today_h_df["wdir"].mode()
    today_df["wspd"] = round(today_h_df["wspd"].mean(), 1)
    today_df["season"] = pd.to_datetime(today_df["date"]).apply(season)
    today_df.set_index("date", inplace=True)
    return today_df

def sun_preprocessing(sun_2022):
    sun_2022["year"] = sun_2022["Date"].apply(lambda x: x.split("-")[0])
    sun_2022["month"] = sun_2022["Date"].apply(lambda x: x.split("-")[1])
    sun_2022["day"] = sun_2022["Date"].apply(lambda x: x.split("-")[2])
    sun_2022["sunrise"] = sun_2022["Sunrise"].apply(
        lambda x: (x.split(":")[0]).zfill(2) + ":" + x.split(":")[1]
    )
    sun_2022["sunset"] = sun_2022["Sunset"].apply(
        lambda x: (x.split(":")[0]).zfill(2) + ":" + x.split(":")[1]
    )
    sun_2022["durationday"] = sun_2022["Day length"].apply(
        lambda x: (x.split(":")[0]).zfill(2) + ":" + x.split(":")[1]
    )
    sun_2022.rename(columns={"Date": "date"}, inplace=True)
    sun_2022.drop(columns=["Sunrise", "Sunset", "Day length"], inplace=True)
    return sun_2022


# Month abbreviations for UK
month_dict = {
                "01": " Jan.", "02": " Feb.",
                "03": " Mar.", "04": " Apr.",
                "05": " May", "06": " June",
                "07": " July", "08": " Aug.",
                "09": " Sep.", "10": " Oct.",
                "11": " Nov.", "12": " Dec.",
            }


def format_sun_plot(df, leap_year=False, month_dict=month_dict):
    df["date"] = df["date"].apply(lambda x: x[5:])
    df.replace({"month": month_dict}, inplace=True)
    df["day_month"] = df["day"] + df["month"]
    # Format needed to plot automatically
    year = ticks_year(leap_year)
    df["date"] = year + df["date"]
    df["sunrise_hover"] = df["sunrise"].apply(lambda x: x[:5])
    df["sunset_hover"] = df["sunset"].apply(lambda x: x[:5])
    df["sunrise_min"] = df["sunrise_hover"].apply(
        lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1])
    )
    df["sunset_min"] = df["sunset_hover"].apply(
        lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1])
    )
    df["durationday"] = df["durationday"].apply(
        lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1])
    )
    df["durationday_h"] = df["durationday"].apply(hour) + " h"
    df["durationday_m"] = df["durationday"].apply(minute) + " m"
    df.drop(columns=["year", "month", "day", "sunrise", "sunset"], inplace=True)
    return df


def format_daytime_plot(df, leap_year=False, month_dict=month_dict):
    df["date"] = df["date"].apply(lambda x: x[5:])
    df.replace({"month": month_dict}, inplace=True)
    df["day_month"] = df["day"] + df["month"]
    df.drop(columns=["year", "month", "day"], inplace=True)
    # Format needed to plot automatically
    year = ticks_year(leap_year)
    df["date"] = year + df["date"]
    df["durationday_h"] = df["durationday"].apply(hour) + " h"
    df["durationday_m"] = df["durationday"].apply(minute) + " m"
    return df

    
def monthly_agg(data):
    temp = data.copy()
    temp.drop(columns=["sunrise", "sunset", "season"], inplace=True)
    data_group_m = temp.groupby(["month"]).agg(
        {
            "tavg": [
                lambda x: np.percentile(x, 25),
                "mean",
                lambda x: np.percentile(x, 75),
            ],
            "tmin": [
                min, 
                lambda x: np.percentile(x, 25), 
                lambda x: np.percentile(x, 75)
            ],
            "tmax": [
                max, 
                lambda x: np.percentile(x, 25), 
                lambda x: np.percentile(x, 75)
            ],
            "wspd": [
                lambda x: np.percentile(x, 25),
                "mean",
                lambda x: np.percentile(x, 75),
            ],
            "humidity": [
                min,
                max,
                lambda x: np.percentile(x, 25),
                "mean",
                lambda x: np.percentile(x, 75),
            ],
            "uvindex": [
                lambda x: np.percentile(x, 25),
                "mean",
                lambda x: np.percentile(x, 75),
            ],
        }
    )
    data_group_m = data_group_m.round(1)
    for col in data_group_m.columns:
        if col[1] == "<lambda_0>":
            data_group_m.rename(columns={col[1]: "q25"}, level=1, inplace=True)
        elif col[1] == "<lambda_1>":
            data_group_m.rename(columns={col[1]: "q75"}, level=1, inplace=True)
    return data_group_m
        

def seasonly_agg(data):
    temp = data.copy()
    temp.drop(columns=["sunrise", "sunset", "year", "month", "day"], inplace=True)
    data_group_s = temp.groupby(["season"]).agg(
        {"wspd": ["mean"], 
        "humidity": ["mean"], 
        "uvindex": ["mean"]}
    )
    data_group_s = data_group_s.round(1)
    return data_group_s


def common_directions(today_h_df, today, season_df):
    directions = list(today_h_df[['time','wdir']].groupby('wdir').count().nlargest(3, 'time').index)
    main_dir = directions[0]
    directions.sort()
    if season(today)=='spring':
        n_dir = 6
    elif season(today)=='fall':
        n_dir = 5
    else:
        n_dir = 4
    common = list(season_df[['Direction', 'Frequency']].groupby('Direction').sum().nlargest(n_dir,'Frequency').index)
    common.sort()
    i = int(np.ceil(n_dir/2))
    return directions, main_dir, common, i