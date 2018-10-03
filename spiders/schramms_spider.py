"""Schramms Spider implementation.

Example:
    $ scrapy runspider schramms_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import random
import constants
import hashlib

class SchrammsSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Schramms.
    """

    name = "schrammsSpider"
    download_delay = random.randint(1,8)
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            'https://store.schrammsmead.com/mead-bottles-c6all.aspx'
        ]

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

            for item in response.css('div.nextTileProductWrapper'):

                if item is not None:
                    product = item.css('a.nextProdName')
                
                    if product is not None:

                        title = product.xpath('./@title').extract()[0]
                        link = product.xpath('./@href').extract()[0]
                        out_of_stock = item.css('div.nextSoldOut').xpath('./text()').extract()

                        if len(out_of_stock) > 1 and 'Sold Out' in out_of_stock[0]:
                            continue # skip, not in stock

                        yield {
                            constants.NAME_KEY: title,
                            constants.ID_KEY: hashlib.md5(title).hexdigest(),
                            constants.LINK_KEY: link
                        }
                        # todo next page

