"""KNL Spirits Spider implementation.

Example:
    $ scrapy runspider knl_spirits_spider.py -o output.json

"""

import datetime
import logging
import scrapy

class KnLSpiritsSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """

    name = "knlSpiritsSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            #'http://www.klwines.com/Products/r?r=0+4294967191&d=1&t=&o=8&z=False'  # url for all spirits
            #'https://www.klwines.com/Spirits'
            'https://www.klwines.com/Products?&filters=-_x-_v%22p%22-_i%2230%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i%22Distilled+Spirits%22-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-30-Distilled+Spirits--%22-_q%22f%22-_i-_xx_-v_--_q-_v%22p%22-_i%2242%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-42-0--%22-_q%22f%22-_i-_xx_-v_-x_-&limit=500&offset=0&orderBy=&searchText='
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

                    #todo check inventory
                    yield {
                        'name': beer_name,
                        'id': int(id_)
                    }

        links = response.xpath(
            '//div[@class="floatLeft"]/a[contains(text(),"next")]/@href').extract()
        next_page = None

        if links:
            next_page = links[0]

        if next_page is not None:
            next_page = response.urljoin(next_page)
            logging.info(
                '================================================================')
            logging.info('scraping ' + str(next_page))
            logging.info(
                '================================================================')
            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

