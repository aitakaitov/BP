class Const:
    """
    Contains configuration
    """
    ''' Path to chromedriver executable '''
    chromedriver_path = "/home/vojtech/Desktop/BP-Current/chromedriver"

    ''' Keywords that terms and conditions links would contain '''
    terms_keywords = ["podminky", "podmínky", "podmínkami", "protection", "smluvni", "smluvní", "uzivani", "užívání", "terms", "conditions",
                    "policy"]

    ''' Keywords that cookies links would contain '''
    cookies_keywords = ["gdpr", "cookie", "privacy", "ochrana", "soukromi", "soukromí", "zpracovani", "zpracování", "zásady", "zasady", "udaju", "udaje", "údajů", "údaje"]

    ''' Timeout for page load '''
    webdriver_timeout = 20

    ''' Max link depth for scraping terms and cookies pages'''
    max_depth = 1

    ''' Path to log file '''
    log_path = "log.txt"

    '''Path to pages dir'''
    pages_path = "pages"

    '''Persistent to-visit queue name'''
    queue_filename = "inqueue.txt"

    '''Persistent visited list name'''
    visited_filename = "visited.txt"

    '''Persistent scraped list name'''
    scraped_filename = "scraped.txt"

    '''Path to file, where domains with no links will be stored'''
    no_links_filename = "nolinks.txt"

    '''Path to file, where domains with no terms will be stored'''
    no_terms_filename = "noterms.txt"

    '''Path to file, where domains with no cookies will be stored'''
    no_cookies_filename = "nocookies.txt"

    '''Path to persistent files dir'''
    persistent_path = "persistent"

    '''Maximum scrolls'''
    max_scrolls = 20

    '''Pause between scrolls'''
    scroll_pause = 0.2

    '''Maximum filename length'''
    max_filename_length = 250

    '''Starting url'''
    start_urls = ["http://seznam.cz",
                  "http://odkazy.seznam.cz/Cestovani/",
                  "https://odkazy.seznam.cz/Zpravodajstvi/Casopisy-e-ziny/",
                  "https://odkazy.seznam.cz/Kultura-a-umeni/Film/",
                  "https://odkazy.seznam.cz/Volny-cas-a-zabava/",
                  "https://odkazy.seznam.cz/Sport/",
                  "https://odkazy.seznam.cz/Veda-a-technika/"
                  "https://odkazy.seznam.cz/Lide-a-spolecnost/"
                  "https://odkazy.seznam.cz/Pocitace-a-internet/"
                  "https://www.firmy.cz/"]

    '''Extensions we ignore '''
    blacklisted_extensions = [".jpg", ".png", ".jpeg", ".pdf"]

    domain_links_coll = 40


