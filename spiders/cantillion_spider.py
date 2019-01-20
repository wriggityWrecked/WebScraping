"""Cantillion Spider implementation.

Example:
    $ scrapy runspider cantillion_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import hashlib
import random
import constants

class CantillionSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Cantillion.
    """

    name = "cantillionSpider"
    download_delay = random.randint(1,8)
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }


    def start_requests(self):

        # todo cantillion in house availability
        urls = [
            'https://www.billetweb.fr/lpf-nath18-foufoune',
            'https://www.billetweb.fr/multi_event.php?user=13535',
            #'https://www.cantillon.be/'
            #'https://www.cantillon.be/bieres',
            #'https://www.cantillon.be/visites',
            #'https://www.cantillon.be/evenements',
            #'https://www.cantillon.be/#gen_info',
            #'https://www.cantillon.be/ou-trouver-nos-bieres'
        ]

        # random order....
        random.shuffle(urls)

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
        url_to_check = response.request.url

        tuples = []

        if 'www.billetweb.fr' in url_to_check:
            tuples = parse_billetweb(response)

        elif 'shop.cantillon.be' in url_to_check:
            tuples = parse_cantillion_shop(response)

        elif 'www.cantillon.be' in url_to_check:
            tuples = parse_cantillion(response)

        else:
            print 'NO HANDLER FOUND FOR INPUT URL: ' + url_to_check

        # save the relevant info (JSON output)
        for t in tuples:
            if t is not None:
                yield {
                    constants.NAME_KEY: t[1],
                    constants.ID_KEY: t[0]
                }


def hash_string(input):
    return hashlib.md5(input).hexdigest()


def parse_cantillion_shop(response):
    to_return = []

    if response is not None:

        for item in response.xpath('//a/@href').extract():
            if 'https://' not in item:
                item = 'https://shop.cantillon.be/' + item

            to_return.append((hash_string(item), item))

    return to_return  


def parse_cantillion(response):

    to_return = []

    if response is not None:

        for item in response.xpath('//a/@href').extract():
            if 'https://' not in item:
                item = 'https://www.cantillon.be/' + item

            to_return.append((hash_string(item), item))

    return to_return


def parse_billetweb(response):
    '''
    This is dumb, but scrapy won't call custom class methods....
    '''

    logging.getLogger(__name__)
    to_return = []

    # grab each entry listed
    if response is not None:
            
        for item in response.css('div.multi_event_button'):

            if item is not None:
                item_link = item.xpath('./a/@href').extract()[0]
            
                to_return.append((hash_string(item_link), item_link))

    return to_return

