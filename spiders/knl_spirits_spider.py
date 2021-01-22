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
    download_delay = 0
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay),
        'TELNETCONSOLE_ENABLED': 'false',
        'EXTENSIONS' : {
                'scrapy.extensions.telnet.TelnetConsole': None,
                'scrapy.extensions.corestats.CoreStats': None,
                'scrapy.extensions.memusage.MemoryUsage': None,
                'scrapy.extensions.logstats.LogStats': None,
        }
    }

    def start_requests(self):

        urls = [
            #'http://www.klwines.com/Products/r?r=0+4294967191&d=1&t=&o=8&z=False'  # url for all spirits
            #'https://www.klwines.com/Spirits'
            #'https://www.klwines.com/Products?&filters=sv2_206&limit=500&offset=0&orderBy=60%20asc,search.score()%20desc&searchText='
            #'https://www.klwines.com/Products?&filters=sv2_dflt-stock-instock!28$eq$(3)$True$ff-28-(3)--$or,45.or,48&limit=250&offset=0&orderBy=60%20asc,search.score()%20desc&searchText='
            'https://www.klwines.com/Products?&filters=sv2_206!4&limit=500&offset=0&orderBy=60%20asc,search.score()%20desc&searchText='
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

