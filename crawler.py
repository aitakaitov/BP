# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# constants
from const import Const

# static methods
from library_methods import LibraryMethods
from log import Log

# html parsing
from bs4 import BeautifulSoup

import os
import re
import traceback
import shutil


class Crawler:
    """
        Crawls the web from a starting point, navigating trough all valid links, not visiting the same domain twice, and
        scraping cookies and terms for domains.
    """
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--enable-automation")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.headless = True
        self.log = Log(Const.log_path)

        ''' Selenium driver for chrome'''
        self.driver = webdriver.Chrome(executable_path=Const.chromedriver_path, options=chrome_options)
        ''' Page load timeout'''
        self.driver.set_page_load_timeout(Const.webdriver_timeout)
        ''' Already visited and processed links (mainly domains)'''
        self.visited_links = ["--------------------------------------"]
        ''' List of links to visit '''
        self.links_to_visit = ["--------------------------------------"]
        ''' List of already scraped links '''
        self.scraped_terms_cookies = ["--------------------------------------"]
        ''' List of links, that wont be added to the visited_links as domains but as links
            This is done because we dont want to visit the same domain twice, as it will have
            the same cookies policy, but there are some domains we want to visit more than once
            like search results '''
        self.whitelisted_domains = []

    def start_crawler(self, start_url: str):
        """
        Starts the crawler from a starting url. The crawler will collect all usable links and then place then in a queue,
        collecting more links as it goes.
        :param start_url: Starting point
        :return:
        """

        # We add the starting point to the whitelist, so we can visit the domain again
        # (for example our starting point could be search results, and we can go to the nex page)
        self.whitelisted_domains.append(LibraryMethods.strip_url(start_url))

        try:
            self.crawl_page(start_url)
        except WebDriverException:
            self.log.log("[CRAWLER] Error loading starting page, will exit.")
            return

        # remove the placeholders
        self.links_to_visit.remove(self.links_to_visit[0])
        self.visited_links.remove(self.visited_links[0])
        if len(self.scraped_terms_cookies) > 1:
            self.scraped_terms_cookies.remove(self.scraped_terms_cookies[0])

        while True:
            try:
                try:
                    link = self.links_to_visit[0]
                except IndexError:
                    self.log.log("[CRAWLER] No more pages to visit, exiting.")
                    return
                self.links_to_visit.remove(self.links_to_visit[0])
                # check if we have already visited the link or its domain
                if any(visited in LibraryMethods.strip_url(link) for visited in self.visited_links) and all(whitelisted not in LibraryMethods.strip_url(link) for whitelisted in self.whitelisted_domains):
                    self.log.log("[CRAWLER] Domain {} already visited, skipping.".format(LibraryMethods.strip_url(link)))
                    continue
                else:
                    self.crawl_page(link)
            except WebDriverException:
                traceback.print_exc()
                self.log.log("[CRAWLER] Error loading page {}, skipping.".format(link))
                self.links_to_visit.remove(self.links_to_visit[0])

    def crawl_page(self, url: str):
        """
        Crawls a page. Loads and downloads the page code. Extracts all links, adds links to the queue, extracts cookies
        and terms links. Creates folder for the page.
        :param url: Page url
        :return:
        """
        self.driver.delete_all_cookies()

        self.log.log("[CRAWLER - NEW PAGE] Crawling page " + url)

        # acquire html code
        htmltext = LibraryMethods.download_page_html(self.driver, url)

        folder_name = re.sub("[^0-9a-zA-Z]+", "_", self.driver.current_url)
        # create a folder for our url
        try:
            os.mkdir(folder_name)
            os.mkdir(folder_name + "/cookies")
            os.mkdir(folder_name + "/terms")
            f = open(folder_name + "/url.txt", "w", encoding="utf-8")
            f.write(url)
            f.close()
        except OSError:
            self.log.log("[CRAWLER] Folder for page {} has already been created, skipping.".format(url))
            return

        # if the domain is not whitelisted, we add it to visited_links, otherwise we add the link
        # by doing this, we can visit other pages of e.g. results, but wont visit the same results page again
        if all(wl_domain not in LibraryMethods.strip_url(url) for wl_domain in self.whitelisted_domains):
            self.visited_links.append(LibraryMethods.strip_url(url))
        else:
            self.visited_links.append(url)

        # parse the html
        soup = BeautifulSoup(htmltext, features="html.parser")

        # find all links
        links = soup.find_all('a')

        links_before = len(self.links_to_visit)
        # add links to links_to_visit
        self.collect_links_to_visit(links, LibraryMethods.strip_url(url))

        terms_links, cookies_links = self.collect_terms_cookies_links(links, LibraryMethods.strip_url(url))

        if len(cookies_links) == 0 and len(terms_links) == 0:
            self.log.log("[CRAWLER] Collected no terms or cookies links, {} will be skipped.".format(url))
            shutil.rmtree(folder_name)
            return

        self.log.log("[CRAWLER] Collected {} links-to-visit, {} terms links, {} cookies links".format(len(self.links_to_visit)-links_before, len(terms_links), len(cookies_links)))

        for link in cookies_links:
            self.scrape_page(link, folder_name, "cookies")

        for link in terms_links:
            self.scrape_page(link, folder_name, "terms")

    def collect_links_to_visit(self, links: list, current_url_stripped):
        """
        Finds valid links we havent visited yet and are not in the to-visit queue and adds them to the to-visit queue
        :param links: Links to filter
        """
        self.log.log("[CRAWLER] Collecting links-to-visit.")
        relevant_links = []
        for link in links:
            link_href = link.get("href")
            try:
                # ignore emails, anything that contains an already visited domain, links we are going to visit and
                # anything that does not start with a letter or number
                # we limit the search to .cz domains
                if "mailto" not in link_href:
                    if link_href[0:2] == "//":
                        link_href = "http:" + link_href
                    if link_href[0] == "/":
                        link_href = "http://" + current_url_stripped + link_href
                    if link_href[0:2] == "./":
                        link_href = "http://" + current_url_stripped + link_href[1:]
                    if ".cz" in link_href and link_href[0] != "#":
                        if all(visited not in link_href for visited in self.visited_links):
                            if all(to_visit not in link_href for to_visit in self.links_to_visit):
                                if all(scraped not in link_href for scraped in self.scraped_terms_cookies):
                                    relevant_links.append(link_href)
            except (TypeError, IndexError):
                # type error means we got an irregular structure from bs4 and we will ignore it
                # index error means that href is empty and we will ignore it
                continue
        relevant_links = list(set(relevant_links))
        self.log.log("[CRAWLER] Collected {} links-to-visit out of {} available links on page.".format(len(relevant_links), len(links)))
        [self.links_to_visit.append(link) for link in relevant_links]

    def collect_terms_cookies_links(self, links: list, current_url_stripped) -> tuple:
        """
        Finds links pointing to cookies and terms pages
        :param links: Links
        :return: Terms and cookies links
        """
        self.log.log("[CRAWLER] Collecting cookies and terms links.")
        cookies_links = []
        terms_links = []

        for link in links:
            link_href = link.get('href')
            try:
                # filter out invalid links
                if "mailto" in link_href:
                    continue
                if link_href[0:2] == "//":
                    link_href = "http:" + link_href
                if link_href[0] == "/":
                    link_href = "http://" + current_url_stripped + link_href
                if link_href[0:2] == "./":
                    link_href = "http://" + current_url_stripped + link_href[1:]
                if not link_href[0].isalnum():
                    continue
            except (TypeError, IndexError):
                # in case href is empty or not there at all
                continue
            try:
                # test for cookies keywords in URL
                if any(keyword in link_href for keyword in Const.cookies_keywords):
                    cookies_links.append(link_href)
                    continue
                # test for cookies keywords in link text
                elif any(keyword in link.contents[0] for keyword in Const.cookies_keywords):
                    cookies_links.append(link_href)
                    continue
            except IndexError:
                # in case link has no contents
                continue
            try:
                # do the same for terms
                if any(keyword in link_href for keyword in Const.terms_keywords):
                    terms_links.append(link_href)
                elif any(keyword in link.contents[0] for keyword in Const.terms_keywords):
                    terms_links.append(link_href)
            except IndexError:
                continue

        self.log.log("[CRAWLER] Collected {} terms links and {} cookies links.".format(len(terms_links), len(cookies_links)))
        return list(set(terms_links)), list(set(cookies_links))

    def scrape_page(self, url: str, dir_path: str, page_type: str, current_depth=0):
        """
        Downloads HTML of a web page, can recursively download pages from links
        :param url: URL to scrape
        :param dir_path: path to directory, where the scraped page will be saved
        :param page_type: "terms" or "cookies"
        :param current_depth: how deep the current page is
        :return: None
        """
        self.log.log("[CRAWLER] Scraping page {} as a {} page with current depth {}.".format(url, page_type, current_depth))
        self.scraped_terms_cookies.append(url)

        current_depth += 1

        try:
            html_text = LibraryMethods.download_page_html(self.driver, url)
        except WebDriverException:
            self.log.log("[CRAWLER] Error loading page, skipping.")
            return

        soup = BeautifulSoup(html_text, features="html.parser")
        # filtrovani tagu
        LibraryMethods.filter_html(soup)
        # ziskani textu bez tagu
        htmltext = soup.get_text()

        file_name = re.sub("[^0-9a-zA-Z]+", "_", url)
        if len(file_name) > Const.max_filename_length:
            file_name = file_name[:Const.max_filename_length]
        file = open(dir_path + "/" + page_type + "/" + file_name, "w", encoding="utf-8")
        file.write("SITE URL: " + url + "\n")
        file.write(htmltext)
        file.close()

        # TODO catch links pointing to this page
        if current_depth == Const.max_depth:
            return
        else:
            links = soup.find_all('a')
            terms_links, cookies_links = self.collect_terms_cookies_links(links)
            if page_type == "cookies":
                for link in cookies_links:
                    self.scrape_page(link, dir_path, page_type, current_depth)
            elif page_type == "terms":
                for link in terms_links:
                    self.scrape_page(link, dir_path, page_type, current_depth)

        return
