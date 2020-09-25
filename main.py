# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from const import Const
from selenium.common.exceptions import WebDriverException

# pro operace s html
from bs4 import BeautifulSoup

import time


# inicializace selenia
def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=Const.chromedriver_path, options=chrome_options)
    driver.set_page_load_timeout(3)
    url = "https://o.seznam.cz/ochrana-udaju/"
    #url = "https://www.mafra.cz/o-spolecnosti.aspx?y=mafra_all/pouceni.htm&cat=pouceni"
    max_depth = 2
    scrape_page(driver, url, max_depth)


# zakladni mechanismus nacteni cele stranky a jejiho stazeni
def scrape_page(driver, url, max_depth, current_depth=0, append_file_path=None):
    # pro pripad timeoutu
    try:
        driver.get(url)
    except WebDriverException:
        print("Error loading " + url)

    current_depth += 1
    print("Scraping url " + url + " at depth " + current_depth.__str__())

    # zajistuje scrollovani
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # ziskame html
    htmltext = driver.page_source
    # parsujeme
    soup = BeautifulSoup(htmltext, features="html.parser")
    # filtrovani tagu
    filter_html(soup)
    # ziskani textu s tagy
    #htmltext = str(soup)
    # ziskani textu bez tagu
    htmltext = soup.get_text()

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
        links = soup.find_all('a')
        links = filter_links(links, url)

        scraped_urls = []
        for link in links:
            if link.get("href") not in scraped_urls:
                scrape_page(driver, link.get("href"), max_depth, current_depth, append_file_path)
                scraped_urls.append(link.get("href"))
        return


# odstranuje tagy a jejich obsah z html
def filter_html(soup):
    scripts = soup.find_all("script")
    for tag in scripts:
        tag.decompose()

    iframes = soup.find_all("iframe")
    for tag in iframes:
        tag.decompose()

    link_tags = soup.find_all("link")
    for tag in link_tags:
        tag.decompose()

    metas = soup.find_all("meta")
    for tag in metas:
        tag.decompose()

    styles = soup.find_all("style")
    for tag in styles:
        tag.decompose()


# provadi filtrovani odkazu na zaklade klicovych slov
def filter_links(links, current_url) -> list:
    relevant_links = []
    current_url = strip_url(current_url)
    for link in links:
        try:
            if "mailto" in link.get("href") or current_url in link.get("href") or link.get("href")[0] == "#":
                continue
            if any(keyword in link.get("href") for keyword in Const.link_keywords) or any(keyword in link.contents[0] for keyword in Const.link_keywords):
                relevant_links.append(link)
        except TypeError:
            continue

    return relevant_links


# ocisti url adresu od protokolu a get casti
def strip_url(url):
    index_qmark = url.find("?")
    index_http = url.find("http://")
    index_https = url.find("https://")

    if index_qmark >= 0:
        url = url[0:index_qmark]
    if index_https >= 0:
        url = url[8:len(url)]
    elif index_http >= 0:
        url = url[7:len(url)]

    return url


main()
