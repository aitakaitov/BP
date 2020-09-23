# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from const import Const

# pro operace s html
from bs4 import BeautifulSoup

import time


# inicializace selenia
def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=Const.chromedriver_path, options=chrome_options)
    url = "https://o.seznam.cz/ochrana-udaju/"
    max_depth = 2
    scrape_page(driver, url, max_depth)


# zakladni mechanismus nacteni cele stranky a jejiho stazeni
def scrape_page(driver, url, max_depth, current_depth=0, append_file_path=None):
    driver.get(url)
    current_depth += 1

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    htmltext = driver.page_source

    if append_file_path is None:
        append_file_path = "".join(c for c in url if c.isalnum())
        file = open(append_file_path + ".txt", "w", encoding="utf-8")
        file.write("URL: " + url + "\n")
        file.write(htmltext)
        file.close()
    else:
        file = open(append_file_path + ".txt", "a", encoding="utf-8")
        file.write("\nURL: " + url + "\n")
        file.write(htmltext)
        file.close()

    if current_depth == max_depth:
        return
    else:
        soup = BeautifulSoup(htmltext)
        links = soup.find_all('a')
        links = filter_links(links, url)

        scraped_urls = []
        for link in links:
            if link.get("href") not in scraped_urls:
                scrape_page(driver, link.get("href"), max_depth, current_depth, append_file_path)
                scraped_urls.append(link.get("href"))
        return


# provadi filtrovani odkazu na zaklade klicovych slov
def filter_links(links, current_url) -> list:
    relevant_links = []
    for link in links:
        if "mailto" in link.get("href") or current_url in link.get("href"):
            continue
        if any(keyword in link.get("href") for keyword in Const.link_keywords) or any(keyword in link.contents[0] for keyword in Const.link_keywords):
            relevant_links.append(link)

    return relevant_links


main()
