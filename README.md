# GeoResearchProject
Web scraper for Craigslist apartment data

Scrapes important apartment data such as rent, address, size, number of bedrooms and bathrooms, etc., as well as whatever tags are on the posts. This information is then saved as a .csv file. If the .csv file already exists when the program is run, the program will read the 'last scrape date' column and only add posts that have been added since that date, effectively updating the file with new postings.

The posts are read with a delay to prevent throttling. Because of this the program takes several hours to read through all apartment postings. This time is reduced after the first run, since it only needs to read new posts.

The scraper was created to read apartments from Portland, however any region can be read by changing the url of the apartments page in the code (the url variable). 

#### Created on commission for Dr. Hongwei Dong at CSU Fresno
