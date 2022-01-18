import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leruaparser.items import LeruaparserItem

class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&family=7f8ab360-4691-11ea-b7ce-8d83641e7e8e&suggest=true']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_goods)

    def parse_goods(self, response: HtmlResponse):

        loader = ItemLoader(item=LeruaparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//uc-pdp-price-view[@slot='primary-price']/span[@slot='price']/text()")
        loader.add_xpath('photos', "//source[@media =' only screen and (min-width: 1024px)']/@srcset")
        loader.add_xpath('_id', "//span[@slot='article']/@content")
        loader.add_value('url', response.url)
        yield loader.load_item()


