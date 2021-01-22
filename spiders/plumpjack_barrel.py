"""
Example:
    $ scrapy runspider knl_coming_soon.py -o output.json

Big thanks to https://stackoverflow.com/questions/42947417/scrapy-extract-items-from-table

"""

import datetime
import logging
import scrapy
import hashlib


class PlumpjackBarrelSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """
    name = "plumpjackBarrelSpider"
    download_delay = 0
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay),
        'TELNETCONSOLE_ENABLED': 'false',
        'REDIRECT_ENABLED': False,
        'RETRY_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'REACTOR_THREADPOOL_MAXSIZE': 20,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 40,
        'CONCURRENT_REQUESTS': 40,
        'EXTENSIONS': {
            'scrapy.extensions.telnet.TelnetConsole': None,
            'scrapy.extensions.corestats.CoreStats': None,
            'scrapy.extensions.memusage.MemoryUsage': None,
            'scrapy.extensions.logstats.LogStats': None,
        }
    }

    def start_requests(self):

        urls = [
            'https://plumpjackwines.com/collections/barrel-picks?sort_by=created-descending'
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

            for item in response.xpath('//div[contains(@class, "three")]'):
                name = item.css('div.info').css('span.title').xpath('text()').extract()

                if len(name) <= 0:
                    continue
                name = name[0]

                link = item.xpath('./a/@href').extract()[0]

                name = name + ': https://plumpjackwines.com/' + link

                price_info = item.css('div.info').css('span.price').css('span.sold_out').xpath('text()').extract()

                if len(price_info) > 0:
                    name = '*(SOLD OUT)* ' + name
                yield {
                    'name': name,
                    'id': hashlib.md5(name.encode('utf-8')).hexdigest(),
                }

            next_page = response.css('span.next').xpath('./a/@href').extract()

            if len(next_page) > 0:
                yield scrapy.Request('https://plumpjackwines.com/' + next_page[0], callback=self.parse, dont_filter=False)
