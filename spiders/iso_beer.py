"""Suarez Spider implementation.

Example:
    $ scrapy runspider suarez_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class IsoBeer(scrapy.Spider):

    name = "isoBeer"
    download_delay = 0
    start_urls = [
        'https://isobeersstore.ecwid.com/Sour-Beers-c51385628',
        'https://isobeersstore.ecwid.com/'
    ]
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

    # def start_requests(self):
    #
    #     urls = [
    #         'https://isobeersstore.ecwid.com/Sour-Beers-c51385628',
    #         'https://isobeersstore.ecwid.com/'
    #     ]
    #
    #     logging.getLogger(__name__)
    #
    #     for url in urls:
    #         # logging.info(
    #         #     '================================================================')
    #         # logging.info('scraping ' + url)
    #         # logging.info(
    #         #     '================================================================')
    #
    #         yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):

        logging.getLogger(__name__)

        # grab each entry listed
        if response is not None:
            items = response.css('div.grid-product')

            for item in items:

                link = item.css('a.grid-product__title').xpath('@href').extract()[0]
                name = item.css('div.grid-product__title-inner::text').extract()[0]

                name = name + " " + link
                for span in item.xpath('.//div[@class="label__text"]/text()'):
                    if 'Sold out' == span.extract():
                        name = "*(SOLD OUT)* " + name

                yield {
                    'name': name,
                    'id': hashlib.md5(name.encode('utf-8')).hexdigest(), # don't use this, hash won't change if back in stock: item['id'],
                }
