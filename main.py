import requests
import selenium
import time
import traceback
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pymongo

DB_NAME = "vk_liker"
DB_COLLECTION = "liked"
MONGO_CLIENT_URL = "mongodb://localhost:27017/"

mongo_client = pymongo.MongoClient(MONGO_CLIENT_URL)
mongo_db = mongo_client[DB_NAME]

# krasnodar 72, for example

CITY_CODE = 72
CHROME_PROFILE = "/Users/user/Library/Application Support/Google/Chrome/Profile 1"
CHROME_DRIVER = "/Users/user/Downloads/chromedriver_2_2"
API_TOKEN ="your token"

while True:
    ch_options = Options()
    ch_options.add_argument(
        "user-data-dir={}".format(CHROME_PROFILE))
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=ch_options)

    try:
        vk_url = "https://api.vk.com/method/users.search?count=1000&&city={CITY_CODE}&country=1&status=1&can_access_closed=1&sex=1&online=1&has_photo=1&age_from=18&age_to=28&access_token={API_TOKEN}&v=5.89"
        .format(CITY_CODE=CITY_CODE, API_TOKEN=API_TOKEN)
        vk_response = requests.get(vk_url).json()

        for item in vk_response["response"]["items"]:
            if item["can_access_closed"]:
                user_url = "https://vk.com/id{}".format(item["id"])

                if mongo_db[DB_COLLECTION].count_documents({
                    '_id': int(item["id"])
                }, limit=1) == 0:
                    driver.get(user_url)
                    avatar_elem = driver.find_element_by_class_name("page_avatar_img")
                    avatar_elem.click()
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "like_btn.like._like")))
                    try:
                        # it is already liked if there is no exception
                        driver.find_element_by_class_name("like_btn.like._like.active")
                        mongo_db[DB_COLLECTION].insert_one({
                            "_id": int(item["id"])
                        })
                    except selenium.common.exceptions.NoSuchElementException:
                        # we haven't liked it, like it now
                        time.sleep(5)
                        like_button = driver.find_element_by_class_name("like_btn.like._like")
                        like_button.click()

                        mongo_db[DB_COLLECTION].insert_one({
                            "_id": int(item["id"])
                        })
                    time.sleep(30)
                else:
                    print("skip: {}".format(user_url))
    finally:
        driver.close()

    time.sleep(60 * 30)
