

import datetime
import logging
import scrapy
import json
import hashlib

class HolyWaterSpider(scrapy.Spider):

    name = "santeSpider"
    download_delay = 0
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
            'https://www.holywater2go.com/app/store/api/v13/editor/users/132480005/sites/705432645679784969/store-locations?page=1&per_page=100&include=address&lang=en'
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
                if 'name' in item:
                    name = item['name']

                    link = ''
                    if 'site_link' in item and item['site_link'] is not None:
                        link = 'https://https://www.holywater2go.com/' + item['site_link']

                    name = name + ': ' + price  + ': ' + link
                    if item['inventory']['total'] <= 0:
                        name = '*(SOLD OUT)* ' + name

                    yield {
                        'name': name,
                        'id': hashlib.md5(name.encode('utf-8')).hexdigest(), # don't use this, hash won't change if back in stock: item['id'],
                        'link': item['site_link'],
                    }
