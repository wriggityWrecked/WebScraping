"""KNL Spider implementation.

Example:
    $ scrapy runspider total_wine_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import constants
from random import randint


class TotalWineSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Total Wine (beer).
    """

    name = "totalWineSpider"
    download_delay = randint(2, 6)
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }


    def start_requests(self):

        urls = [
            'http://www.totalwine.com/beer/c/c0010?storename=1117,1115,1120&viewall=true&page=1&pagesize=200&tab=aty_isp&sort=name-asc' # url for all beer
        ]

        logging.getLogger(__name__)

        for url in urls:
            logging.info(
                '================================================================')
            logging.info('scraping ' + url)
            logging.info(
                '================================================================')

            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)


    def parse(self, response):

        logging.getLogger(__name__)

        # grab each entry listed
        if response is not None:

            for beer in response.css('div.plp-product-content-wrapper'):

                if beer is not None:

                    beer_item = beer.css('h2.plp-product-title')
                    beer_stock = beer.css('div.plp-product-buy-options').css('input').extract()[0].lower()

                    if 'instock=true' not in beer_stock:
                        continue #not in stock so keep iterating....

                    # id used for hashmap
                    id_ = beer_item.xpath('./a/@href').extract()[0]

                    start_index = id_.index('/p/') + 3
                    end_index = id_.index('?', start_index)

                    id_ = id_[start_index:end_index]

                    # grab the long name
                    beer_name = beer_item.xpath('./a/text()').extract()

                    # cleanup for json storage
                    id_ = ''.join(id_).strip()

                    beer_name = ''.join(beer_name).strip()

                    yield {
                        constants.NAME_KEY: beer_name,
                        constants.ID_KEY: int(id_)
                    }

        # https://stackoverflow.com/questions/18810850/scrapy-next-button-uses-javascript

        # check if the next button exists
        next_page_button = response.css('a.pager-next')

        if next_page_button is None or not next_page_button or len(next_page_button) == 0:
            next_page = None
        else:
            #get the current page number from the url
            page_start = response.url.index('page=')
            page_end = response.url.index('&', page_start)
            page_number = int(response.url[page_start+5:page_end]) + 1 #next page

            next_page = response.url[0:page_start+5] + str(page_number) + response.url[page_end:]

        if next_page is not None:
            next_page = response.urljoin(next_page)
            logging.info(
                '================================================================')
            logging.info('scraping ' + str(next_page))
            logging.info(
                '================================================================')
            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)
