"""KNL Spider implementation.

Example:
    $ scrapy runspider knl_beer_spider.py -o output.json

"""

import datetime
import logging
import scrapy


class KnLBeerSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """

    name = "knlBeerSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'TELNETCONSOLE_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            #'http://www.klwines.com/Products/r?&r=4294956886+82&&o=3&z=False' # url for all beer
            #'https://www.klwines.com/beer'
            #'https://www.klwines.com/Products?&filters=-_x-_v%22p%22-_i%2230%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i%22Beer%22-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-30-Beer--%22-_q%22f%22-_i-_xx_-v_--_q-_v%22p%22-_i%2242%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-42-0--%22-_q%22f%22-_i-_xx_-v_-x_-&limit=50&offset=0&orderBy=&searchText='
           'https://www.klwines.com/Products?&filters=sv2_203&limit=500&offset=0&orderBy=60%20asc,search.score()%20desc&searchText='
           #'https://www.klwines.com/Products?&filters=-_x-_v%22p%22-_i%2230%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i%22Beer%22-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-30-Beer--%22-_q%22f%22-_i-_xx_-v_--_q-_v%22p%22-_i%2242%22-_q%22o%22-_i%22eq%22-_q%22v%22-_i0-_q%22vi%22-_itrue-_q%22t%22-_i%22ff-42-0--%22-_q%22f%22-_i-_xx_-v_-x_-&limit=500&offset=0&orderBy=&searchText='
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

            for item in response.css("div.tf-product-image"):

                if item is not None:
                    # get the inventory

                    # id used for hashmap
                    id_ = item.xpath('./a/@data-app-insights-track-search-doc-id').extract()
                    # grab the long name
                    beer_name = item.xpath('./a/@title').extract()

                    # cleanup for json storage
                    id_ = ''.join(id_).strip()
                    id_ = int(id_)
                    beer_name = ''.join(beer_name).strip()
                    #todo GET INVENTORY
                    yield {
                        'name': beer_name,
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
