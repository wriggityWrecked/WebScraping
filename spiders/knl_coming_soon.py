"""KNL Coming Soon Spider implementation.

Example:
    $ scrapy runspider knl_coming_soon.py -o output.json

Big thanks to https://stackoverflow.com/questions/42947417/scrapy-extract-items-from-table

"""

import datetime
import logging
import scrapy
#import constants


class KnLComingSoonSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """

    name = "knlBeerSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay),
        'LOG_ENABLED': False
    }

    def start_requests(self):

        urls = [
            'https://www.klwines.com/Products?&filters=-_x-_v%22p%22-_i%2247%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i1-_q%22vi%22-_itrue-_q%22t%22-_i%22coming-soon%22-_q%22f%22-_i-_x-_v%22l%22-_i%22and%22-_q%22f%22-_i-_v%22p%22-_i%2258%22-_q%22o%22-_i%22gt%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22%22-_q%22f%22-_i-_xx_-v_-v_--_q-_v%22l%22-_i%22and%22-_q%22f%22-_i-_v%22p%22-_i%2257%22-_q%22o%22-_i%22le%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22%22-_q%22f%22-_i-_xx_-v_-v_--_q-_v%22l%22-_i%22and%22-_q%22f%22-_i-_v%22p%22-_i%2248%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22%22-_q%22f%22-_i-_xx_-v_-v_-x_-v_--_q-_v%22t%22-_i%22dflt-stock-all%22v_--_q-_v%22p%22-_i%2230%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i%22Beer%22-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-30-Beer--%22-_q%22f%22-_i-_xx_-v_-x_-&limit=500&offset=0&orderBy=&searchText=',
            'https://www.klwines.com/Products?&filters=-_x-_v%22p%22-_i%2247%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i1-_q%22vi%22-_itrue-_q%22t%22-_i%22coming-soon%22-_q%22f%22-_i-_x-_v%22l%22-_i%22and%22-_q%22f%22-_i-_v%22p%22-_i%2258%22-_q%22o%22-_i%22gt%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22%22-_q%22f%22-_i-_xx_-v_-v_--_q-_v%22l%22-_i%22and%22-_q%22f%22-_i-_v%22p%22-_i%2257%22-_q%22o%22-_i%22le%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22%22-_q%22f%22-_i-_xx_-v_-v_--_q-_v%22l%22-_i%22and%22-_q%22f%22-_i-_v%22p%22-_i%2248%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22%22-_q%22f%22-_i-_xx_-v_-v_-x_-v_--_q-_v%22t%22-_i%22dflt-stock-all%22v_--_q-_v%22p%22-_i%2230%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i%22Distilled+Spirits%22-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-30-Distilled+Spirits--%22-_q%22f%22-_i-_xx_-v_-x_-&limit=500&offset=0&orderBy=&searchText='
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

            for item in response.css('div.result-desc'):

                if item is not None:

                    # get the inventory

                    # id used for hashmap
                    id_ = item.xpath('./a/@href').extract()

                    # grab the long name
                    beer_name = item.xpath('./a/text()').extract()

                    # cleanup for json storage
                    id_ = ''.join(id_).strip()
                    id_ = id_[7:]
                    beer_name = ''.join(beer_name).strip()
                    #todo GET INVENTORY

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
                # logging.info(
                #     '================================================================')
                # logging.info('scraping ' + str(next_page))
                # logging.info(
                #     '================================================================')
                yield scrapy.Request(next_page, callback=self.parse, dont_filter=False)






