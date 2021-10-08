from bs4 import BeautifulSoup
import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import re
from collections import namedtuple
from time import sleep
from typing import Any, Dict
from datetime import datetime
from pprint import pprint

# Instantiate an Options object
# and add the "--headless" argument
opts = Options()
# opts.add_argument(" --headless")
# If necessary set the path to you browser’s location
# opts.binary_location = os.getcwd() + '\\GoogleChromePortable\GoogleChromePortable.exe'
# Set the location of the webdriver
chrome_driver = os.getcwd() + "\\chromedriver.exe"
# Instantiate a webdriver
# Load the HTML page

RowInfo = namedtuple('RowInfo', 'week day date')
Row = namedtuple('Row', 'time team1 team2 court')
Week = namedtuple('Week', 'info games')

Schedule = list[Week]


def prints(x: Any) -> None:
    print(*x, sep='\n')


year = 2021
season_id = 166
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
season_map = {k.upper(): v for k, v in season_map.items()}
base_url = 'https://rvc.net/adult-volleyball-programs/adult-indoor-leagues/schedules/?division_id={}&season_id={}'


def get_schedule(season: str, team_name: str) -> Schedule:
    driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
    try:
        url = base_url.format(season_map[season], season_id)
        driver.get(url)
        soup_file = driver.page_source
        soup = BeautifulSoup(soup_file, features="html.parser")

        big_div = soup.find("div", attrs={'class': 'container'})
        season_info = [get_week_info(div) for div in big_div.find_all('div', attrs={'class': 'container header'})]
        # print(*season_info, sep='\n')
        schedule = get_schedule_for_team(team_name, season_info)
        # print(*schedule, sep='\n')
        driver.quit()
        return schedule
    except Exception as e:
        print(e)
        driver.quit()


def get_schedules(season: str, teams: list[str]) -> list[Schedule]:
    schedules = []
    for i, team in enumerate(teams):
        schedule = get_schedule(season, team)
        schedules.append(schedule)
        if i < len(teams) - 1:
            sleep(5)
    return schedules


def get_schedule_for_team(team_name: str, season_info: list[(RowInfo, list[Row])]) -> list[Week]:
    team_schedule = []
    for info, rows in season_info:
        week = Week(info, [])
        for row in rows:
            if row.team1 == team_name or row.team2 == team_name:
                week.games.append(row)
        team_schedule.append(week)

    return team_schedule


def get_week_info(div: bs4.element.Tag) -> (RowInfo, list[Row]):
    text = div.text
    pattern = re.compile(r"(?P<week>.*) : (?P<day>\w+) (?P<date>\d+/\d+).*")
    match = pattern.match(text)
    row_info = RowInfo(*list(match.groups()))
    rows = []
    for d in div.next_siblings:
        if 'row' in d.attrs['class']:
            rows.append(parse_row(d))
        else:
            break
    return row_info, rows


def parse_row(div: bs4.element.Tag) -> Row:
    time, team1, _, team2, court_num = [d.text for d in div.find_all('div')]
    return Row(time, team1, team2, court_num)


def create_calendar_events(team: str, week: Week, attendees: list[str]) -> list[Dict]:
    info, games = week
    summary_base = f'VBALL - {team.upper()} - {info.week} - COURT '
    # for game in games:
    #     transformed = [f'{info.week}', f'{"-" * 10}'] + [transform_game(game)]
    #     description = "\n".join(transformed)
    #     start, end = get_start_and_end(info.date, game)
    #     create_event(summary_base + , description, start, end, attendees)

    summary1 = summary_base + f'{games[0].court}'
    summary2 = summary_base + f'{games[1].court}'

    game1 = [f'{games[0].time} ON <b>COURT {games[0].court}</b>', f'{"-" * 9}'] + [transform_game(games[0])]
    game2 = [f'{games[1].time} ON <b>COURT {games[1].court}</b>', f'{"-" * 9}'] + [transform_game(games[1])]

    description1 = "\n".join(game1)
    description2 = "\n".join(game2)

    s1, e1 = get_start_and_end(info.date, games[0])
    s2, e2 = get_start_and_end(info.date, games[1])

    event1 = create_event(summary1, description1, s1, e1, attendees)
    event2 = create_event(summary2, description2, s2, e2, attendees)

    return [event1, event2]


def create_event(summary: str, description: str, start: str, end: str, attendees: list[str]) -> Dict:
    invitees = [{"email": attendee} for attendee in attendees]
    event = {
        'summary': summary,
        'location': '2921 Byrdhill Rd, Richmond, VA 23228',
        'description': description,
        'start': {
            'dateTime': start,
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'America/New_York',
        },
        'attendees': invitees,
        'reminders': {
            'useDefault': 'false',
            'overrides': [
                {'method': 'popup', 'minutes': 600},
            ],
        },
    }
    return event


def transform_game(row: Row) -> str:
    return f'{row.team1.upper()}\nVS\n{row.team2.upper()}'


def get_start_and_end(date: str, game: Row) -> list[str]:
    month, day = [int(x) for x in date.split('/')]
    hour, minute = [int(x) for x in game.time.split(' ')[0].split(":")]
    start = 'T'.join(str(datetime(year, month, day, hour + 12, minute)).split(' '))
    end = 'T'.join(str(datetime(year, month, day, hour + 13, minute)).split(' '))
    return [start, end]


if __name__ == '__main__':
    s = "MEN'S TUE A"
    t = "Bomb Squad"
    sch = get_schedule(s, t)
    week1 = sch[0]
    g1, g2 = create_calendar_events(t, week1, ["pwnergod411@gmail.com"])

    pprint(g1, sort_dicts=False)
    pprint(g2, sort_dicts=False)
# datetime
