# Import Dependencies
from flask import Flask, render_template
import pandas as pd
import pymongo
#from mission_to_mars.ipynb import scrapeData()




# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
########################### mongo_Variable = PyMongo(app, uri="mongodb://localhost:27017/DATABASE_NAME")


# Route to render index.html template
@app.route("/")
def index():
    # Setup connection to mongodb
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    links = client.mars_db.web_links.find()
    print(links)
    stats_table = pd.read_html("Resources/stats.html")
    # Return template and data
    return render_template("index.html", links=links, stats_table=stats_table)


@app.route("/scraper")
def scraper():

    
    # Return template and data
    return render_template("scraper.html", links=links, stats_table=stats_table)

if __name__ == "__main__":
    app.run(debug=False)