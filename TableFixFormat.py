# Written by Gideon Marsh
# Last updated: Oct 29 2019

from __future__ import division, print_function, unicode_literals
import numpy as np
import os
import math
import pandas as pd

# Read a single Excel or CSV file specified in the program as variable "filename"
# Check this file to see if it uses wide format
# If it does, create a new file with long format
# Save new file in same directory as original file with name "[original name]_Fix"

# Directory of file to be reformatted
# Path can be relative or absolute
filename = "Data_Files/Test_Data.csv"

# Get file type
ext = filename[filename.find(".",len(filename) - 5):]

# Attempt to get file and turn into a dataframe
try:
    if ext == ".xlsx" or ext == ".xls":
        data = pd.read_excel(filename)
    elif ext == ".csv":
        data = pd.read_csv(filename)
    else:
        raise Exception()
except:
    # File could not be read
    # Common reasons include file does not exist, or is not an acceptable file type
    print("ERROR: File could not be read. Check the path name for errors.")
    print("       File name can be entered as an absolute or relative path.")
else:
    # Check if file uses wide format
    cols = ['state','county','year','Jan','Feb','Mar','Apr','May','June',\
            'July','Aug','Sept','Oct','Nov','Dec']
    if np.array_equal(cols, data.columns):
        # File uses wide format
        
        # Check that new file can be overwritten
        try:
            testWrite = pd.DataFrame(columns=cols) # Empty dataframe used only to check writeability of new file
            if ext == ".xlsx" or ext == ".xls":
                newFilename = filename[:filename.find(".",len(filename) - 5)] + "_Fix.xlsx"
                data.to_excel(newFilename)
            elif ext == ".csv":
                newFilename = filename[:filename.find(".",len(filename) - 5)] + "_Fix.csv"
                data.to_csv(newFilename)
        except:
            # File cannot be overwritten
            print("ERROR: File '" + newFilename +"' cannot be overwritten.")
            print("       File already exists and is open in another program.")
            print("       Close the file and try again.")
        else:
            # File can be overwritten
            # Create new dataframe with long format
            # May take a while depending on the number of rows
            
            print("Reformatting file...",end ="")
            
            months = ['Jan','Feb','Mar','Apr','May','June',\
                      'July','Aug','Sept','Oct','Nov','Dec']
            q1 = math.floor(len(data.index) / 4)
            q2 = math.floor(len(data.index) / 2)
            q3 = q1 + q2
            
            newState = []
            newCounty = []
            newYear = []
            newMonth = []
            newTemp = []
            
            for i in range(len(data.index)):
                for j in range(12):
                    newState.append(data['state'].iloc[i])
                    newCounty.append(data['county'].iloc[i])
                    newYear.append(data['year'].iloc[i])
                    newMonth.append(months[j])
                    newTemp.append(data[months[j]].iloc[i])
                    
                if (i == q1):
                    print("25%...",end ="")
                if (i == q2):
                    print("50%...",end ="")
                if (i == q3):
                    print("75%...")
    
            newFile = pd.DataFrame({'state': newState,
                                    'county': newCounty,
                                    'year': newYear,
                                    'month': newMonth,
                                    'temp': newTemp})
    
            if ext == ".xlsx" or ext == ".xls":
                # Create new Excel file using new dataframe
                # Use an ExcelWriter to enforce regular formatting
                writer = pd.ExcelWriter(newFilename, engine='xlsxwriter')
                try:
                    newFile.to_excel(writer,sheet_name='Sheet1',index=False,startrow=1,header=False)
                    workbook  = writer.book
                    worksheet = writer.sheets['Sheet1']
                    header_format = workbook.add_format({'bold':False,'border':0})
                    
                    for col_num, value in enumerate(newFile.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        
                    writer.save()
                except:
                    # New file could not be saved
                    print("ERROR: Cannot overwrite '" + newFilename + "'")
                else:
                    print("Reformatted file saved as '" + newFilename + "'")
            if ext == ".csv":
                # Create new CSV file using new dataframe
                try:
                    newFile.to_csv(newFilename,index=False)
                except:
                    # New file could not be saved
                    print("ERROR: Cannot overwrite '" + newFilename + "'")
                else:
                    print("Reformatted file saved as '" + newFilename + "'")
    else:
        # File does not use wide format
        print("ERROR: File does not use correct format for reformatting.")
  