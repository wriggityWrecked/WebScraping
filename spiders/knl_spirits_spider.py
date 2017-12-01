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

    def __init__(self, *args, **kwargs):

        self.date_entry = False
        super(KnLSpiritsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):

        urls = [
            'http://www.klwines.com/Products/r?r=0+4294967191&d=1&t=&o=8&z=False'  # url for all spirits
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

                    # filter out location in the name, specific to these scraped results
                    if beer_name != "Redwood City" and beer_name != "Hollywood" \
                            and beer_name != "San Francisco" and 'Read More ' not in beer_name:

                        if not self.date_entry:
                            self.date_entry = True
                            yield {
                                'creationDate': \
                                    datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                            }

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

