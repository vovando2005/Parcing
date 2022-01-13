from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['emailru']
letters_col = db.letters

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://mail.ru/')

elem = driver.find_element(By.NAME, "login")
elem.send_keys('study.ai_172')

elem.send_keys(Keys.ENTER)
driver.implicitly_wait(2)

elem = driver.find_element(By.NAME, "password")
elem.send_keys('NextPassword172#')

elem.send_keys(Keys.ENTER)
time.sleep(3)
letter_link_list = []
while True:
    letters = driver.find_elements(By.XPATH, "//a[contains(@class, 'js-letter-list-item llc_normal')]")
    last_letter = letters[-1]
    actions = ActionChains(driver)
    actions.move_to_element(letters[-1])
    actions.perform()
    letters = driver.find_elements(By.XPATH, "//a[contains(@class, 'js-letter-list-item llc_normal')]")
    if letters[-1] != last_letter:
        for letter in letters:
            letter_link_list.append(letter.get_attribute('href'))
        time.sleep(3)
    else:
        break

letter_link_list_set = set(letter_link_list)

for link in letter_link_list_set:

    letter_data = {}
    driver.get(link)
    driver.implicitly_wait(8)
    from_block = driver.find_element(By.CLASS_NAME, "letter__author")
    from_who = from_block.find_element(By.CLASS_NAME, 'letter-contact').text
    from_email = from_block.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title')
    date = from_block.find_element(By.CLASS_NAME, 'letter__date').text
    topic = driver.find_element(By.TAG_NAME, "h2").text
    all_text = driver.find_element(By.CLASS_NAME, "letter-body__body").text

    letter_data['_id'] = from_who + ' at ' + date
    letter_data['from_who'] = from_who
    letter_data['from_email'] = from_email
    letter_data['date'] = date
    letter_data['topic'] = topic
    letter_data['all_text'] = all_text

    try:
        letters_col.insert_one(letter_data)
    except dke:
        pass

for letter in letters_col.find({}):
    pprint(letter)