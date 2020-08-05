"""Side Project Spider implementation.

Example:
    $ scrapy runspider sideProjectSpider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class SideProjectSpider(scrapy.Spider):

    name = "sideProjectSpider"
    download_delay = 0
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
            'http://www.sideprojectbrewing.com/shop'
        ]

        logging.getLogger(__name__)

        for url in urls:
            # logging.info(
            #     '================================================================')
            # logging.info('scraping ' + url)
            # logging.info(
            #     '================================================================')

            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):

        logging.getLogger(__name__)

        # grab each entry listed
        if response is not None:

            for entry in response.xpath('//div[@id="productList"]//a'):

               link = str(entry.xpath('@href').extract()[0])
               link = 'https://www.sideprojectbrewing.com' + link

               for item in entry.css('div.product-overlay'): #response

                    beers = item.css('div.product-title')
                    for beer in beers:
                        name = beer.xpath('text()').extract_first() + ': ' + link

                        if entry.css('div.product-mark'):
                            name = '*(Sold Out)* ' + name


                        yield {
                            'name': name,
                            'id': hashlib.md5(name.encode('utf-8')).hexdigest(), # don't use this, hash won't change if back in stock: item['id'],
                        }
