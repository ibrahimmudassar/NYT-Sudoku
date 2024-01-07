from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


nyt_link = 'https://www.nytimes.com/puzzles/sudoku/hard'

soup = BeautifulSoup(requests.get(nyt_link).content, "html.parser")

key = soup.findAll("script", {"type": "text/javascript"})
gameData = ""
for i in key:
    if "window.gameData = " in i.text:
        gameData = i.text.replace("window.gameData = ", "")

gameData = json.loads(gameData)

hard = ('hard', ''.join([str(i)
        for i in gameData['hard']["puzzle_data"]['puzzle']]))
medium = ('medium', ''.join(
    [str(i) for i in gameData['medium']["puzzle_data"]['puzzle']]))
easy = ('easy', ''.join([str(i)
        for i in gameData['easy']["puzzle_data"]['puzzle']]))

final_list = []

# get an image of the hard sudoku of the day
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(nyt_link)

    # Show candidates
    page.locator('.su-keyboard__checkbox').click(button='left')

    # Take a screenshot of a specific element
    element = page.locator('.su-board')
    element.screenshot(path='sudoku.png')

# get the HoDoKu and SE metrics for each of the difficulties
for i, j in [easy, medium, hard]:
    temp = {'string': j}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f'https://sudoku.coach/en/solver/{j}')

        page.wait_for_selector("div:has-text('HoDoKu:')")
        soup = BeautifulSoup(page.content(), 'html.parser')

        browser.close()

    se = soup.find('div', string='SE:')
    se_score = se.find_next('div')
    temp["SE"] = float(se_score.text.replace("~", ''))

    hodoku = soup.find('div', string='HoDoKu:')
    hodoku_score = hodoku.find_next('div')
    temp["HoDoKu"] = int(hodoku_score.text.replace("~", ''))

    temp['difficulty'] = i

    final_list.append(temp)


def embed_to_discord(nyt_link):

    # create embed object for webhook
    embed = DiscordEmbed(title='NYT Sudoku',
                         description='Analysis of NYT Sudoku Today')

    sudokku_coach_hard = "https://sudoku.coach/en/play/" + ''.join([str(i)
                                                                      for i in gameData['hard']['puzzle_data']['puzzle']])
    embed.add_embed_field(
        name="Ways to Play", value=f"[Play on NYT]({nyt_link})\n[Play on SudokuCoach]({sudokku_coach_hard})", inline=False)

    embed.add_embed_field(
        name="Analysis", value=f"Medium\nHoDoKu: {final_list[1]['HoDoKu']}\nSE: {final_list[1]['SE']}\n\nHard\nHoDoKu: {final_list[2]['HoDoKu']}\nSE: {final_list[1]['SE']}", inline=False)

    # set image
    embed.set_image(url='attachment://sudoku.png')

    # set thumbnail
    embed.set_thumbnail(
        url='https://cdn-1.webcatalog.io/catalog/nytimes-sudoku/nytimes-sudoku-icon-filled-256.png?v=1675594774672')

    # set footer
    embed.set_footer(text='Made By Ibrahim Mudassar',
                     icon_url='https://avatars.githubusercontent.com/u/22484328?v=4')

    # add embed object to webhook(s)
    # Webhooks to send to
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)

        with open("sudoku.png", "rb") as f:
            webhook.add_file(file=f.read(), filename='sudoku.png')

        webhook.add_embed(embed)
        webhook.execute()


embed_to_discord(nyt_link)

df = pd.DataFrame(final_list)
df = df.assign(print_date=gameData['hard']["print_date"])
df = df.assign(day_of_week=gameData['hard']["day_of_week"])
