from flask import Flask, request, jsonify
import json
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as soup
import re
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


@app.route('/api/multiple_legacy')
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



@app.route('/api/multiple')
def fast_multiple_page(label=None):

    url = "https://www.makaan.com/"
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
    option.add_argument("--headless")
    option.add_argument("--incognito")
    option.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'")
    location = request.args.get('location')
    location = location.lower()
    
    google_map_api = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key=AIzaSyD5gN9lDFp22bYRK5U8-2KhgpjkqNoqr7o"

    try:
        f = open(f"{location}_location.json", encoding='utf-8', errors='ignore')
        print(location)
        data = json.load(f)
        return jsonify(data)

    except FileNotFoundError:
        req = requests.get(google_map_api)
        r = req.json()["results"][0]["geometry"]["location"]
        city_coordinates = {"lat":r["lat"],"lng":r["lng"]}
        option.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'")
        driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=option)
        driver.implicitly_wait(30)
        driver.get(url)
        sleep(5)
        driver.implicitly_wait(30)
        search =  driver.find_element_by_xpath('/html/body/div[1]/main/div/section[1]/div[1]/div/div[3]/div[1]/div/div/div/div[2]/input')
        search.send_keys(location)
        drop = driver.find_element_by_class_name("result-type")
        driver.implicitly_wait(30)
        drop.click()
        driver.implicitly_wait(100)
        sleep(1)
        submit = driver.find_element_by_class_name('js-count-properties')
        submit.click()
        # driver.implicitly_wait(100)
        # submit = driver.find_element_by_class_name('css-1hlc5qw')
        # submit.click()

        # sleep(10)

        url = driver.current_url
        
        driver.close()

        dataset = []

        number = 0
        
        location_dict = {}

        for page in range(1,15):

            page_url = f'{url}?page='+str(page)

            response = requests.get(url)

            page_html = soup(response.text, 'html.parser') 

            house_containers = page_html.find_all("li",class_="cardholder")

            for data in house_containers:
                record = {}

                location_ = data.find_all("a",class_="loclink")
                for i in location_:
                        d=i.text
                        r = d.split(',',)[0]

                record["location"] = r
                
                try:
                    if(record["location"] in location_dict.keys()):
                        record["location_coordinates"] = location_dict[record["location"]]
                    
                    else:
                        req_loc = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={record["location"]},{location}&key=AIzaSyD5gN9lDFp22bYRK5U8-2KhgpjkqNoqr7o')
                        req_loc = req_loc.json()["results"][0]["geometry"]["location"]
                        record["location_coordinates"] = {"lat":req_loc["lat"],"lng":req_loc["lng"]}
                        location_dict[record["location"]] = record["location_coordinates"]
            
                except:
                    print("error")
                    
                        
                
                
                cost = data.find_all("td",class_="price")
                for i in cost:
                    d=i.text
                    if 'L' in d:
                        a = d.split()[0]
                        record["total_price"] = float(a) 
                    elif 'Cr' in d:
                        b = d.split()[0]
                        record["total_price"] = float(b) * 100
                    else:  
                        e=0
                        record["total_price"] =float(e)


                rate_sqft=data.find_all('td',class_="lbl rate")
                for i in rate_sqft:
                    d=i.text
                    res= d.split('/',)[0]
                    r=re.sub(",","" ,res) 
                    record["cost_square"] = r


                area_sqft=data.find_all('td',class_="size")
                for i in area_sqft:
                    d=i.text
                    record["square"] = d

                building_status_=data.find_all("td",class_="val")
                for i in building_status_:
                    d=i.text
                    record["building_status"] = d


                bhk = data.find_all("a",class_="typelink")
                for i in bhk:
                    link = i.get('href')
                    d=i.text
                    r = d.split(',',)[0]

                record["post_link"] = link
                record["bedroom"] = ' '.join(r.split(" ")[:2])
                record["city"] = location
                
                record["city_coordinates"] = city_coordinates

                dataset.append(record)

                number += 1


        print(number)
        with open(f"{location}_location.json", 'w', encoding='utf-8', errors='ignore') as f:

            json.dump(dataset, f, ensure_ascii=False, indent=4)

        # return extracted_records
        return jsonify(dataset)


if __name__ == '__main__':
    app.run()
