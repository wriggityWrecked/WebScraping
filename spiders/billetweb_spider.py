"""Billetweb Spider implementation.

Example:
    $ scrapy runspider billetweb_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import hashlib
import random


class BilletwebSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Cantillion.
    """

    name = "billetwebSpider"
    download_delay = random.randint(1, 8)
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            #'https://www.billetweb.fr/search.php?search=cantillon'
            #'https://www.billetweb.fr/multi_event.php?&user=13535&integrate=1'
            'https://www.billetweb.fr//multi_event.php?&multi=u13535'
            # iframe....https://stackoverflow.com/questions/24301376/can-scrapy-scrape-contents-of-iframe-using-scrapy-alone
        ]

        # random order....
        # random.shuffle(urls)

        logging.getLogger(__name__)

        for url in urls:
            logging.info(
                '================================================================')
            logging.info('scraping ' + url)
            logging.info(
                '================================================================')

            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)

    def parse(self, response):

        logging.getLogger(__name__)
        # grab each entry listed
        if response is not None:

            for item in response.xpath("//div[starts-with(@class,'multi_event_container multi_event_list')]"):
                name = item.xpath("./div[@class='multi_event_info']")\
                    .xpath("./div[@class='multi_event_info_text']").xpath("./div[@class='multi_event_name searchable']/text()").extract()
                link = item.xpath("./div[@class='multi_event_button']").xpath('./a/@href').extract()[0]

                if len(name) > 0:
                    name = name[0]

                if name == '' or name == '\n':
                    name = link[0]

                yield {
                    'name': name,
                    'id': link
                }


def hash_string(input):
    return hashlib.md5(input).hexdigest()
