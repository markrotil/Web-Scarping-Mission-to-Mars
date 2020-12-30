# Import Dependencies

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import time
# browser = Browser()

def init_browser():
    # Create a path to use for splinter
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():

    browser = init_browser()

    # Create shortcut for URL of main page
    url = 'https://mars.nasa.gov/news/'

    # Get response of web page
    response = requests.get(url)

    # html parser with beautiful soup
    soup = bs(response.text, 'html.parser')

    # check to see if it parses
    print(soup.prettify())

    # locates most recent articel title

    title = soup.find("div", class_="content_title").text
    print(title)

    # Locates the paragraph within the most recent story
    paragraph = soup.find("div", class_="rollover_description_inner").text
    print(paragraph)

    time.sleep(2)

    # Visit's the website below in the new browser
    browser.visit(
        'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

    # Manually clicks the link in the browser
    browser.click_link_by_id('full_image')

    # manually clicks the "more info" link
    browser.click_link_by_partial_text('more info')

    # html parser
    html = browser.html
    soup = bs(html, "html.parser")

    image = soup.select_one('figure.lede a img').get('src')
    image

    main_url = "https://www.jpl.nasa.gov"
    featured_image_url = main_url+image
    featured_image_url

    time.sleep(2)

    # Use Pandas to scrape data
    tables = pd.read_html('https://space-facts.com/mars/')
    tables

    # Creates a dataframe from the list that is "tables"
    mars_df = pd.DataFrame(tables[0])
    # Changes the name of the columns
    mars_df.rename(columns={0: "Information", 1: "Values"})

    # Transforms dataframe so it is readible in html
    mars_html_table = [mars_df.to_html(
        classes='data_table', index=False, header=False, border=0)]
    mars_html_table

    time.sleep(2)

    # Visits the website below
    browser.visit(
        'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')

    # html and parser
    html = browser.html
    soup = bs(html, 'html.parser')

    # Creates an empty list that will contian the names of the hemispheres
    hemi_names = []

    # Search for the names of all four hemispheres
    results = soup.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')

    # Get text and store in list
    for name in hemispheres:
        hemi_names.append(name.text)

    hemi_names

    # Search for thumbnail links
    thumbnail_results = results[0].find_all('a')
    thumbnail_links = []

    for thumbnail in thumbnail_results:

        # If the thumbnail element has an image...
        if (thumbnail.img):

            # then grab the attached link
            thumbnail_url = 'https://astrogeology.usgs.gov/' + \
                thumbnail['href']

            # Append list with links
            thumbnail_links.append(thumbnail_url)

    thumbnail_links

    full_imgs = []

    for url in thumbnail_links:

        # Click through each thumbanil link
        browser.visit(url)

        html = browser.html
        soup = bs(html, 'html.parser')

        # Scrape each page for the relative image path
        results = soup.find_all('img', class_='wide-image')
        relative_img_path = results[0]['src']

        # Combine the reltaive image path to get the full url
        img_link = 'https://astrogeology.usgs.gov/' + relative_img_path

        # Add full image links to a list
        full_imgs.append(img_link)

    full_imgs

    # Zip together the list of hemisphere names and hemisphere image links
    mars_hemi_zip = zip(hemi_names, full_imgs)

    hemisphere_image_urls = []

    # Iterate through the zipped object
    for title, img in mars_hemi_zip:

        mars_hemi_dict = {}

        # Add hemisphere title to dictionary
        mars_hemi_dict['title'] = title

        # Add image url to dictionary
        mars_hemi_dict['img_url'] = img

        # Append the list with dictionaries
        hemisphere_image_urls.append(mars_hemi_dict)

    hemisphere_image_urls

    time.sleep(2)

    mars_data: {"Title": title,
              "Paragraph": paragraph,
              "Image": image,
              "Table": mars_html_table,
              "hemispheres": hemisphere_image_urls
              }

    browser.quit()

    return mars_data
