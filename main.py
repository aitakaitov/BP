# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from const import Const

# pro hledani odkazu v html
from bs4 import BeautifulSoup

import time

# inicializace selenia
def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_exec_path = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chrome_exec_path, options=chrome_options)
    url = "https://o.seznam.cz/ochrana-udaju/"
    max_depth = 1
    scrape_page(driver, url, max_depth)


# zakladni mechanismus nacteni cele stranky a jejiho stazeni
def scrape_page(driver, url, max_depth, current_depth=0):
    driver.get(url)
    current_depth += 1

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    htmltext = driver.page_source
    file_name = "".join(c for c in url if c.isalnum())
    file = open(file_name + ".txt", "w", encoding="utf-8")
    file.write(htmltext)

    soup = BeautifulSoup(htmltext)
    links = soup.find_all('a')
    links = filter_links(links)

    if current_depth == max_depth:
        return
    else:
        return


# provadi filtrovani odkazu na zaklade klicovych slov
def filter_links(links) -> list:
    relevant_links = []
    for link in links:
        if "mailto" in link.get("href"):
            continue
        if any(keyword in link.get("href") for keyword in Const.link_keywords) or any(keyword in link.contents[0] for keyword in Const.link_keywords):
            relevant_links.append(link)

    return links


main()
