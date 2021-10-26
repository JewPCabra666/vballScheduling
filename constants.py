from dataclasses import dataclass

from dataclasses_json import dataclass_json

season_map = {
    "Coed Wed A": 420,
    "Coed Wed BBB": 494,
    "Coed Wed BB": 430,
    "Coed Wed B": 440,
    "Senior Masters Division": 498,
    "Coed Wed C": 460,
    "Coed Thu BB": 432,
    "Coed Thu BBB": 495,
    "Coed Thu B": 442,
    "Coed Thu C": 462,
    "Coed Fri BB": 434,
    "Coed Fri B": 444,
    "Masters": 491,
    "Men's Mon A": 256,
    "Men's Tue A": 257,
    "Men's Mon BBB": 262,
    "Men's Tue BB": 259,
    "Women's Mon Open": 305,
    "Women's Sun AA": 353,
    "Women's Tue AA": 354,
    "Women's Tue A": 355,
    "Women's Mon BB": 330,
}
season_map = {k.upper(): str(v) for k, v in season_map.items()}
season_id = str(166)
folder_path = f"seasons/{season_id}"
base_url = 'https://rvc.net/adult-volleyball-programs/adult-indoor-leagues/schedules/?division_id={}&season_id=' + season_id
teams_url = 'https://rvc.net/adult-volleyball-programs/adult-indoor-leagues/standings/'


@dataclass_json
@dataclass
class TimeInfo:
    week: str
    day: str
    date: str


@dataclass_json
@dataclass
class GameInfo:
    time: str
    team1: str
    team2: str
    court: str

    def has_team(self, team) -> bool:
        return self.team1 == team or self.team2 == team


@dataclass_json
@dataclass
class WeekInfo:
    time_info: TimeInfo
    games: list[GameInfo]
