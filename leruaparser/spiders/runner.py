from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leruaparser.spiders.lerua import LeruaSpider
from leruaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    search = input('Ввеите критерий поиска ')
    process.crawl(LeruaSpider, search)
    process.start()

