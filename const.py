class Const:
    """
    Contains constants
    """
    ''' Path to chromedriver executable '''
    chromedriver_path = "C:/Users/Vojtěch Bartička/Desktop/BP/BP/geckodriver.exe"

    ''' Keywords that terms and conditions links would contain '''
    terms_keywords = ["podminky", "podmínky", "podmínkami", "protection", "smluvni", "smluvní", "ochrana", "soukromi", "soukromí", "uzivani", "užívání", "osobní", "terms", "conditions",
                    "policy", "privacy", "údaj", "zpracování", "udaj", "zpracovani"]

    ''' Keywords that cookies links would contain '''
    cookies_keywords = ["cookie"]

    ''' Timeout for page load '''
    webdriver_timeout = 10

    ''' Max link depth for scraping terms and cookies pages'''
    max_depth = 1

    log_path = "log.txt"

    pages_path = "pages"

    queue_filename = "inqueue.txt"

    visited_filename = "visited.txt"

    scraped_filename = "scraped.txt"

    no_links_filename = "nolinks.txt"

    persistent_path = "persistent"

    max_scrolls = 10

    max_filename_length = 250

    start_url = "https://seznam.cz/"

    blacklisted_extensions = [".jpg", ".png"]
