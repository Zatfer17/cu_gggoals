import asyncio
import json
import aiohttp
from understat import Understat
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np

async def getUpsetOfTheWeek():

    print("UPSET OF THE WEEK FUNCTIONALITY")

    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        fixtures = await understat.get_league_results("serie_a", 2021)

        latestGameDate = datetime.strptime(fixtures[-1]['datetime'], "%Y-%m-%d %H:%M:%S")
        olderGameDate = latestGameDate - timedelta(7)

        toKeep = []
        for value in fixtures:
            if datetime.strptime(value['datetime'], "%Y-%m-%d %H:%M:%S") >= olderGameDate:
                toKeep.append(value)

        index = 0
        maxUpset = 0
        id = ""

        for i in range(0, len(toKeep)):
            actualResultDifference = float(toKeep[i]['goals']['h']) - float(toKeep[i]['goals']['a'])
            expectedResultDifference = float(toKeep[i]['xG']['h']) - float(toKeep[i]['xG']['a'])
            upset = abs(abs(actualResultDifference) - abs(expectedResultDifference))
            if np.sign(actualResultDifference) != np.sign(expectedResultDifference) and upset > maxUpset:
                index = i
                maxUpset = upset
                id = toKeep[i]['id']

        print("UPSET OF THE WEEK:")
        print(json.dumps(toKeep[index], indent=4, sort_keys=True))
        print()

        stats = await understat.get_match_shots(id)
        top10_h = sorted(stats['h'], key=lambda x: x['xG'], reverse=True)
        top10_a = sorted(stats['a'], key=lambda x: x['xG'], reverse=True)

        df_h = pd.DataFrame(top10_h)
        df_a = pd.DataFrame(top10_a)

        df_h = df_h[["X", "Y", "xG", "result", "h_team"]]
        df_h[["X", "Y", "xG"]] = df_h[["X", "Y", "xG"]].apply(pd.to_numeric)
        df_h["X"] = 1.0 - df_h["X"]
        df_h.rename(columns={"h_team": "team"}, inplace=True)

        df_a = df_a[["X", "Y", "xG", "result", "a_team"]]
        df_a[["X", "Y", "xG"]] = df_a[["X", "Y", "xG"]].apply(pd.to_numeric)
        df_a.rename(columns={"a_team": "team"}, inplace=True)

        result = pd.concat([df_h, df_a])
        result["xG"] = 2 * result["xG"]

        print("OCCASIONS DATAFRAME")
        print(result)

        fig = px.scatter(result, x="X", y="Y", color="team", size="xG", width=1280, height=877)
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(255, 255, 255, 1)',
            'xaxis.visible': False,
            'yaxis.visible': False
        })
        fig.add_layout_image(
            source="https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Football_pitch_v2.svg/1280px-Football_pitch_v2.svg.png",
            layer="below",
            x=0,
            y=0,
            xanchor="left",
            yanchor="bottom",
            sizex=1,
            sizey=1,
        )
        fig.update_xaxes(range=[0.0, 1.0])
        fig.update_yaxes(range=[0.0, 1.0])

        fig.show()
        home_team = toKeep[index]['h']['short_title']
        away_team = toKeep[index]['a']['short_title']
        date = toKeep[index]['datetime']
        fig.write_image("graphs/" + home_team + "_" + away_team + "_" + date + ".png")

        print()
        print("RESULT STORED")

def routine(functionality):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(functionality)
