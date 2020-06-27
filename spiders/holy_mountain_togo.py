"""HolyMountainToGo Spider implementation.

Example:
    $ scrapy runspider holy_mountain_togo.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class HolyMountainToGo(scrapy.Spider):

    name = "HolyMountainToGo"
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
            'https://togo.holymountainbrewing.com/app/store/api/v8/editor/users/131538033/sites/790861313732442182/products?per_page=100'
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
                    short_description = item['short_description'].replace('<br />', ', ')

                link = ''
                if item['site_link'] is not None:
                    link = 'https://togo.holymountainbrewing.com/' + item['site_link']

                name = name + ': ' + short_description + ': ' + link
                if item['inventory']['total'] <= 0:
                    name = '*(SOLD OUT)* ' + name

                yield {
                    'name': name.encode('utf-8'),
                    'id': hashlib.md5(name.encode('utf-8')).hexdigest(),
                }
