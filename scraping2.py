from __future__ import annotations

import os
import re
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import constants

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

def get_teams(season: str) -> List[str]:
    driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
    try:
        teams = []
        s_id = constants.season_map[season.upper()]
        driver.get(constants.teams_url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"option[value='{s_id}']"))
        )
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "st_list")))
        select = Select(driver.find_element_by_id('st_list'))
        select.select_by_value(s_id)
        team_div = driver.find_element_by_id('standings_table')
        table_rows = team_div.find_elements_by_xpath('//*[@id="standings_table"]/table/tbody/tr')
        for row in table_rows:
            try:
                td = row.find_element_by_tag_name('td')
                teams.append(td.text)
            except NoSuchElementException:
                pass
        return teams
    finally:
        driver.quit()


def make_season_json(teams: List[str], season: str) -> None:
    driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
    try:
        driver.get(constants.base_url.format(constants.season_map[season.upper()]))
        soup_file = driver.page_source
        soup = BeautifulSoup(soup_file, features='html.parser')
        big_div = soup.find("div", attrs={'class': 'container'})
        divs = big_div.find_all('div', attrs={'class': 'container header'})
        weeks = []
        for div in divs:
            time_info, games = get_time_and_game_infos(div)
            week = constants.WeekInfo(time_info, games)
            weeks.append(week)

        str_for_file = f'{[week.to_json() for week in weeks]}'
        season_path = f"{constants.folder_path}/{season}"
        os.makedirs(season_path, exist_ok=True)
        with open(f'{season_path}/master.json', 'w') as jsonfile:
            jsonfile.write(str_for_file)
        team_dicts = {team: [] for team in teams}
        for week_num, week in enumerate(weeks):
            for team in team_dicts:
                new_dict = {"time_info": week.time_info, "games": []}
                team_dicts[team].append(new_dict)
            for game in week.games:
                team_dicts[game.team1][week_num]['games'].append(game)
                team_dicts[game.team2][week_num]['games'].append(game)
        for team in team_dicts:
            with open(f'{season_path}/{team}.json', 'w') as jsonfile:
                jsonfile.write(f'{[info.to_json() for info in team_dicts[team]]}')
    finally:
        driver.quit()


def get_time_and_game_infos(div: Tag) -> (constants.TimeInfo, list[constants.GameInfo]):
    text = div.text
    pattern = re.compile(r"(?P<week>.*) : (?P<day>\w+) (?P<date>\d+/\d+).*")
    match = pattern.match(text)
    time_info = constants.TimeInfo(*list(match.groups()))
    game_rows = []
    for d in div.next_siblings:
        if 'row' in d.attrs['class']:
            game_rows.append(parse_row(d))
        else:
            break
    return time_info, game_rows


def parse_row(div: Tag) -> constants.GameInfo:
    time, team1, _, team2, court_num = [d.text for d in div.find_all('div')]
    return constants.GameInfo(time, team1, team2, court_num)


if __name__ == '__main__':
    teams_a = get_teams("Coed Wed A")
    # teams_bbb = get_teams("Coed Wed bbb")
    # print(teams_a)
    # print(teams_bbb)
    make_season_json(teams_a, 'Coed Wed A')
