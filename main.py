import asyncio
import json
import aiohttp
from understat import Understat

'''
FUNCTIONS:
  - get_stats()
  - get_teams(league_name, season)
  - get_league_players(league_name, season)
  - get_league_results(league_name, season)
  - get_league_fixtures(league_name, season)
  - get_league_table(league_name, season)
  - get_player_shots(player_id)
  - get_player_matches(player_id)
  - get_player_stats(player_id)
  - get_player_grouped_stats(player_id)
  - get_team_stats(team_name, season)
  - get_team_results(team_name, season)
  - get_team_fixtures(team_name, season)
  - get_team_players(team_name, season)
  - get_match_players(match_id)
  - get_match_shots(match_id)
'''


async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        fixtures = await understat.get_match_shots(15473)
        print(json.dumps(fixtures, sort_keys=True, indent=4))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
