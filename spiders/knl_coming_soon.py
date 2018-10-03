"""KNL Spider implementation.

Example:
    $ scrapy runspider knl_coming_soon.py -o output.json

"""

import datetime
import logging
import scrapy
import constants


class KnLComingSoonSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """

    name = "knlBeerSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            'https://www.klwines.com/Products/r?r=47+4294965539&d=1&t=&o=8&z=True', # url for beer coming soon
            'http://www.klwines.com/Products/r?r=47+4294967191&d=1&t=&o=8&z=True' # url for spirits coming soon
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

            for beer in response.css('div.result-desc'):

                if beer is not None:

                    # id used for hashmap
                    id_ = beer.xpath('./a/@href').extract()

                    # grab the long name
                    beer_name = beer.xpath('./a/text()').extract()

                    # cleanup for json storage
                    id_ = ''.join(id_).strip()
                    id_ = id_[7:]
                    beer_name = ''.join(beer_name).strip()

                    yield {
                        constants.NAME_KEY: beer_name,
                        constants.ID_KEY: int(id_)
                    }
