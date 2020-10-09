# Import Dependencies
from flask import Flask, render_template
import pandas as pd
import pymongo

# Create single function to scrape all the data, export it to mongodb and html file
def scrapeData():
    # Import Dependencies
    from bs4 import BeautifulSoup
    import pandas as pd
    import requests
    import pymongo

    # Base news page
    News_URL = "https://mars.nasa.gov/news/"
    # Pulls URL and parses to HTML using BeautifulSoup
    News_Response = requests.get(News_URL)
    News_Soup = BeautifulSoup(News_Response.text, 'html.parser')
    # Pulls the text of the title, and paragraph based on their parent div classes
    news_title = News_Soup.find("div", class_="content_title").text
    news_p = News_Soup.find("div", class_="rollover_description_inner").text

    # Base image page
    Small_Image_URL = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    # Pulls URL and parses to HTML using BeautifulSoup
    Small_Image_Response = requests.get(Small_Image_URL)
    Small_Image_Soup = BeautifulSoup(Small_Image_Response.text, 'html.parser')
    # Pulls the target from the "more info" button to get a new URL to reference the full size image
    Details_Page_URL = Small_Image_Soup.find("a", class_="button fancybox")["data-link"]
    # Combine base with full size image URLs
    Full_Image_URL = "https://www.jpl.nasa.gov" + Details_Page_URL
    # Pulls NEW URL and parses to HTML using BeautifulSoup
    Full_Image_Response = requests.get(Full_Image_URL)
    Full_Image_Soup = BeautifulSoup(Full_Image_Response.text, 'html.parser')
    # Pulls tag contating full size image
    Full_Image_URL = Full_Image_Soup.find('figure', class_="lede")
    # Combines base with final target URLs
    featured_image_url = "https://www.jpl.nasa.gov" + Full_Image_URL.a['href']

    # Base table page
    Stats_URL = "https://space-facts.com/mars/"
    # Use built in Pandas function to read the webpage
    Stats_Table = pd.read_html(Stats_URL)
    # Finds first tatble and assigns it to dataframe
    Stats_Table_df = Stats_Table[0]
    # Clean format of DataFrame prior to HTML output
    Stats_Table_df.columns = ["Mars","Metrics"]
    Stats_Table_df.reset_index(drop=True, inplace=True)
    # Output table in HTML format to be used in landing page
    Stats_html = Stats_Table_df.to_html(index=False)

    # Base hemispheres page
    Hemisphere_Base_URL = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    # Pulls URL and parses to HTML using BeautifulSoup
    Hemisphere_Base_Response = requests.get(Hemisphere_Base_URL)
    Hemisphere_Base_Soup = BeautifulSoup(Hemisphere_Base_Response.text, 'html.parser')
    # Finds all 'item' class div tags
    Hemisphere_List = Hemisphere_Base_Soup.find_all('div', class_="item")
    # Establish list variables to append to
    titles = []
    raw_img_urls = []
    full_img_urls = []
    # First loop - gets titles and URLs for enhanced photo TARGET LINKS
    for x in Hemisphere_List:
        # Add currrently looped title to titles list
        titles.append(x.div.text)
        # Combine base with full size image URLs and add currrently looped URL to raw image list
        raw_img_urls.append("https://astrogeology.usgs.gov" + x.a["href"])
    # Second loop - for each TARGET LINK, get the full size image URL from each of those pages
    for x in raw_img_urls:
        # Pulls currently looped URL and parses to HTML using BeautifulSoup
        Hemisphere_response = requests.get(x)
        Hemisphere_Soup = BeautifulSoup(Hemisphere_response.text, 'html.parser')
        # Pulls full size image URL from TARGET LINK
        Hemisphere_url = Hemisphere_Soup.find("img", class_="wide-image")["src"]
        # Combine base URL with full image URL and add currrently looped URL to full size image list
        full_img_urls.append("https://astrogeology.usgs.gov" + Hemisphere_url)
    # Create dataframe and assign titles and full size image URLs as columns
    Hemisphere_df = pd.DataFrame()
    Hemisphere_df["title"] = titles
    Hemisphere_df["img_url"] = full_img_urls

    # Combine data into one dictionary and output to MondoDB
    Mongo_df = Hemisphere_df.append({"title":news_title, "img_url":news_p}, ignore_index=True)
    Mongo_df = Mongo_df.append({"title":"Featured Image","img_url":featured_image_url}, ignore_index=True)
    Mongo_df = Mongo_df.append({"title":"Stats Table","img_url": Stats_html}, ignore_index=True)
    Mongo_dict = Mongo_df.to_dict("records")

    # Setup connection to mongodb
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    # Clears existing database for fresh start
    client.mars_db.web_links.drop()
    # Add all items to be passed to index.html into MongoDB
    client.mars_db.web_links.insert(Mongo_dict)
    
    return

# Setup connection to mongodb
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# Create an instance of Flask
app = Flask(__name__)

# Route to render index.html template
@app.route("/")
def index():
    # Pull data from mongoDB and pass to webpage
    links = client.mars_db.web_links.find()
    print("Homepage Accessed")
    # Return template and data
    return render_template("index.html", links=links)

@app.route("/scrape")
def scrape():
    # Run Data Scraper function from mission_to_mars.ipynb
    scrapeData()
    # User output
    print("Data Scrape Complete")
    # Pull updated data from mongoDB and pass to webpage
    links = client.mars_db.web_links.find()
    # Return template and data
    return render_template("index.html", links=links)

if __name__ == "__main__":
    app.run(debug=False)