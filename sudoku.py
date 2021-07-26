from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables
from selenium import webdriver  # Browser prereq
from selenium.common.exceptions import NoSuchElementException

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


# Create new Instance of Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = env("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")


def embed_to_discord():
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook
    embed = DiscordEmbed(title='yo', description='yo',
                         color='000000')

    with open("yo.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='yo.png')

    embed.set_image(url='attachment://yo.png')

    # add embed object to webhook(s)
    webhook.add_embed(embed)
    webhook.execute()


def get_import_code():
    import_code = ""  # will use this to import and standardize puzzle
    for i in range(1, 82):
        try:
            # gets the number and appends it if exists
            cell = browser.find_element_by_css_selector(
                "#pz-game-root > div.su-app > div > div.su-app__play > div > div > div > div:nth-child(" + str(i) + ") > svg").get_attribute('number')
            import_code += str(cell)
        except NoSuchElementException:
            import_code += "."

    return import_code


def take_screenshot():
    full_grid = browser.find_element_by_xpath(
        '//*[@id="pz-game-root"]/div[2]/div/div[1]/div/div')
    top_toolbar = browser.find_element_by_xpath(
        '//*[@id="js-hook-pz-moment__game"]/div[1]')  # this is just to crop it properly

    browser.execute_script("arguments[0].scrollIntoView();", top_toolbar)
    full_grid.screenshot('yo.png')


browser = webdriver.Chrome(executable_path=env(
    'CHROMEDRIVER_PATH'), options=chrome_options)

browser.get("https://www.nytimes.com/puzzles/sudoku/hard")


get_import_code()
embed_to_discord('yo.png')

browser.quit()
