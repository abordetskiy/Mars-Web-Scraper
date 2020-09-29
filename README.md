# Welcome to the Mars Web Scraper!
### To visit the webpage, please run the app.py script and open the webpage in your browser
#### Please note, properly running app.py may require you to pip install ipynb

This script pulls data and photos from different websites related to Mars. These items are scraped directly from the web using BeautifulSoup and passed into an HTML template via Flask using a MongoDB database to store the information. 


Files in this repository:

mission_to_mars.ipynb - this file contains the code to scrape data from the web. It includes breakdowns of the individual sections with outputs, and a function created to be called from app.py. This file need not be run seperately.

index.html - this is the template to which the scraped data is passed. It is based off of a generic Bootstrap template and includes a jumbotron header who's background is set to the featured image, a scrape data button, a featured image link, the lastest news, a Mars fact table, and an image gallery with thumbnails and links to the full size images.

app.py - this file contains the Flask code, which allows us to pass variables into an html template. It pulls from the MongoDB database and passes that information to the webpage. Please run this file to access the website.

