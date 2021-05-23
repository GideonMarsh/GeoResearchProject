# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 11:17:10 2019

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
import datetime as dt

# Class for preventing sleep mode while running
class WindowsInhibitor:
    '''Prevent OS sleep/hibernate in windows; code from:
    https://github.com/h3llrais3r/Deluge-PreventSuspendPlus/blob/master/preventsuspendplus/core.py
    API documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx'''
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        pass

    def inhibit(self):
        import ctypes
        print("Preventing Windows from going to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS | \
            WindowsInhibitor.ES_SYSTEM_REQUIRED)

    def uninhibit(self):
        import ctypes
        print("Allowing Windows to go to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS)

try:
    osSleep = None
    
    # The list of regions to scrape from
    # The name must be the exact same as the start of the url
    # For example: to read Gold Country, CA apartments (goldcountry.craigslist.org), enter "goldcountry"
    regions = ['portland','bakersfield','chico','fresno','goldcountry','hanford','humboldt','imperial',
               'inlandempire','losangeles','mendocino','merced','modesto','monterey','orangecounty',
               'palmsprings','redding','reno','sacramento','sandiego','slo','santabarbara','santamaria',
               'sfbay','siskiyou','stockton','susanville','ventura','visalia','yubasutter']
    
    # The file name of the output file
    outFile = 'Craigslist_Scrape.csv'
    
    # The number of pages to be read (120 posts per page)
    # Each post takes about 2 seconds to read - 4 minutes per page!
    # If pages is 0, read all pages
    pages = 0
    
    # The maximum number of seconds to sleep between each html get request
    # The program will randomly sleep between 1 second and the number of seconds specified
    # The lower the number, the faster the program BUT ALSO you are more likely to be blocked
    sleepSecs = 3
    
    # The list of all tags to be included in the table
    # The housing, laundry, and parking tags can have several different values, shown below
    # The others are either true or false
    tags_names = ['housing type','laundry','parking','cats are OK - purrr','dogs are OK - wooof',
                  'furnished','no smoking','wheelchair accessible','EV charging']
    
    housing_types = ['apartment','condo','cottage/cabin','duplex','flat','house','in-law','loft',
                     'townhouse','manufactured','assisted living','land']
    
    laundry_types = ['w/d in unit','w/d hookups','laundry in bldg','laundry on site','no laundry on site']
    
    parking_types = ['carport','attached garage','detached garage','off-street parking','street parking',
                     'valet parking','no parking']
    
    # The two-dimensional list for storing the tag values
    # Must contain an empty bracket for each tag in 'tag_names' above
    tags_values = [[],[],[],[],[],[],[],[],[]]
    
    # The lists to store the data
    ids = []
    latitudes = []
    longitudes = []
    prices = []
    addresses = []
    bedrooms = []
    bathrooms = []
    sizes = []
    availability_dates = []
    links = []
    last_read_date = []
    other_tags = []
    scrape_dates = []
    
    # The number of posts that failed to load
    failedLoads = 0
    
    # The number of old posts
    oldPosts = 0
    
    # Total posts checked
    totalPosts = 0
    
    # Read the existing file
    existing_info = None
    try:
        existing_info = pd.read_csv(outFile)
        # Extract the date of previous scrape
        date_limit = existing_info['last scrape date'][0]
    except IndexError:
        print("WARNING! Index for 'last scrape date' is incorrect. Scraper will read all posts regardless of post date.")
        date_limit = None
    except:
        date_limit = None
    
    # Prevent Windows from going into sleep mode while running
    if os.name == 'nt':
        osSleep = WindowsInhibitor()
        osSleep.inhibit()
    
    print("Starting scrape:")
    scrapeDate = dt.datetime.now()
    for r in regions:
        # The url of posts
        url = "https://"+r+".craigslist.org/search/apa"
        
        # The current page count
        count = 0
        
        try:
            # Get total pages
            response = get(url)
        except:
            print("Could not load url for " + r)
        else:
            html_soup = BeautifulSoup(response.text, 'html.parser')
            if (not pages == 0):
                pageCount = math.ceil(min(int(html_soup.find('span',class_='totalcount').string) / 120, pages))
            else:
                pageCount = math.ceil(int(html_soup.find('span',class_='totalcount').string) / 120)
            
            effectiveurl = url
            
            print("Reading",pageCount,"pages for " + r)
            while count < pageCount:
                sleep(randint(1,sleepSecs))
                
                # Get a page of aparments
                try:
                    response = get(effectiveurl)
                except:
                    count = count + 1
                    failedLoads += 120
                    totalPosts += 120
                    effectiveurl = url + "?s=" + str(count * 120)
                    print("Could not load page number", count,"- skipping to next page")
                else:
                    html_soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Get a list of each post from first page
                    posts = html_soup.find_all('li', class_='result-row')
                    
                    for post in posts:
                        totalPosts += 1
                        
                        # Check post result date
                        # If not recent, skip to save time
                        if (date_limit == None or post.find('time', class_='result-date') == None or date_limit <= post.find('time', class_='result-date')['datetime']):
                            # Wait for a few seconds to prevent throttling
                            sleep(randint(1,sleepSecs))
                            # For each post, follow link to description page
                            try:
                                post_response = get(post.a['href'])
                            except:
                                failedLoads += 1
                            else:
                                post_soup = BeautifulSoup(post_response.text, 'html.parser')
                                
                                # If post is not recent, don't save
                                if (date_limit == None or post_soup.find('time',class_='date timeago') == None or date_limit <= post_soup.find('time',class_='date timeago')['datetime']):
                                    
                                    # Find data
                                    link = post.a['href']
                                    
                                    id_ = None
                                    br = None
                                    ba = None
                                    size = None
                                    date = None
                                    mapdata = None
                                    
                                    price = post.find('span',class_='result-price')
                                    address = post_soup.find('div', class_="mapaddress")
                                    
                                    # If address can't be found in tags, search title for address instead
                                    if (address == None):
                                        if (not post_soup.find('span',class_='postingtitletext') == None):
                                            address = post_soup.find('span',class_='postingtitletext').find('small',string=re.compile("^(.*)$"))
                                    
                                    info = post_soup.find_all('p', class_='attrgroup')
                                    
                                    if (not info == None):
                                        for i in info:
                                            if (br == None):
                                                br = i.find(string=re.compile("[0-9]+BR$"))
                                            if (ba == None):
                                                ba = i.find(string=re.compile("[0-9]+Ba$"))
                                            if (size == None):
                                                size = i.find(string=re.compile("^ft$"))
                                            if (date == None):
                                                date = i.find('span', class_='property_date')
                                    
                                    
                                    if not post_soup.find('p',class_='postinginfo',string=re.compile('post id')) == None:
                                        id_ = post_soup.find('p',class_='postinginfo',string=re.compile('post id')).string[9:]
                                    
                                    mapData = post_soup.find('div',id='map')
                                    
                                    # Append data to data arrays
                                    links.append(link)
                                    last_read_date.append(None)
                                    ids.append(id_)
                                    scrape_dates.append(dt.datetime.now())
                                    
                                    if price == None:
                                        prices.append(None)
                                    else:
                                        prices.append(price.string)
                                    
                                    if address == None:
                                        addresses.append(None)
                                    else:
                                        if ('(' in address.string):
                                            addresses.append(address.string[2:len(address.string) - 1])
                                        else:
                                            addresses.append(address.string)
                                    
                                    if br == None:
                                        bedrooms.append(None)
                                    else:
                                        bedrooms.append(br[:1])
                                    
                                    if ba == None:
                                        bathrooms.append(None)
                                    else:
                                        bathrooms.append(ba[:1])
                                    
                                    if size == None:
                                        sizes.append(None)
                                    else:
                                        sizes.append(size.find_previous_sibling('b').string)
                                        
                                    if date == None:
                                        availability_dates.append(None)
                                    else:
                                        availability_dates.append(date['data-date'])
                                        
                                    if mapData == None:
                                        latitudes.append(None)
                                        longitudes.append(None)
                                    else:
                                        latitudes.append(mapData['data-latitude'])
                                        longitudes.append(mapData['data-longitude'])
                                    
                                    # Get all tags as strings
                                    data = []
                                    for j in i.find_all('span', class_=""):
                                        if (not j.string == None):
                                            data.append(j.string)
                                    
                                    # Check tag lists to see if post contains each tag
                                    for tag in tags_names[3:]:
                                        if (tag in data):
                                            tags_values[tags_names.index(tag)].append(True)
                                        else:
                                            tags_values[tags_names.index(tag)].append(None)
                                    tagMissing = [True,True,True]
                                    for d in data:
                                        if (d in housing_types):
                                            tags_values[tags_names.index('housing type')].append(d)
                                            tagMissing[0] = False
                                        if (d in laundry_types):
                                            tags_values[tags_names.index('laundry')].append(d)
                                            tagMissing[1] = False
                                        if (d in parking_types):
                                            tags_values[tags_names.index('parking')].append(d)
                                            tagMissing[2] = False
                                    for k in range(3):
                                        if (tagMissing[k]):
                                            tags_values[k].append(None)
                                    
                                    # Check for any missed tags
                                    tags = ''
                                    for j in data:
                                        if (not j == None and not (j in tags_names or j in housing_types or j in laundry_types or j in parking_types)):
                                            tags = tags + j + "; "
                                    if (not tags == ''):
                                        other_tags.append(tags)
                                else:
                                    oldPosts += 1
                        else:
                            oldPosts += 1
                    count = count + 1
                    effectiveurl = url + "?s=" + str(count * 120)
                    print("Page", count, "complete - next page...")
                    # Page complete
            print("Finished reading posts for " + r)
            # End of one region
        # End of scrape
        
    # Create table with data
    new_info = pd.DataFrame({'listing id' : ids,
                             'address' : addresses,
                             'latitude' : latitudes,
                             'longitude' : longitudes,
                             'price' : prices,
                             'bedrooms' : bedrooms,
                             'bathrooms' : bathrooms,
                             'size' : sizes,
                             'availability date' : availability_dates,
                             tags_names[0] : tags_values[0],
                             tags_names[1] : tags_values[1],
                             tags_names[2] : tags_values[2],
                             tags_names[3] : tags_values[3],
                             tags_names[4] : tags_values[4],
                             tags_names[5] : tags_values[5],
                             tags_names[6] : tags_values[6],
                             tags_names[7] : tags_values[7],
                             tags_names[8] : tags_values[8],
                             'link' : links,
                             'read date' : scrape_dates,
                             'last scrape date' : last_read_date})
    
    # Append to existing file
    endLoop = True
    userInput = ""
    while (endLoop):
        try:    
            craigslist_info = pd.concat([existing_info, new_info],sort=False)
            endLoop = False
        except:
            print("Could not combine the new data with the existing file.")
            print("The old file most likely has the wrong format.")
            print("Save the old file under a different name to keep it.")
            print("Enter 'quit' to end the program without saving.")
            print("Enter 'write' to overwrite the old file.", end = "")
            userInput = input("Enter anything else to try combining the files again: ")
            if (userInput == "quit"):
                print("Scrape complete - file not saved")
                endLoop = False
            if (userInput == "write"):
                print("Overwriting old data...")
                craigslist_info = new_info
                endLoop = False
    
    craigslist_info['last scrape date'] = scrapeDate
    
    if (not userInput == "quit"):
        # If output file is open, ask user to close it before attempting to write
        endLoop = True
        userInput = ""
        while (endLoop):
            try:
                craigslist_info.to_csv(outFile,index=False,
                    columns=['listing id','address','latitude','longitude','price',
                    'bedrooms','bathrooms','size','availability date',tags_names[0],tags_names[1],
                    tags_names[2],tags_names[3],tags_names[4],tags_names[5],
                    tags_names[6],tags_names[7],tags_names[8],'link','read date',
                    'last scrape date'], encoding='utf-8')
                
                print(failedLoads,"/",totalPosts,"posts were unable to be read.")
                if (not date_limit == None):
                    print(oldPosts,"posts were outdated and skipped.")
                print("File saved")
                
                # If tags were found that aren't included in the output file, print them to the console
                if (len(other_tags) > 0):
                    print("Tags were found that were not included in table:")
                    print(other_tags)
                endLoop = False
            except PermissionError:
                print("Could not write to file - close the file and try again")
                print("Enter 'quit' to end program without saving", end = "")
                userInput = input("Enter anything else to try again: ")
                if (userInput == "quit"):
                    endLoop = False
                    print("Scrape complete - file not saved")
    print("Scrape complete")
#except:
#    print("Unknown error encountered - ending program")
finally:
    if osSleep:
        osSleep.uninhibit()