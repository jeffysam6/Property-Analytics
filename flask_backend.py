from flask import Flask, request, jsonify
import json
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
from tabulate import tabulate
from time import sleep
import requests

from flask_cors import CORS, cross_origin


app = Flask(__name__)


cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/api')
def single_page(label=None):

    url = "https://www.99acres.com/"
    option = webdriver.ChromeOptions()
    # option.add_argument("--window-size=1920,1080")
    # option.add_argument("--disable-extensions")
    # option.add_argument("--proxy-server='direct://'")
    # option.add_argument("--proxy-bypass-list=*")
    # option.add_argument("--start-maximized")
    # option.add_argument("--headless")
    # option.add_argument("--disable-gpu")
    # option.add_argument("--disable-dev-shm-usage")
    # option.add_argument("--no-sandbox")
    # option.add_argument("--ignore-certificate-errors")
    # option.add_argument("--incognito")

    option.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'")

   
    location = request.args.get('location')

    try:
        f = open(f"{location}_location.json", encoding='utf-8', errors='ignore')
        print(location)
        data = json.load(f)
        return jsonify(data)

    except FileNotFoundError:
        driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)        
        driver.implicitly_wait(50)
        driver.get(url)
        search =  driver.find_element_by_id('keyword')
        search.send_keys(location)
        submit = driver.find_element_by_id('submit_query')
        submit.click()
        sleep(10)
        driver.implicitly_wait(50)
        post_list = driver.find_elements_by_xpath("//div[@class='pageComponent srpTop__tuplesWrap']/div[@class='pageComponent srpTuple__srpTupleBox srp']")
        print(post_list)

        extracted_records = []

        for i in post_list:

            try:
                record = {
                'total_price' : i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:],
                'cost_square' : i.find_element_by_id('srp_tuple_price').text.split('\n')[1][2:],
                'square' : i.find_element_by_id('srp_tuple_primary_area').text.split('\n')[0],
                'bedroom' : i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[0],
                'bathroom' : i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[1],
                'post_link' : i.find_element_by_id('srp_tuple_property_title').get_attribute('href'),
                'location' : i.find_element_by_id('srp_tuple_property_title').text.split("in")[-1]
                }

                if(i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:].split(" ")[-1] == "Cr"):
                    record['total_price'] = str(int(i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:].split(" ")[0]) * 100) + " Lac"

                extracted_records.append(record)
        
            except:
                print("Missing values")


        driver.implicitly_wait(30)
        driver.close()

        with open(f"{location}_location.json", 'w', encoding='utf-8', errors='ignore') as f:

            json.dump(extracted_records, f, ensure_ascii=False, indent=4)

        # return extracted_records
        return jsonify(extracted_records)


@app.route('/api/multiple')
def multiple_page(label=None):

    url = "https://www.99acres.com/"
    option = webdriver.ChromeOptions()

    option.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'")

   
    location = request.args.get('location')

    try:
        f = open(f"{location}_location.json", encoding='utf-8', errors='ignore')
        print(location)
        data = json.load(f)
        return jsonify(data)

    except FileNotFoundError:

        def adding_post(post_list):
            for i in post_list:

                try:
                    record = {
                    'total_price' : i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:],
                    'cost_square' : i.find_element_by_id('srp_tuple_price').text.split('\n')[1][2:],
                    'square' : i.find_element_by_id('srp_tuple_primary_area').text.split('\n')[0],
                    'bedroom' : i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[0],
                    'bathroom' : i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[1],
                    'post_link' : i.find_element_by_id('srp_tuple_property_title').get_attribute('href'),
                    'location' : i.find_element_by_id('srp_tuple_property_title').text.split("in")[-1]
                    }

                    if('-' in i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:]):
                        price = i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:].split(" ")[0]

                        if(i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:].split(" ")[-1] == "Cr"):
                            price = str(float(price) * 100) + " Lac"

                        else:
                            price = price + " Lac"

                        record['total_price'] = price

                    elif(i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:].split(" ")[-1] == "Cr"):
                        record['total_price'] = str(float(i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:].split(" ")[0]) * 100) + " Lac"

                    extracted_records.append(record)

                except:
                    print("Error in value")


        driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)        
        driver.implicitly_wait(50)
        driver.get(url)
        search =  driver.find_element_by_id('keyword')
        search.send_keys(location)
        submit = driver.find_element_by_id('submit_query')
        submit.click()
        sleep(10)
        driver.implicitly_wait(50)
        pages = driver.find_elements_by_xpath("//div[@class='Pagination__srpPageBubble list_header_semiBold']/a")

        extracted_records = []

        for page in range(0,len(pages)//2):
            p = pages[page].get_attribute('href')
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(p)
            post_list = driver.find_elements_by_xpath("//div[@class='pageComponent srpTop__tuplesWrap']/div[@class='pageComponent srpTuple__srpTupleBox srp']")
            adding_post(post_list)
            sleep(10)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    

        driver.implicitly_wait(30)
        driver.close()

        with open(f"{location}_location.json", 'w', encoding='utf-8', errors='ignore') as f:

            json.dump(extracted_records, f, ensure_ascii=False, indent=4)

        # return extracted_records
        return jsonify(extracted_records)



# @app.route('/user')
# def users(label=None):
#     url = "http://chuachinhon.pythonanywhere.com"

#     option = webdriver.ChromeOptions()
#     option.add_argument("--window-size=1920,1080")
#     option.add_argument("--disable-extensions")
#     option.add_argument("--proxy-server='direct://'")
#     option.add_argument("--proxy-bypass-list=*")
#     option.add_argument("--start-maximized")
#     option.add_argument("--headless")
#     option.add_argument("--disable-gpu")
#     option.add_argument("--disable-dev-shm-usage")
#     option.add_argument("--no-sandbox")
#     option.add_argument("--ignore-certificate-errors")
#     option.add_argument("--incognito")

#     option.add_argument(
#         "user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'")
#     path = 'scrape.png'

#     driver = webdriver.Chrome(
#         executable_path='chromedriver', chrome_options=option)
#     username = request.args.get('username')

#     try:
#         f = open(f"{username}_username.json",
#                  encoding='utf-8', errors='ignore')
#         data = json.load(f)
#         return jsonify(data)

#     except:

#         consumer_key = ''
#         consumer_secret = ''
#         access_token_key = ''
#         access_token_secret = ''
#         auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#         auth.set_access_token(access_token_key, access_token_secret)
#         api = tweepy.API(auth)

#         number_of_tweets = 10

#         tweets = api.user_timeline(screen_name=username)
#         tweets_for_csv = [tweet.text for tweet in tweets]

#         temp_data = []
#         data = []

#         for i in tweets_for_csv:
#             temp_data.append(i)

#         for index, i in enumerate(temp_data):
#             obj = {}
#             driver.get(url)
#             search = driver.find_element_by_xpath(
#                 '/html/body/div[1]/form/textarea')
#             obj['tweet'] = i
#             obj['id'] = index
#             text = i.split(" ")
#             cleaned_text = [t.lower() for t in text if(t.isalpha())]
#             search.send_keys(' '.join(cleaned_text))
#             submit = driver.find_element_by_class_name('btn-info')
#             submit.click()
#             # sleep(1)
#             result = driver.find_element_by_xpath('/html/body/div/p')
#             if(result.text == "Real tweet"):
#                 obj["is_troll"] = 0
#             else:
#                 obj["is_troll"] = 1

#             sleep(1)

#             data.append(obj)

#         with open(f"{username}_username.json", 'w', encoding='utf-8', errors='ignore') as f:

#             json.dump(data, f, ensure_ascii=False, indent=4)

#     return jsonify(data)


if __name__ == '__main__':
    app.run()