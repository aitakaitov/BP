# selenium
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import JavascriptException

# constants
from const import Const

# static methods
from library_methods import LibraryMethods
from log import Log
from persistent_list import PersistentList

# html parsing
from bs4 import BeautifulSoup
import urllib.parse

import os
import re
import traceback
import shutil
import random


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
        self.driver = webdriver.Firefox(executable_path=Const.chromedriver_path, options=chrome_options)
        ''' Page load timeout'''
        self.driver.set_page_load_timeout(Const.webdriver_timeout)
        ''' Scraped links'''
        self.scraped_links = PersistentList(Const.scraped_filename)
        if len(self.scraped_links) == 0:
            self.scraped_links.append("--------------------------------------")
        ''' List of links to visit '''
        self.links_to_visit = PersistentList(Const.queue_filename)
        if len(self.links_to_visit) == 0:
            self.links_to_visit.append("--------------------------------------")
        ''' List of visited links '''
        self.visited_links = PersistentList(Const.visited_filename)
        if len(self.visited_links) == 0:
            self.visited_links.append("--------------------------------------")

        try:
            os.mkdir("./" + Const.pages_path)
        except OSError:
            self.log.log("[CRAWLER] Pages directory already exists.")

        self.no_links_file = open(Const.no_links_filename, "a")

        self.no_terms_file = open(Const.no_terms_filename, "a")

        self.no_cookies_file = open(Const.no_cookies_filename, "a")

    def start_crawler(self, start_url: str):
        """
        Starts the crawler from a starting url. The crawler will collect all usable links and then place then in a queue,
        collecting more links as it goes.
        :param start_url: Starting point
        :return:
        """

        try:
            self.crawl_page(start_url)
        except (WebDriverException, JavascriptException):
            self.log.log("[CRAWLER] Error loading starting page, will exit.")
            return

        # remove the placeholders
        if self.links_to_visit[0] == "--------------------------------------":
            self.links_to_visit.remove(self.links_to_visit[0])
        if self.scraped_links[0] == "--------------------------------------":
            self.scraped_links.remove(self.scraped_links[0])
        if len(self.visited_links) > 1 and self.visited_links[0] == "--------------------------------------":
            self.visited_links.remove(self.visited_links[0])

        while True:

            if len(self.links_to_visit) == 0:
                self.log.log("[CRAWLER] No more pages to visit, exiting.")
                self.driver.quit()
                return

            link = self.links_to_visit[0]
            self.links_to_visit.remove(self.links_to_visit[0])
            try:
                self.crawl_page(link)
            except (WebDriverException, JavascriptException):
                traceback.print_exc()
                self.log.log("[CRAWLER] Error loading page {}, skipping.".format(link))

    def crawl_page(self, url: str):
        """
        Crawls a page. Loads and downloads the page code. Extracts all links, adds links to the queue, extracts cookies
        and terms links. Creates folder for the page.
        :param url: Page url
        :return:
        """
        self.driver.delete_all_cookies()

        # acquire html
        htmltext = LibraryMethods.download_page_html(self.driver, url)
        #if LibraryMethods.strip_url(self.driver.current_url)[-3:] != ".cz":
        #    self.log.log("[CRAWLER] Redirected to non-.cz domain, skipping.")
        #    return

        self.log.log("[CRAWLER - NEW PAGE] Crawling page " + self.driver.current_url)

        self.visited_links.append(self.driver.current_url)

        # parse the html
        soup = BeautifulSoup(htmltext, features="html.parser")

        # find all links
        links = soup.find_all('a')
        links_before = len(self.links_to_visit)

        # add links to links_to_visit
        self.collect_links_to_visit(links, self.driver.current_url)

        if any(visited == LibraryMethods.strip_url(url) for visited in self.scraped_links):
            self.log.log("[CRAWLER] Domain already scraped, collected {} links-to-visit.".format(len(self.links_to_visit) - links_before))
            return

        terms_links, cookies_links = self.collect_terms_cookies_links(links, self.driver.current_url)

        if len(cookies_links) == 0 and len(terms_links) == 0:
            self.log.log("[CRAWLER] Collected no terms or cookies links, {} will be skipped.".format(url))
            self.no_links_file.write(url + "\n")
            #self.no_links_file.write(LibraryMethods.strip_url(url) + "\n")
            self.no_links_file.flush()
            return
        elif len(cookies_links) == 0 and len(terms_links) != 0:
            self.no_cookies_file.write(url + "\n")
            self.no_cookies_file.flush()
        elif len(cookies_links) != 0 and len(terms_links) == 0:
            self.no_terms_file.write(url + "\n")
            self.no_terms_file.flush()

        folder_name = re.sub("[^0-9a-zA-Z]+", "_", LibraryMethods.strip_url(self.driver.current_url))
        # create a folder for our url
        try:
            os.mkdir(Const.pages_path + "/" + folder_name)
            os.mkdir(Const.pages_path + "/" + folder_name + "/cookies")
            os.mkdir(Const.pages_path + "/" + folder_name + "/terms")
            f = open(Const.pages_path + "/" + folder_name + "/url.txt", "w", encoding="utf-8")
            f.write(url)
            f.close()
        except OSError:
            self.log.log("[CRAWLER] Folder for page {} has already been created, skipping.".format(url))
            return

        self.log.log("[CRAWLER] Collected {} links-to-visit, {} terms links, {} cookies links".format(len(self.links_to_visit)-links_before, len(terms_links), len(cookies_links)))

        for link in cookies_links:
            try:
                self.scrape_page(link, Const.pages_path + "/" + folder_name, "cookies")
            except WebDriverException:
                self.log.log("[CRAWLER] Error loading page {}, skipping.".format(link))

        for link in terms_links:
            try:
                self.scrape_page(link, Const.pages_path + "/" + folder_name, "terms")
            except WebDriverException:
                self.log.log("[CRAWLER] Error loading page {}, skipping.".format(link))

        self.scraped_links.append(LibraryMethods.strip_url(url))

    def collect_links_to_visit(self, links: list, current_url_full):
        """
        Finds valid links we havent visited yet and are not in the to-visit queue and adds them to the to-visit queue
        :param links: Links to filter
        """
        self.log.log("[CRAWLER] Collecting links-to-visit.")
        relevant_links = []
        current_url_stripped = LibraryMethods.strip_url(current_url_full)
        for link in links:
            link_href = link.get("href")
            try:
                # ignore emails, anything that contains an already visited domain, links we are going to visit and
                # anything that does not start with a letter or number
                # we limit the search to .cz domains
                if "mailto" not in link_href and link_href[0] != "#":
                    if link_href[0:2] == "//":
                        link_href = "http:" + link_href
                    link_href = urllib.parse.urljoin(current_url_full, link_href)
                    if link_href[-1] != "/":
                        link_href += "/"
                    if ".cz" == current_url_stripped[-3:] and all(extension not in link_href[-4:] for extension in Const.blacklisted_extensions):
                        if all(to_visit != link_href for to_visit in self.links_to_visit):
                            if all(visited != link_href for visited in self.visited_links):
                                relevant_links.append(link_href)
            except (TypeError, IndexError):
                # type error means we got an irregular structure from bs4 and we will ignore it
                # index error means that href is empty and we will ignore it
                continue
        relevant_links = list(set(relevant_links))
        [self.links_to_visit.append(link) for link in relevant_links]
        self.log.log("[CRAWLER] Collected {} links-to-visit out of {} available links on page.".format(len(relevant_links), len(links)))

    def collect_links_to_visit_alt(self, links: list, current_url_full: str):
        """
        Finds valid links we havent visited yet and are not in the to-visit queue and adds them to the to-visit queue
        Uses an alternative algorithm to prevent selecting too many links pointing to the same domain
        :param links: Links to filter
        """
        self.log.log("[CRAWLER] Collecting links-to-visit.")
        relevant_links = []
        same_domain_links = []
        current_url_stripped = LibraryMethods.strip_url(current_url_full)
        for link in links:
            link_href = link.get("href")
            try:
                # ignore emails, anything that contains an already visited domain, links we are going to visit and
                # anything that does not start with a letter or number
                # we limit the search to .cz domains
                if "mailto" not in link_href and link_href[0] != "#":
                    if link_href[0:2] == "//":
                        link_href = "http:" + link_href
                    link_href = urllib.parse.urljoin(current_url_full, link_href)
                    if link_href[-1] != "/":
                        link_href += "/"
                    if ".cz" == current_url_stripped[-3:] and all(
                            extension not in link_href[-4:] for extension in Const.blacklisted_extensions):
                        if all(to_visit != link_href for to_visit in self.links_to_visit):
                            if all(visited != link_href for visited in self.visited_links):
                                if current_url_stripped == LibraryMethods.strip_url(link_href):     # if the domain is the same one we are scraping
                                    same_domain_links.append(link_href)
                                else:
                                    relevant_links.append(link_href)
            except (TypeError, IndexError):
                # type error means we got an irregular structure from bs4 and we will ignore it
                # index error means that href is empty and we will ignore it
                continue

        same_domain_links = list(set(same_domain_links))        # select links to add at random
        for i in range(Const.domain_links_coll):
            r = random.randrange(0, len(same_domain_links))
            relevant_links.append(same_domain_links[r])
            same_domain_links.remove(same_domain_links[r])

        relevant_links = list(set(relevant_links))                      # then add the selected + ones pointing to other domains to to_visit
        [self.links_to_visit.append(link) for link in relevant_links]
        self.log.log(
            "[CRAWLER] Collected {} links-to-visit out of {} available links on page.".format(len(relevant_links),
                                                                                              len(links)))

    def collect_terms_cookies_links(self, links: list, current_url_full) -> tuple:
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
                if link_href[0] == '#':
                    continue

                if link_href[0:2] == "//":
                    link_href = "http:" + link_href

                link_href = urllib.parse.urljoin(current_url_full, link_href)
            except (TypeError, IndexError):
                # in case href is empty or not there at all
                continue
            try:
                # test for cookies keywords in URL
                if any(keyword in link_href.lower() for keyword in Const.cookies_keywords):
                    cookies_links.append(link_href)
                    continue
                # test for cookies keywords in link text
                elif any(keyword in link.contents[0].lower() for keyword in Const.cookies_keywords):
                    cookies_links.append(link_href)
                    continue
            except (IndexError, TypeError):
                # in case link has no contents
                continue
            try:
                # do the same for terms
                if any(keyword in link_href.lower() for keyword in Const.terms_keywords):
                    terms_links.append(link_href)
                elif any(keyword in link.contents[0].lower() for keyword in Const.terms_keywords):
                    terms_links.append(link_href)
            except (IndexError, TypeError):
                continue

        return list(set(terms_links)), list(set(cookies_links))

    def scrape_page(self, url: str, dir_path: str, page_type: str, current_depth = 1):
        """
        Downloads HTML of a web page, can recursively download pages from links
        :param url: URL to scrape
        :param dir_path: path to directory, where the scraped page will be saved
        :param page_type: "terms" or "cookies"
        :param current_depth: how deep the current page is
        :return: None
        """
        self.log.log("[CRAWLER] Scraping page {} as a {} page with current depth {}.".format(url, page_type, current_depth))
        self.visited_links.append(url)

        html_text = LibraryMethods.download_page_html(self.driver, url)

        soup = BeautifulSoup(html_text, features="html.parser")
        # filtrovani tagu
        LibraryMethods.filter_html(soup)
        # ziskani textu bez tagu
        htmltext = soup.get_text()

        file_name = re.sub("[^0-9a-zA-Z]+", "_", url)
        if len(file_name) > Const.max_filename_length:
            file_name = file_name[:Const.max_filename_length]
        file = open(dir_path + "/" + page_type + "/" + file_name, "w", encoding="utf-8")
        file.write("URL: " + url + "\n" + "DEPTH: " + str(current_depth) + "\n")
        file.write(htmltext)
        file.close()

        if current_depth == Const.max_depth:
            return
        else:
            current_depth += 1
            links = soup.find_all('a')
            terms_links, cookies_links = self.collect_terms_cookies_links(links, LibraryMethods.strip_url(url))
            if page_type == "cookies":
                for link in cookies_links:
                    if link != url:
                        self.scrape_page(link, dir_path, page_type, current_depth)
            elif page_type == "terms":
                for link in terms_links:
                    if link != url:
                        self.scrape_page(link, dir_path, page_type, current_depth)

        return
