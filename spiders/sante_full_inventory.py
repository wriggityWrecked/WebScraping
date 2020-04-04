"""Sante Spider implementation.

Example:
    $ scrapy runspider sante_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class SanteFullInventorySpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Holy Mountain.
    """

    name = "santeFullInventorySpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            'https://sante-adairius-rustic-ale.square.site/app/website/cms/api/v1/sites/5b03e2e0-5b39-11ea-92fc-4167e98f6d11/commerce-links'
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
            products = jsonresponse['products']

            for item in products.keys():
                name = products[item]['name']
                yield {
                    'name': name,
                    'id': item,
                }
