import scrapy
import datetime
import logging
from check_status import check_response_status
from random import *

# can run with scrapy runspider etreSpider.py -o output.json
#https://doc.scrapy.org/en/latest/topics/items.html

class EtreSpider(scrapy.Spider):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    name = "etreBeerSpider"
    downloadDelay = randint(1, 4)

    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(downloadDelay),
        'LOG_ENABLED': False
    }

    def __init__(self, *args, **kwargs):
        super(EtreSpider, self).__init__(*args, **kwargs)
        self.scrape_success = True


    def start_requests(self):
        urls = [
            'https://www.bieresgourmet.be/en/new-products?page=1'
        ]

        for url in urls:

            logging.info('================================================================')
            logging.info('scraping ' + url)
            logging.info('================================================================')

            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # grab each entry listed
        if response is not None:

            for item in response.css('div.product-miniature'):

                subitem = item.css('div.product-description')

                name = subitem.css('h3.product-title').xpath('./a/text()').extract()

                stock_status = subitem.css('div.product-quantities').xpath('./label/text()').extract()                

                if not name or 'Out of stock' in stock_status:
                    continue

                product_id = item.xpath('@data-id-product').extract()[0]

                link = subitem.css('h3.product-title').xpath('./a/@href').extract()

                price = subitem.css('div.product-price-and-shipping').xpath('./span/text()').extract()
                print(name)
                yield {
                     'name': name,
                     'id': int(product_id),
                     'price': price,
                     'link': link,
                 }

            next_page_link = response.css('a.next').xpath('./@href').extract()
            print next_page_link

            if next_page_link is not None:
                logging.info('================================================================')
                logging.info('scraping ' + str(next_page_link[0]))
                logging.info('================================================================')
                yield scrapy.Request(str(next_page_link[0]), callback=self.parse)
