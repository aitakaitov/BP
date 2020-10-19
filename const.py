class Const:
    """
    Contains constants
    """
    ''' Path to chromedriver executable '''
    chromedriver_path = "/home/vojtech/Desktop/BP/chromedriver"

    ''' Keywords that terms and conditions links would contain '''
    terms_keywords = ["podminky", "podmínky", "smluvni", "smluvní", "ochrana", "soukromi", "soukromí", "uzivani", "užívání", "osobni", "osobní", "terms", "conditions",
                    "policy", "privacy", "údaj", "zpracování", "udaj", "zpracovani"]

    ''' Keywords that cookies links would contain '''
    cookies_keywords = ["cookie"]

    ''' Timeout for page load '''
    webdriver_timeout = 10

    ''' Max link depth for scraping terms and cookies pages'''
    max_depth = 1

    log_path = "log.txt"

    max_scrolls = 10

    max_filename_length = 250

    start_url = "https://search.seznam.cz/?q=inurl%3Ah"
