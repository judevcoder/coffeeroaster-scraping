import re
import scrapy

from lxml import html
from urllib.parse import urljoin
from scrapy.http import Request


class CoffeeRoasterItem(scrapy.Item):
    Name = scrapy.Field()
    Web_Address = scrapy.Field()
    Description = scrapy.Field()
    Social = scrapy.Field()
    Contact = scrapy.Field()


class CoffeeRoasterSpider(scrapy.Spider):

    name = 'coffeeroaster'

    allowed_domains = ["thecoffeeroasters.co.uk"]

    start_urls = ['https://thecoffeeroasters.co.uk/pages/a-big-list-of-coffee-roasters-in-uk']

    headers = {
        'Accept': '',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '',
        'Host': 'system.reins.jp',
        'Referer': 'https: // system.reins.jp / reins / ktgyoumu / KG001_001.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(CoffeeRoasterSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.current_page = 1
        self.next_page = True

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse_result)

    def parse_result(self, response):
        table = response.xpath('//div[contains(@class, "collection-list-items")]//table//tr').extract()
        next_page = response.xpath('//div[contains(@class, "grid-item body-large")][1]/a/@class').extract()[-1]
        if 'disabled' in next_page:
            self.next_page = False
        try:
            for item in table:
                name = html.fromstring(item).xpath('//tr/td[contains(@class, "body-large")]/text()')
                if name:
                    name = self._clean_text(name[0])
                web_address = html.fromstring(item).xpath('//tr/td[contains(@class, "body-large")]/a/@href')
                if web_address:
                    web_address = self._clean_text(web_address[0])
                if len(name) == 0:
                    name = self._clean_text(html.fromstring(item).xpath
                                     ('//tr/td[contains(@class, "body-large")]//h3/text()')[0])
                    web_address = urljoin(response.url, web_address)
                description = self._clean_text(' '.join(html.fromstring(item).xpath
                                                        ('//tr/td[contains(@class, "lh-12 body")]/text()')))
                if len(description) == 0:
                    description = self._clean_text(' '.join(html.fromstring(item).xpath
                                                            ('//tr/td[contains(@class, "lh-12 body")]/p/text()')))
                if len(description) == 0:
                    description = self._clean_text(' '.join(html.fromstring(item).xpath
                                                            ('//tr/td[contains(@class, "lh-12 body")]/span/text()')))

                result = CoffeeRoasterItem()
                result['Name'] = name
                result['Web_Address'] = web_address
                result['Description'] = description
                yield result
        except Exception as e:
            print(e)

        if self.next_page:
            self.current_page += 1
            next_url = self.start_urls[0] + '?page=' + str(self.current_page) + '#scroll-top'
            yield Request(
                url=next_url,
                callback=self.parse_result
            )
        else:
            return

    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)
