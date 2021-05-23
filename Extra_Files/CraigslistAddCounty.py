# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 14:10:49 2019

@author: Gideon
"""

from __future__ import division, print_function, unicode_literals
import numpy as np
import os
import math
import pandas as pd

filename = "Craigslist_Scrape.csv"

# Attempt to get file and turn into a dataframe
try:
    data = pd.read_csv(filename)
except:
    # File could not be read
    # Common reasons include file does not exist, or is not an acceptable file type
    print("ERROR: File could not be read. Check the path name for errors.")
    print("       File name can be entered as an absolute or relative path.")
else:
    # Check if file is missing county column
    cols = ['address','price','bedrooms','bathrooms','size',
            'availability date','housing type','laundry','parking',
            'cats are OK - purrr','dogs are OK - wooof','furnished',
            'no smoking','wheelchair accessible','EV charging','link',
            'last read date']
    if np.array_equal(cols, data.columns):
        print("Reformatting file...")
        
        counties = []
        
        for i in range(len(data.index)):
            counties.append(data['link'].iloc[i][32:35])

        newFile = pd.DataFrame({'address' : data['address'],
                                 'county' : counties,
                                 'price' : data['price'],
                                 'bedrooms' : data['bedrooms'],
                                 'bathrooms' : data['bathrooms'],
                                 'size' : data['size'],
                                 'availability date' : data['availability date'],
                                 'housing type' : data['housing type'],
                                 'laundry' : data['laundry'],
                                 'parking' : data['parking'],
                                 'cats are OK - purrr' : data['cats are OK - purrr'],
                                 'dogs are OK - wooof' : data['dogs are OK - wooof'],
                                 'furnished' : data['furnished'],
                                 'no smoking' : data['no smoking'],
                                 'wheelchair accessible' : data['wheelchair accessible'],
                                 'EV charging' : data['EV charging'],
                                 'link' : data['link'],
                                 'last read date' : data['last read date']})
        # Create new CSV file using new dataframe
        try:
            newFile.to_csv('Craigslist_Scrape.csv',index=False,
                columns=['address','county','price','bedrooms','bathrooms','size',
                'availability date','housing type','laundry','parking',
                'cats are OK - purrr','dogs are OK - wooof','furnished',
                'no smoking','wheelchair accessible','EV charging','link',
                'last read date'], encoding='utf-8')
        except:
            # New file could not be saved
            print("ERROR: Cannot overwrite '" + filename + "'")
        else:
            print("Reformatted file saved as '" + filename + "'")
    else:
        # File does not use wide format
        print("ERROR: File does not use correct format for reformatting.")
  