import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MoenItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MoenSpider(scrapy.Spider):
    name = 'moen'
    start_urls = ['https://moensbank.dk/om-moens-bank/nyheder?created=All&page=0']

    def parse(self, response):
        links = response.xpath('//p[@class="news-title"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_post)

        next_page = response.xpath('//li[@class="pager__item pager__item--next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_post(self, response):
        date = response.xpath('//span[@class="field-content news-date-page"]/text()').get()
        title = response.xpath('//h1//text()').get()
        content = response.xpath('(//div[@class="field field--name-body field--type-text-with-summary field--label-hidden field--item"])[position()=2]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "",' '.join(content))

        item = ItemLoader(item=MoenItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()
