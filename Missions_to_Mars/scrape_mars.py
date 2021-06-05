from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    # --- Visit Mars News site ---
    browser.visit('https://mars.nasa.gov/news/')

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Get the first news title
    titles = soup.find_all('div', class_='content_title')
    news_title = titles[0].text

    # Get the corresponding paragraph text
    paragraphs = soup.find_all('div', class_='article_teaser_body')
    news_paragraph= paragraphs[0].text


    
    # --- Visit JPL site for featured Mars image ---
    browser.visit('hhttps://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html')

    time.sleep(1)

    # Click through to full image
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(2)
    browser.click_link_by_partial_text('more info')

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')

    # Search for image source
    img = soup.find_all('img', class_='headerimage fade-in')
    source = soup.find('img', class_='headerimage fade-in').get('src')

    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
    feat_url = url + source


    # --- Use Pandas to scrape data ---
    tables = pd.read_html('https://space-facts.com/mars/')

    # Take second table for Mars facts
    mars_df = tables[1]
    
    # Convert table to html
    mars_facts = [mars_df.to_html(classes='data table table-borderless', index=False, header=False, border=0)]

    # --- Visit USGS Astrogeology Site ---
    browser.visit('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    
    time.sleep(1)
    


    # --- Search for Hemisphere titles --- 

    html = browser.html
    soup = bs(html, 'html.parser')

    hemispheres = []

    # Search for the names of all four hemispheres
    results = soup.find_all('div', class_="collapsible results")
    hemi_names = results[0].find_all('h3')

    # Get text and store in list
    for name in hemi_names:
        hemispheres.append(name.text)

    # Search for the names of all four hemispheres
    results = soup.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')

    # Get text and store in list
    for name in hemispheres:
        hemi_names.append(name.text)

    # Search for thumbnail links
    thumbnail_results = results[0].find_all('a')
    thumbnail_links = []

    for thumbnail in thumbnail_results:
    
    # If the thumbnail element has an image...
        if (thumbnail.img):
        
        # then grab the attached link
            thumbnail_url = 'https://astrogeology.usgs.gov/' + thumbnail['href']
        
        # Append list with links
            thumbnail_links.append(thumbnail_url)
        
        

    # --- Extract Image URLs ---

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
    

    # --- Zip together the list of hemisphere names and hemisphere image links ---
    mars_zip = zip(hemispheres, full_imgs)

    hemisphere_image_urls = []

    # Iterate through the zipped object
    for title, img in mars_zip:
    
        mars_hemi_dict = {}
    
    # Add hemisphere title to dictionary
        mars_hemi_dict['title'] = title
    
    # Add image url to dictionary
        mars_hemi_dict['img_url'] = img
    
    # Append the list with dictionaries
        hemisphere_image_urls.append(mars_hemi_dict)



    # --- Store data in a dictionary ---
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": full_imgs,
        "mars_facts": mars_facts,
        "hemispheres": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data