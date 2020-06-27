"""Sante Spider implementation.

Example:
    $ scrapy runspider good_karma_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class GoodKarmaSpider(scrapy.Spider):

    name = "goodKarmaSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }
    EXTENSIONS = {
        'scrapy.telnet.TelnetConsole': None
    }

    def start_requests(self):

        urls = [
            'https://goodkarmasj.revelup.com/weborders/products/?establishment=1&ignore_timetable=0'
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

            jsonresponse = json.loads(response.body_as_unicode())
            data = jsonresponse['data']

            for item in data:
                name = item['name']
                id = item['barcode']

                yield {
                    'name': name,
                    'id': id,
                }
