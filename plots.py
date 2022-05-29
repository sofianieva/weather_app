import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import ticks_year


def hourly_plots(today_h_df, element, label, extra, color, title, dtick, today_text):
    fig = px.line(
        today_h_df,
        x="time",
        y=element,
        markers=True,
        labels={element: label, "time": ""},
        height=300,
        template="simple_white",
        color_discrete_sequence=[color],
        title=title + ", " + today_text,
    )
    fig.update_traces(hovertemplate="%{y}" + extra + " <br>%{x}")
    fig.update_xaxes(nticks=13, showgrid=True)
    fig.update_yaxes(dtick=dtick, showgrid=True)
    return fig


# This df is just to generate the month ticks automatically in plot_quartiles
def ticks_percentile_plot_df(data, element, leap_year=False):
    df = data[[element, "year"]].copy().reset_index()
    if leap_year:
        df = df[df["year"] == "2016"].drop(columns=["year"])
    else:
        df = df[df["year"] == "2018"].drop(columns=["year"])
    df["date"] = df["date"].apply(lambda x: x[5:])
    # Format needed to plot automatically
    year_plot = ticks_year(leap_year)   
    df["date"] = year_plot + df["date"]
    return df


def quartiles_plots(data, data_group_m, today_df, element, extra, 
                   y_axis_label, color, today, leap_year, title=""):
    months = [
        " Jan.", " Feb.", " Mar.",
        " Apr.", " May", " June",
        " July", " Aug.", " Sep.",
        " Oct.", " Nov.", " Dec."
    ]
    df_plot = ticks_percentile_plot_df(data, element, leap_year)
    year_plot = ticks_year(leap_year)
    today_df_plot = today_df.copy()
    today_df_plot["date_plot"] = year_plot + str(today_df.index[0])[5:]
    today_df_plot["day_month"] = today.strftime("%d %b") + "."
    
    fig = px.line(
        df_plot,
        x="date",
        y=element,
        labels={element: y_axis_label, "date": ""},
        height=300,
        template="simple_white",
        color_discrete_sequence=["rgba(0,0,0,0)"],
        title=title,
    )
    fig.update_traces(hovertemplate=None, hoverinfo="skip")
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period", showgrid=True)
    fig.update_yaxes(showgrid=True)

    fig.add_trace(
        go.Scatter(
            x=data_group_m.reset_index()["month"]
            .apply(lambda x: year_plot + x + "-15")
            .values,
            y=data_group_m[(element, "q25")].values,
            fill=None,
            mode="lines",
            line_color=color,
            showlegend=False,
            hovertemplate="%{text} %{customdata} <br>%{y}" + extra + "<extra></extra>",
            text=["Q1"] * 12,
            customdata=months,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data_group_m.reset_index()["month"]
            .apply(lambda x: year_plot + x + "-15")
            .values,
            y=data_group_m[(element, "q75")].values,
            fill="tonexty",  # fill area between trace0 and trace1
            mode="lines",
            line_color=color,
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data_group_m.reset_index()["month"]
            .apply(lambda x: year_plot + x + "-15")
            .values,
            y=data_group_m[(element, "q75")].values,
            mode="lines",
            line_color=color,
            showlegend=False,
            hovertemplate="%{text} %{customdata} <br>%{y}" + extra + "<extra></extra>",
            text=["Q3"] * 12,
            customdata=months,
        )
    )
    fig.add_traces(
        px.scatter(
            today_df_plot,
            x="date_plot",
            y=element,
        )
        .update_traces(
            marker_size=10,
            marker_color=color,
            hovertemplate="<br>%{text} <br>%{y}" + extra,
            text=today_df_plot["day_month"],
        )
        .data
    )
    fig.add_annotation(
        x=today_df_plot["date_plot"].values[0],
        y=today_df_plot[element].values[0],
        text="Today",
        showarrow=True,
        arrowhead=5,
        arrowwidth=1,
        yshift=5,
        xshift=-1,
    )
    return fig


def season_wind_rose(data, colors, season):
    temp = data[["season", "wdirn", "wspd"]].copy()
    temp["wdir_bin"] = pd.cut(
        temp["wdirn"],
        bins=[
            0, 11.25, 33.75,
            56.25, 78.75, 101.25,
            123.75, 146.25, 168.75,
            191.25, 213.75, 236.25,
            258.75, 281.25, 303.75,
            326.25, 348.75, 360.00,
        ],
        labels=[
            "North", "NNE", "NE",
            "ENE", "East", "ESE",
            "SE", "SSE", "South",
            "SSW", "SW", "WSW",
            "West", "WNW", "NW",
            "NNW", "NN",
        ],
    )

    temp["wspd_bin"] = pd.cut(
        temp["wspd"],
        bins=[1.5, 5, 10, 15, 20, 30, 50],
        labels=[
            "1.5-5 km/h", "5-10 km/h",
            "10-15 km/h",  "15-20 km/h",
            "20-30 km/h", "30+ km/h",
        ],
    )
    temp.replace({"NN": "North"}, inplace=True)
    temp.reset_index(inplace=True)

    windfreq_group = (
        temp[["date", "season", "wdir_bin", "wspd_bin"]]
        .groupby(["season", "wdir_bin", "wspd_bin"])
        .count()
    )
    windfreq_group.rename(columns={"date": "Frequency"}, inplace=True)
    windfreq_group.reset_index(inplace=True)
    windfreq_group.rename(
        columns={"wdir_bin": "Direction", "wspd_bin": "Speed"}, inplace=True
    )
    season_df = windfreq_group[windfreq_group.season == season][
        ["Direction", "Speed", "Frequency"]
    ]
    total_days = season_df.Frequency.sum()
    fig = px.bar_polar(
        season_df,
        r="Frequency",
        theta="Direction",
        color="Speed",
        template="simple_white",
        color_discrete_sequence=colors,
        title="Distribution of speed and direction of wind in the last 5 "
        + season
        + "s",
    )
    fig.update_polars(angularaxis_showgrid=True, radialaxis_showgrid=True)
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        modebar={
            "bgcolor": "rgba(0, 0, 0, 0)",
            "color": "LightGray",
            "activecolor": "Gray",
        },
        xaxis_title=None,
        margin=dict(l=40, r=0, t=70, b=20),
    )
    return season_df, fig


def sun_plot(today_sun_df, sun_2022, element, hover, title, colors, n, a1, a2):
    fig = px.line(
        sun_2022,
        x="date",
        y=element,
        labels={element: "Hour of the day", "date": ""},
        height=300,
        template="simple_white",
        color_discrete_sequence=[colors[n]],
        custom_data=[hover],
        title=title,
    )
    fig.update_traces(
        hovertemplate="%{text} <br>%{customdata}", text=sun_2022["day_month"]
    )
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period", showgrid=True)
    fig.update_yaxes(
        tickvals=[60 * (x) for x in range(24)],
        ticktext=[str(x).zfill(2) + ":00" for x in range(24)],
        showgrid=True,
        autorange="reversed",
    )
    fig.add_traces(
        px.scatter(today_sun_df, x="date", y=element, custom_data=[hover])
        .update_traces(
            marker_size=10,
            marker_color=colors[n],
            hovertemplate="<br>%{text} <br>%{customdata}",
            text=today_sun_df["day_month"],
        )
        .data
    )
    fig.add_annotation(
        x=today_sun_df["date"].values[0],
        y=today_sun_df[element].values[0],
        text="Today",
        showarrow=True,
        arrowhead=5,
        arrowwidth=1,
        yshift=5,
        xshift=-1,
    )

    fig.add_annotation(
        x=today_sun_df["date"].values[0][:4] + "-03-27",
        y=a1,
        text="Start Daylight<br>Saving Time",
        showarrow=True,
        arrowhead=5,
        arrowwidth=1,
        yshift=5,
        xshift=-1,
    )

    fig.add_annotation(
        x=today_sun_df["date"].values[0][:4] + "-10-30",
        y=a2,
        text="End Daylight<br>Saving Time",
        showarrow=True,
        arrowhead=5,
        arrowwidth=1,
        yshift=5,
        xshift=0,
    )
    return fig


def day_length_plot(sun_2022, color, today_sun_df):
    fig = px.line(
        sun_2022,
        x="date",
        y="durationday",
        labels={"durationday": "Length of the Day (h)", "date": ""},
        height=300,
        template="simple_white",
        color_discrete_sequence=[color],
        custom_data=["durationday_h", "durationday_m"],
        title="Length of the day during the year and today",
    )
    fig.update_traces(
        hovertemplate="%{text} <br>%{customdata[0]} %{customdata[1]} <br>of daytime",
        text=sun_2022["day_month"],
    )
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period", showgrid=True)
    fig.update_yaxes(
        tickvals=[120 * (x) for x in range(12)],
        ticktext=[str(2 * x) for x in range(12)],
        showgrid=True,
    )
    fig.add_traces(
        px.scatter(
            today_sun_df,
            x="date",
            y="durationday",
            custom_data=["durationday_h", "durationday_m"],
        )
        .update_traces(
            marker_size=10,
            marker_color=color,
            hovertemplate="<br>%{text} <br>%{customdata[0]} %{customdata[1]} <br>of daytime",
            text=today_sun_df["day_month"],
        )
        .data
    )
    fig.add_annotation(
        x=today_sun_df["date"].values[0],
        y=today_sun_df["durationday"].values[0],
        text="Today",
        showarrow=True,
        arrowhead=5,
        arrowwidth=1,
        yshift=5,
        xshift=-1,
    )
    return fig


# There is an issue with plotly templates and streamlit, so I have to update the figures background colors
def update_fig(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        modebar={
            "bgcolor": "rgba(0, 0, 0, 0)",
            "color": "LightGray",
            "activecolor": "Gray",
        },
        xaxis_title=None,
        margin=dict(l=70, r=0, t=40, b=40),
    )