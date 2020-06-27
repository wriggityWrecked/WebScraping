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

    name = "santeSpider"
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
            'https://sante-adairius-rustic-ale.square.site/app/store/api/v8/editor/users/130333744/sites/289424801839818400/products'
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
                short_description = ''

                if item['short_description'] is not None:
                    short_description = item['short_description'].replace('<br />', ', ').replace('Shipping via GSO within CALIFORNIA ONLY!, GSO will not deliver to PO Box\'s!, Please make sure your shipping address is entered correctly!, You should receive a tracking # from GSO when they take the package into their system. ', '')

                link = ''
                if item['site_link'] is not None:
                    link = 'https://www.rusticalesonline.com/' + item['site_link']

                name = name + ': ' + short_description + ': ' + link
                if item['inventory']['total'] <= 0:
                    name = '*(SOLD OUT)* ' + name

                yield {
                    'name': name,
                    'id': hashlib.md5(name.encode('utf-8')).hexdigest(), # don't use this, hash won't change if back in stock: item['id'],
                    'link': item['site_link'],
                }
