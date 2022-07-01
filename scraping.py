import sys
sys.path.append("c:\\users\\lt\\anaconda3\\envs\\pythondata\\lib\\site-packages")
from splinter import Browser
from bs4 import BeautifulSoup as Soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
  executable_path = {'executable_path': ChromeDriverManager().install()}
  browser = Browser('chrome', **executable_path, headless=False)

  news_title, news_paragraph = mars_news(browser)

  # Run all scraping functions and store results in dictionary
  data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hem_imgs()
  }

  # Stop webdriver and return data
  browser.quit()
  return data

def mars_news(browser):

  # Visit the mars nasa news site
  url = 'https://redplanetscience.com'
  browser.visit(url)

  # Optional delay for loading the page
  browser.is_element_present_by_css('div.list_text', wait_time=1)

  html = browser.html
  news_soup = Soup(html, 'html.parser')
  slide_elem = news_soup.select_one('div.list_text')

  # Add try/except for error handling
  try:
    slide_elem.find('div', class_='content_title')
    # Use the parent element to find the first `a` tag and save it as `news_title`
    news_title = slide_elem.find('div', class_='content_title').get_text()
    news_title

    # Use the parent element to find the paragraph text
    news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    news_p
  except AttributeError:
    return None, None

  return news_title, news_p

def featured_image(browser):
  # Visit URL
  url = 'https://spaceimages-mars.com'
  browser.visit(url)

  # Find and click the full image button
  full_image_elem = browser.find_by_tag('button')[1]
  full_image_elem.click()

  # Parse the resulting html with soup
  html = browser.html
  img_soup = Soup(html, 'html.parser')

  try:
    # Find the relative image url
    img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
  except AttributeError:
    return None
  
  # Use the base URL to create an absolute URL
  img_url = f'https://spaceimages-mars.com/{img_url_rel}'

  return img_url

def mars_facts():
  try:
    df = pd.read_html('https://galaxyfacts-mars.com')[0]
  except BaseException:
    return None

  df.columns=['description', 'Mars', 'Earth']
  df.set_index('description', inplace=True)
  # facts_html = df.to_html(classes = "table table-striped")
  # fsoup = Soup(facts_html, 'html.parser')
  # fsoup.find(class_="dataframe")['class'] = 'table table-striped'  
  # return str(fsoup)
  return df.to_html(classes = 'table table-striped', border = 0)

def hem_imgs():
  executable_path = {'executable_path': ChromeDriverManager().install()}
  browser = Browser('chrome', **executable_path, headless=False)
  
  url = 'https://marshemispheres.com/'

  browser.visit(url)
  browser.is_element_present_by_css('div.list_text', wait_time=1)

  # 2. Create a list to hold the images and titles.
  hemisphere_image_urls = []

  # 3. Write code to retrieve the image urls and titles for each hemisphere.
  # Parse the resulting html with soup
  soup = Soup(browser.html, 'html.parser')
  results = soup.find_all('h3')[:-1]
  for result in results:
    page_with_jpg_url = f"{url}{result.text.split()[0].lower()}.html"
    browser.visit(page_with_jpg_url)
    browser.is_element_present_by_css('div.list_text', wait_time=1)
    soup = Soup(browser.html, 'html.parser')
    img_url_rel = soup.find(class_='downloads').find("ul").find('li').find('a').get('href')
    img_url = url + img_url_rel
    # print(img_url)
    hemisphere_image_urls.append({'img_url': img_url, 'title': result.text})
  return hemisphere_image_urls

if __name__ == "__main__":
  # If running as script, print scraped data
  print(scrape_all())
