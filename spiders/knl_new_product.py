"""KNL New Product Soon Spider implementation.

Example:
    $ scrapy runspider knl_new_product.py -o output.json

Big thanks to https://stackoverflow.com/questions/42947417/scrapy-extract-items-from-table

"""

import datetime
import logging
import scrapy
#import constants


class KnLNewProductSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """

    name = "knlNewProductSpider"
    download_delay = 0
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay),
        'LOG_ENABLED': False
    }

    def start_requests(self):

        urls = [
            'https://www.klwines.com/Products?&filters=sv2_NewProductFeedYN$eq$1$True$ProductFeed$!dflt-stock-all!203&limit=500&offset=0&orderBy=60%20asc,NewProductFeedDate%20desc&searchText=',
            'https://www.klwines.com/Products?&filters=sv2_NewProductFeedYN$eq$1$True$ProductFeed$!dflt-stock-all!206&limit=500&offset=0&orderBy=60%20asc,NewProductFeedDate%20desc&searchText='
        ]

        logging.getLogger(__name__)

        for url in urls:
            # logging.info(
            #     '================================================================')
            # logging.info('scraping ' + url)
            # logging.info(
            #     '================================================================')

            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)

    def parse(self, response):

        logging.getLogger(__name__)

        # grab each entry listed
        if response is not None:

            for item in response.xpath('//*[@class="table table-striped table-hover"]/tbody/tr'):
                                
                # check if in stock
                stock = item.xpath('td[6]//text()').extract_first()
   
                if 'Sold Out' not in stock:

                    id_ = item.xpath('td[2]//text()').extract_first()
                    name = item.xpath('td[4]//text()').extract_first()
                    # cleanup for json storage
                    id_ = ''.join(id_).strip()
                    name = ''.join(name).strip()
                    #todo GET INVENTORY

                    yield {
                        'name': name,
                        'id': id_
                    }
                    
            links = response.xpath(
                '//div[@class="floatLeft"]/a[contains(text(),"next")]/@href').extract()
            next_page = None

            if links:
                next_page = links[0]

            if next_page is not None:
                next_page = response.urljoin(next_page)
                # logging.info(
                #     '================================================================')
                # logging.info('scraping ' + str(next_page))
                # logging.info(
                #     '================================================================')
                yield scrapy.Request(next_page, callback=self.parse, dont_filter=False)





