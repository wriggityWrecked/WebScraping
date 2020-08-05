"""Suarez Spider implementation.

Example:
    $ scrapy runspider suarez_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import json
import hashlib

class SuarezSpider(scrapy.Spider):

    name = "suarezSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'TELNETCONSOLE_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }
    EXTENSIONS = {
        'scrapy.telnet.TelnetConsole': None
    }

    def start_requests(self):

        urls = [
            'https://www.suareztogo.com/app/store/api/v8/editor/users/131233472/sites/757498984233357138/products?per_page=200'
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
                name = '*' + item['name'] + '* '
                short_description = ''

                if item['short_description'] is not None:
                    short_description = item['short_description']

                link = ''
                if item['site_link'] is not None:
                    link = 'https://www.suareztogo.com/' + item['site_link']

                name = name + ':\n' + short_description + '\n' + link + '\n'
                item['visibility_tl']

                if item['inventory']['enabled'] == False or 'visibility_tl' not in item:
                    name = '*_(NOT ENABLED / PRE RELEASE)_*: ' + name
                elif item['inventory']['total'] <= 0:
                    name = '*_(SOLD OUT)_*: ' + name

                yield {
                    'name': name,
                    'id': hashlib.md5(name.encode('utf-8')).hexdigest(), # don't use this, hash won't change if back in stock: item['id'],
                    'link': item['site_link'],
                }
