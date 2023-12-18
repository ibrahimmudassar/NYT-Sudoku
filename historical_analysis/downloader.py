from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import concurrent.futures
from tqdm import tqdm
import pandas as pd

from requests_html import HTMLSession
session = HTMLSession()

with open("items.txt", "r") as f:
    archived_links = [i.replace("\n", "") for i in f.readlines()]
print(archived_links)

list_of_sudokus = []

def link_to_df(url:str) -> list:
    try:
        soup = BeautifulSoup(session.get(url).content, "html.parser")

        key = soup.findAll("script", {"type": "text/javascript"})
        gameData = ""
        for i in key:
            if "window.gameData = " in i.text:
                gameData = i.text.replace("window.gameData = ", "")

        gameData = json.loads(gameData)

        hard = ('hard',''.join([str(i) for i in gameData['hard']["puzzle_data"]['puzzle']]))
        medium = ('medium',''.join([str(i) for i in gameData['medium']["puzzle_data"]['puzzle']]))
        easy = ('easy',''.join([str(i) for i in gameData['easy']["puzzle_data"]['puzzle']]))


        final_list = []

        for i,j in [easy,medium,hard]:

            briefing_link = f'https://sudoku.coach/en/solver/{j}'
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                page.goto(briefing_link)

                page.wait_for_selector("div:has-text('HoDoKu:')")
                soup = BeautifulSoup(page.content(), 'html.parser')
                browser.close()
            
            temp = {'string':j, 'difficulty':i}

            se = soup.find('div', string='SE:')
            se_score = se.find_next('div')
            temp["SE"] = float(se_score.text.replace("~", ''))

            hodoku = soup.find('div', string='HoDoKu:')
            hodoku_score = hodoku.find_next('div')
            temp["HoDoKu"] = int(hodoku_score.text.replace("~", ''))

            temp['print_date'] = gameData['hard']["print_date"]
            temp['day_of_week'] = gameData['hard']["day_of_week"]

            final_list.append(temp)

        return final_list
    except:
        return []

with concurrent.futures.ThreadPoolExecutor() as executor:

    # Submit the tasks to the executor
    results = [executor.submit(link_to_df, url)
               for url in archived_links]

    # Get the results as they complete
    for future in tqdm(concurrent.futures.as_completed(results), total=len(results)):
        list_of_sudokus += future.result()

df = pd.DataFrame(list_of_sudokus)
df.to_csv('historical_nyt_sudokus.csv')