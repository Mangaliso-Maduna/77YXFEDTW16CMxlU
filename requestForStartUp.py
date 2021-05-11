from selenium import webdriver
import csv
from getpass import getpass
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def get_data(card):
    username = card.find_element_by_xpath('.//span').text
    try:
        handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except NoSuchElementException:
        return
    try:
        post_date = WebDriverWait(card, 10).until(EC.presence_of_element_located((By.XPATH, "//time")))
        post_date.get_attribute('datetime')
    except NoSuchElementException:
        return

    # tweet_content
    comment = WebDriverWait(card, 10).until(EC.presence_of_element_located((By.XPATH, "//div[2]/div[2]/div[1]"))).text
    response = WebDriverWait(card, 10).until(EC.presence_of_element_located((By.XPATH, "//div[2]/div[2]/div[2]"))).text
    tweet_content = comment + response

    # reactions
    comments_count = WebDriverWait(card, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@data-testid="reply"]')))
    comments_count.text

    retweets_count = WebDriverWait(card, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweet"]')))
    retweets_count.text

    likes = WebDriverWait(card, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="like"]'))).text

    tweet = (username, handle, post_date, tweet_content, comments_count, retweets_count, likes)
    return tweet


# NAVIGATING AND CLICKING ELEMENTS

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("https://twitter.com/explore")

search_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
    (By.XPATH, '//input[@aria-label="Search query"]')))
search_input.send_keys("request for startup")
search_input.send_keys(Keys.RETURN)

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Latest")))
element.click()

tweet_data = []
tweet_ids = set()
last_position = driver.execute_script("return window.pageYOffset;")
scrolling = True

while scrolling:
    cards = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="tweet"]')))
    for card in cards[-15:]:
        tweet = get_data(card)
        if tweet:
            tweet_id = ' , '.join(map(str, tweet))
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                tweet_data.append(tweet)

    scroll_attempt = 0
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)
        current_position = driver.execute_script("return window.pageYOffset;;")
        # compare last and current position
        if last_position == current_position:
            scroll_attempt = scroll_attempt + 1

            if scroll_attempt >= 3:
                scrolling = False
                break
            else:
                time.sleep(2)
        else:
            last_position = current_position
            break
driver.close()
with open('startup_tweets.csv', 'w', newline='', encoding='utf-8') as f:
    header = ['username', 'handle', 'Timestamp', 'Comments', 'likes', 'retweets', 'Text']
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerow(tweet_data)