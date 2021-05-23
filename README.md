# GeoResearchProject
Web scraper for Craigslist apartment data

Also includes a small program for changing the format of a spreadsheet (see Extra_Files)

### Files:
- ***CraigslistAptScraper_Portland.py*** is the main web scraper program
- ***Craigslist_Scrape.csv*** is the output file for the scraper

Scrapes important apartment data from Craigslist postings such as rent, address, size, number of bedrooms and bathrooms, etc., as well as whatever tags are on the posts. This information is then saved as a .csv file. If the .csv file already exists when the program is run, the program will read the 'last scrape date' column and only add posts that have been added since that date, effectively updating the file with new postings.

The posts are read with a delay to prevent throttling. Because of this the program takes several hours to read through all apartment postings. This time is reduced after the first run, since it only needs to read new posts.

The scraper was created to read apartments from Portland, however any region can be read by changing the url of the apartments page in the code (the url variable). 

Extra_Files:
- *TableFixFormat.py* is the short program for reformatting a spreadsheet
- *CraigslistAddCounty.py* was used to update the Craigslist_Scrape spreadsheet when a new column was added
- *CraigslistAptScraper.py* and *CraigslistReadTest.py* are old/test versions of the project file

Data_Files:
- *Test_Data.csv* and *Test_Data.xlsx* are the test input files for the TableFixFormat program
- *Test_Data_Fix.csv* and *Test_Data_Fix.xlsx* are the outputs of the TableFixFormat program for the above input files
- *Craigslist_Scrape_Test.csv* is an old version of the CraigslistAptScraper_Portland program output

#### Created on commission for Dr. Hongwei Dong at CSU Fresno
