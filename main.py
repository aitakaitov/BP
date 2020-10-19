from crawler import Crawler
from const import Const

def main():
    c = Crawler()
    c.start_crawler(Const.start_url)

main()