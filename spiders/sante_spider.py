"""Sante Spider implementation.

Example:
    $ scrapy runspider sante_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class SanteSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Holy Mountain.
    """

    name = "santeSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            'https://sante-adairius-rustic-ale.square.site/app/store/api/v5/editor/users/130333744/sites/289424801839818400/products'
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
                if item['inventory']['total'] <= 0:
                    name += ' (SOLD OUT)'

                yield {
                    'name': name,
                    'id': hashlib.md5(name).hexdigest(), # don't use this, hash won't change if back in stock: item['id'],
                    'link': item['site_link'],
                }
