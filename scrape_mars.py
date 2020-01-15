# Import dependencies
import pandas as pd
import time
import requests
from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser("chrome")

def scrape():
    # Create mars_data dictionary to store all resulting information
    mars_data = {}


    ### SECTION 1 - START
    # First notate the URL that we will scrape the information from.
    urlNews = "https://mars.nasa.gov/news"

    # Create BeautifulSoup object; parse with 'html.parser'
    browser = init_browser()
    browser.visit(urlNews)

    time.sleep(1)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Discover and assign to variables the latest "News Title" & "Paragraph Text"
    news_title = soup.find('div',class_='content_title').a.text.strip()
    news_p = soup.find('div', class_='rollover_description_inner').text.strip()

    # EXPORT
    mars_data["news_title"] = news_title
    mars_data["news_p"] = news_p

    browser.quit()
    ### SECTION 1 - END


    ### SECTION 2 - START
    browser = init_browser()
    urlImage = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(urlImage)
    
    time.sleep(1)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Scrape the html code
    featured_image_url = soup.find('div', class_='carousel_items')

    # Dig into the html code, and split it until we're able to isolate the image url pathway only.
    featured_image_url = featured_image_url.article["style"].split("(")[1]
    featured_image_url = featured_image_url.split(")")[0]
    featured_image_url = featured_image_url.split("'")[1]
    featured_image_url = featured_image_url.split("'")[0]

    # Attach the pathway to the end of a url pathway to complete URL assembly.
    featured_image_url = "https://www.jpl.nasa.gov"+featured_image_url

    # EXPORT
    mars_data["featured_image_url"] = featured_image_url

    browser.quit()
    ### SECTION 2 - END


    ### SECTION 3 - START
    # URL
    urlWeather = "https://twitter.com/marswxreport?lang=en"

    response = requests.get(urlWeather)
    soup = BeautifulSoup(response.text, "html.parser")

    # Scrape weather data from tweet
    mars_weather = soup.find('p', class_="TweetTextSize").text

    # Strip off the "InSight" from the weather data string and capitalize "sol" to "Sol"
    mars_weather = mars_weather.lstrip('InSight ')
    mars_weather = mars_weather.capitalize()
    mars_weather = mars_weather.split('pic.twitter.com')[0]

    # EXPORT
    mars_data["mars_weather"] = mars_weather
    ### SECTION 3 - END


    ### SECTION 4 - START
    # URL
    urlFacts = "https://space-facts.com/mars/"

    # Use Pandas to scrape data.
    marsScrape = pd.read_html(urlFacts)

    # Convert data into dataframe table, and rename the columns & assign index.
    marsScrape_df = marsScrape[0]
    marsScrape_df.columns = ['Measurement','Value']
    marsScrape_df = marsScrape_df.set_index('Measurement')

    # Convert dataframe into a table and make some minor adjustments to smooth out html integration.
    mars_htmlTable = marsScrape_df.to_html()
    mars_htmlTable = mars_htmlTable.replace("\n","")
    mars_htmlTable = mars_htmlTable.replace("right","left")

    # EXPORT
    mars_data["mars_htmlTable"] = mars_htmlTable
    ### SECTION 4 - END


    ### SECTION 5 - START
    urlHemisphere = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    response = requests.get(urlHemisphere)
    soup = BeautifulSoup(response.text, "html.parser")

    scrape = soup.find_all('div', class_="item")

    path = []

    # Iterate through the variable scrape that contains BS4 scraped info.
    # Iterated action: for the value within the <a> tag and href section, append into path array.
    for i in scrape:
        path.append(i.a['href'])

    # Iterate through the path array and scrape each pathway into a variable called "soup".
    # Each iteration will extract the title and img url within the soup...
    # ...and then iterate into hemisphere_image_url array as a nested dictionary!

    hemisphere_image_urls = []
    urlHemi = "https://astrogeology.usgs.gov"

    for i in path:
        response = requests.get(f"{urlHemi}{i}")
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find('h2', class_='title').text.split("Enhanced")[0]
        img_url = soup.find_all('li')[1].a['href']
        img_url = img_url+"/full.jpg"
        hemisphere_image_urls.append({"title":title,"img_url":img_url})

    # EXPORT
    mars_data["hemisphere_image_urls"] = hemisphere_image_urls
    ### SECTION 5 - END

    return mars_data