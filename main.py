import json

import pandas as pd
import requests
from atproto import Client, client_utils
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env
from playwright.sync_api import sync_playwright

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


nyt_link = "https://www.nytimes.com/puzzles/sudoku/hard"

soup = BeautifulSoup(requests.get(nyt_link).content, "html.parser")

key = soup.findAll("script", {"type": "text/javascript"})
gameData = ""
for i in key:
    if "window.gameData = " in i.text:
        gameData = i.text.replace("window.gameData = ", "")

gameData = json.loads(gameData)

hard = ("hard", "".join([str(i) for i in gameData["hard"]["puzzle_data"]["puzzle"]]))
medium = (
    "medium",
    "".join([str(i) for i in gameData["medium"]["puzzle_data"]["puzzle"]]),
)
easy = ("easy", "".join([str(i) for i in gameData["easy"]["puzzle_data"]["puzzle"]]))

final_list = []

# get an image of the hard sudoku of the day
with sync_playwright() as playwright:
    for i, j in [easy, medium, hard]:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"https://www.nytimes.com/puzzles/sudoku/{i}")

        # Show candidates
        page.locator(
            "#portal-modal-system > div > div > div.xwd__modal--body.dark-mode-body.animate-opening.animate-opening-slide-up > article > button"
        ).click(button="left")
        # page.locator(".fam-close-x").click(button="left")
        page.locator(".su-keyboard__checkbox").click(button="left")

        # Take a screenshot of a specific element
        element = page.locator(".su-board")
        element.screenshot(path=f"sudoku_{i}.png")

# get the HoDoKu and SE metrics for each of the difficulties
for i, j in [easy, medium, hard]:
    temp = {"string": j}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        # print(f"https://sudoku.coach/en/solver/{j}")
        page.goto(f"https://sudoku.coach/en/solver/{j}")

        # page.wait_for_selector("div:has-text('Summary Mode')")
        page.wait_for_load_state("networkidle")
        soup = BeautifulSoup(page.content(), "html.parser")

        browser.close()

    se = soup.find("div", string="SE:")
    se_score = se.find_next("div")
    try:
        temp["SE"] = float(se_score.text.replace("~", ""))
    except ValueError:
        temp["SE"] = ""

    hodoku = soup.find("div", string="HoDoKu:")
    hodoku_score = hodoku.find_next("div")
    try:
        temp["HoDoKu"] = int(hodoku_score.text.replace("~", ""))
    except ValueError:
        print(hodoku_score.text)
        temp["HoDoKu"] = ""

    temp["difficulty"] = i

    final_list.append(temp)


def embed_to_discord(nyt_link):

    # create embed object for webhook
    embed = DiscordEmbed(title="NYT Sudoku", description="Analysis of NYT Sudoku Today")

    sudokku_coach_hard = "https://sudoku.coach/en/play/" + "".join(
        [str(i) for i in gameData["hard"]["puzzle_data"]["puzzle"]]
    )
    embed.add_embed_field(
        name="Ways to Play",
        value=f"[Play on NYT]({nyt_link})\n[Play on SudokuCoach]({sudokku_coach_hard})",
        inline=False,
    )

    embed.add_embed_field(
        name="Analysis",
        value=f"Medium\nHoDoKu: {final_list[1]['HoDoKu']}\nSE: {final_list[1]['SE']}\n\nHard\nHoDoKu: {final_list[2]['HoDoKu']}\nSE: {final_list[1]['SE']}",
        inline=False,
    )

    # set image
    embed.set_image(url="attachment://sudoku.png")

    # set thumbnail
    embed.set_thumbnail(
        url="https://cdn-1.webcatalog.io/catalog/nytimes-sudoku/nytimes-sudoku-icon-filled-256.png?v=1675594774672"
    )

    # set footer
    embed.set_footer(
        text="Made By Ibrahim Mudassar",
        icon_url="https://avatars.githubusercontent.com/u/22484328?v=4",
    )

    # add embed object to webhook(s)
    # Webhooks to send to
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)

        with open("sudoku_hard.png", "rb") as f:
            webhook.add_file(file=f.read(), filename="sudoku.png")

        webhook.add_embed(embed)
        webhook.execute()


embed_to_discord(nyt_link)

df = pd.DataFrame(final_list)
df = df.assign(print_date=gameData["hard"]["print_date"])
df = df.assign(day_of_week=gameData["hard"]["day_of_week"])
df["print_date"] = pd.to_datetime(df["print_date"])

client = Client()
profile = client.login(str(env("BSKY_HANDLE")), str(env("BSKY_PASSWORD")))
# print("Welcome,", profile.display_name)
# print(df.to_string(max_colwidth=20))
for d in df.to_dict(orient="records"):
    date = d["print_date"].strftime("%m/%d/%Y")
    text = (
        client_utils.TextBuilder()
        .text(f"{date} NYT Sudoku {d['difficulty'].title()} Analysis\n")
        .text("\nDifficulty Score")
        .text(f"\nHoDoKu: {d['HoDoKu']}")
        .text(f"\nSukakuExplainer: {d['SE']}\n")
        .link(
            "\nNYT Website", f"https://www.nytimes.com/puzzles/sudoku/{d['difficulty']}"
        )
        .link("\nSudokuCoach", f"https://sudoku.coach/en/solver/{d['string']}")
    )

    with open(f"sudoku_{d['difficulty']}.png", "rb") as f:
        img_data = f.read()
    post = client.send_image(
        text,
        image=img_data,
        image_alt=f"{d['difficulty'].title()} sudoku screenshot with candidates",
    )
    )
