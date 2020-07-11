"""Bottleworks Spider implementation.

Example:
    $ scrapy runspider bottleworks_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class BottleworksSpider(scrapy.Spider):

    name = "bottleworksSpider"
    download_delay = 0 # todo zero?
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay),
        'TELNETCONSOLE_ENABLED': 'false',
        'EXTENSIONS' : {
                'scrapy.extensions.telnet.TelnetConsole': None,
                'scrapy.extensions.corestats.CoreStats': None,
                'scrapy.extensions.memusage.MemoryUsage': None,
                'scrapy.extensions.logstats.LogStats': None,
        }
    }

    def start_requests(self):

        urls = [
            'https://www.bottleworks.com/shop/?orderby=date'
        ]

        logging.getLogger(__name__)

        for url in urls:
            # logging.info(
            #     '================================================================')
            # logging.info('scraping ' + url)
            # logging.info(
            #     '================================================================')

            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)

    def parse(self, response):

        logging.getLogger(__name__)

        # grab each entry listed
        if response is not None:

            list_items = response.xpath('//li')
            for list_item in list_items:

                items = list_item.css('a.ast-loop-product__link')

                in_stock = True
                # check if in stock
                stock = list_item.xpath('.//span[@class="ast-shop-product-out-of-stock"]/text()')
                if stock is not None:
                    stock_text = stock.extract()
                    if len(stock_text) > 0 and stock_text[0] == 'Out of stock':
                        in_stock = False

                for item in items:

                    link = item.xpath('./@href').extract()[0]
                    name = item.xpath('./h2/text()').extract()[0] + ": " + link

                    if not in_stock:
                        name = "*(SOLD OUT)* " + name
                    print(name)
                    yield {
                        'name': name,
                        'id': hashlib.md5(name.encode('utf-8')).hexdigest(),
                    }

            # get the next page
            next_link = response.xpath('.//a[@class="next page-numbers"]/@href').extract()
            if len(next_link) > 0:
                yield scrapy.Request(next_link[0], callback=self.parse, dont_filter=True)

