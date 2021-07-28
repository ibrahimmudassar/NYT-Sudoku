from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables
from selenium import webdriver  # Browser prereq
from selenium.common.exceptions import NoSuchElementException
import sudoku_solve

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


# Create new Instance of Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")


def embed_to_discord(image_as_binary):
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook
    embed = DiscordEmbed(title='yo', description='yo',
                         color='000000')

    with open("yo.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='yo.png')

    embed.set_image(url=image_as_binary)

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
    return full_grid.screenshot_as_png


browser = webdriver.Chrome(executable_path=env(
    'CHROMEDRIVER_PATH'), options=chrome_options)

browser.get("https://www.nytimes.com/puzzles/sudoku/hard")

print(sudoku_solve.solveWrapper(sudoku_solve.sudoku_string_to_list(
    get_import_code())))  # find the code, convert it, and then solve the grid
# embed_to_discord(take_screenshot()) #take a screenshot of the grid partially solved


browser.quit()
