"""KNL Spider implementation.

Example:
	$ scrapy runspider knl_spider.py -o output.json

"""
import datetime
import logging
from random import randint
import scrapy

DATE_ENTRY = False #todo this should be a class var


class KnLBeerSpider(scrapy.Spider):


    name = "knlBeerSpider"
    download_delay = randint(8, 15)
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            'http://www.klwines.com/Products/r?&r=4294956886+82&&o=3&z=False'  # url for all beer
        ]

        logging.getLogger(__name__)

        for url in urls:
            logging.info(
                '================================================================')
            logging.info('scraping ' + url)
            logging.info(
                '================================================================')

            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        logging.getLogger(__name__)
        global DATE_ENTRY

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

                    # filter out location in the name
                    if beer_name != "Redwood City" and beer_name != "Hollywood" \
                    		and beer_name != "San Francisco" and 'Read More ' not in beer_name:

                        if not DATE_ENTRY:
                            DATE_ENTRY = True
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

        # did we find a link?
        if links:
            next_page = links[0]

        if next_page is not None:
            next_page = response.urljoin(next_page)
            logging.info(
                '================================================================')
            logging.info('scraping ' + str(next_page))
            logging.info(
                '================================================================')
            yield scrapy.Request(next_page, callback=self.parse)
