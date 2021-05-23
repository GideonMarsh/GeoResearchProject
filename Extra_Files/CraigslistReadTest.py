# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 13:07:52 2019

@author: Gideon
"""

from __future__ import division, print_function, unicode_literals
import numpy as np
import os
import math
import pandas as pd
from requests import get
from bs4 import BeautifulSoup
import re
from time import sleep
from random import randint

prices = []
addresses = []
bedrooms = []
bathrooms = []
sizes = []
availability_dates = []
other_tags = []

# The url of the craigslist apartments page
url = "https://fresno.craigslist.org/search/apa"

# The number of pages to be read (120 posts per page)
# Each post takes about 3 seconds to read - 6 minutes per page!
# If pages is 0, read all pages
pages = 2


count = 0
failedLoads = 0

try:
    # Get total pages
    response = get(url)
except:
    print("Could not load url")
else:
    html_soup = BeautifulSoup(response.text, 'html.parser')
    if (not pages == 0):
        pages = min(int(html_soup.find('span',class_='totalcount').string) / 120, pages)
    else:
        pages = int(html_soup.find('span',class_='totalcount').string) / 120
    
    effectiveurl = url
    
    print("Starting scrape: reading",pages,"pages...")
    while count < pages:
        sleep(randint(1,4))
        
        # Get Craigslist webpage for aparments
        try:
            response = get(effectiveurl)
        except:
            count = count + 1
            failedLoads += 120
            effectiveurl = url + "?s=" + str(count * 120)
            print("Could not load page number", count,"- skipping to next page")
        else:
            html_soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get a list of each post from first page
            posts = html_soup.find_all('li', class_='result-row')
            
            for post in posts:
                # Wait for a few seconds to prevent throttling
                sleep(randint(1,4))
                # For each post, follow link to description page
                try:
                    post_response = get(post.a['href'])
                except:
                    failedLoads += 1
                else:
                    post_soup = BeautifulSoup(post_response.text, 'html.parser')
                
                    info = post_soup.find_all('p', class_='attrgroup')
                    
                    #print(info)
                    
                    already_found = False
                    
                    # Extract data from page
                    address = post_soup.find('div', class_="mapaddress")
                    if (not address == None):
                        #print("Address: " + html_soup.find('div', class_="mapaddress").string)
                        if (address.string in addresses):
                            already_found = True
                        else:
                            addresses.append(address.string)
                    else:
                        addresses.append(None)
                    
                    if (not already_found):
                        
                        price = post.find('span',class_='result-price')
                        if (not price == None):
                            prices.append(price.string)
                        else:
                            prices.append(None)
                        
                        found_info = [False,False,False,False]
                        for i in info:
                            data = i.find_all(string=re.compile("B[R|a]"))
                            if (data != [] and len(data) == 2): 
                                #print("Bedrooms: " + data[0][:1])
                                #print("Bathrooms: " + data[1][:1])
                                bedrooms.append(data[0][:1])
                                bathrooms.append(data[1][:1])
                                found_info[0] = True
                            data = i.find_all(string=re.compile("^ft$"))
                            if (data != []): 
                                #print("Size (sqft): " + data[0].find_previous_sibling('b').string)
                                sizes.append(data[0].find_previous_sibling('b').string)
                                found_info[1] = True
                            data = i.find_all('span', class_='property_date')
                            if (data!= []): 
                                #print("Available: " + data[0]['data-date'])
                                availability_dates.append(data[0]['data-date'])
                                found_info[2] = True
                            tags = ''
                            for j in i.find_all('span', class_=""):
                                if (j.string != None):
                                    #print("Other info: " + j.string)
                                    tags = tags + j.string + '; '
                            if (tags != ''):
                                other_tags.append(tags)
                                found_info[3] = True
                        
                        # Fill in missing values for data not found
                        if (not found_info[0]):
                            bedrooms.append(None)
                            bathrooms.append(None)
                        if (not found_info[1]):
                            sizes.append(None)
                        if (not found_info[2]):
                            availability_dates.append(None)
                        if (not found_info[3]):
                            other_tags.append(None)
            count = count + 1
            effectiveurl = url + "?s=" + str(count * 120)
            #print("Page", count, "complete - next page...")
        
    
    # Create table with data
    craigslist_info = pd.DataFrame({'address' : addresses,
                                    'price' : prices,
                                    'bedrooms' : bedrooms,
                                    'bathrooms' : bathrooms,
                                    'size' : sizes,
                                    'availability date' : availability_dates,
                                    'tags' : other_tags})
    
    endLoop = True
    userInput = ""
    while (endLoop):
        try:
            craigslist_info.to_csv('Craigslist_Scrape_Test.csv',index=False)
            
            print(failedLoads,"/",pages * 120,"posts were unable to be read.")
            print("Scrape complete - file saved")
            endLoop = False
        except:
            print("Could not write to file - close the file and try again")
            print("Enter quit to end program without saving", end = "")
            userInput = input("Enter anything else to try again: ")
            if (userInput == "quit"):
                endLoop = False
                print("Scrape complete - file not saved")
