from django.shortcuts import render
from django.http import HttpResponse
from .forms import LocationForm
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
from time import sleep
from django.http import JsonResponse


def main(location):
    url = "https://www.99acres.com/"
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    # option.add_argument('--no-sandbox')
    # option.add_argument('--disable-dev-shm-usage')
    # option.add_argument('window-size=1920x1480')
        
    # option.add_argument('window-size=1366x768')
    driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=option)

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

        record = {
        'total_price' : i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:],
        'cost_square' : i.find_element_by_id('srp_tuple_price').text.split('\n')[1][2:],
        'square' : i.find_element_by_id('srp_tuple_primary_area').text.split('\n')[0],
        'bedroom' : i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[0],
        'bathroom' : i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[1],
        'post_link' : i.find_element_by_id('srp_tuple_property_title').get_attribute('href')
        }

        extracted_records.append(record)

    driver.implicitly_wait(30)
    driver.close()

    return extracted_records
            # link = i.find_element_by_id('srp_tuple_property_title').get_attribute('href')
            # writer.writerow([i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:]
            #                 ,i.find_element_by_id('srp_tuple_price').text.split('\n')[1][2:]
            #                 ,i.find_element_by_id('srp_tuple_primary_area').text.split('\n')[0]
            #                 ,i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[0]
            #                 ,i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[1]
            #                 ,i.find_element_by_id('srp_tuple_property_title').get_attribute('href')])


    # with open('results.csv','w',encoding='utf-8') as f:
    #     writer = csv.writer(f,delimiter=',')
    #     writer.writerow(["Total Price","Cost/Square Ft","Square Ft","Bedroom","Bathroom","Contact"])
    #     for i in post_list:
    #         link = i.find_element_by_id('srp_tuple_property_title').get_attribute('href')
    #         writer.writerow([i.find_element_by_id('srp_tuple_price').text.split('\n')[0][2:]
    #                         ,i.find_element_by_id('srp_tuple_price').text.split('\n')[1][2:]
    #                         ,i.find_element_by_id('srp_tuple_primary_area').text.split('\n')[0]
    #                         ,i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[0]
    #                         ,i.find_element_by_id('srp_tuple_bedroom').text.split('\n')[1]
    #                         ,i.find_element_by_id('srp_tuple_property_title').get_attribute('href')])
    

def home(request,location):
    data = main(location)

    return JsonResponse(data,safe=False)