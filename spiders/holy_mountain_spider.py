"""Holy Mountain Spider implementation.

Example:
    $ scrapy runspider holy_mountain_spider.py -o output.json

"""

import datetime
import logging
import scrapy
import hashlib
from enum import Enum

class Section(Enum):
    ON_TAP = 1
    IN_HOUSE = 2
    TO_GO = 3
    UNKNOWN = 4

TAP_STRING = 'Beers on tap'
IN_HOUSE_STRING = 'Bottles for here'
TO_GO_STRING = 'Bottles to go'

class HolyMountainSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for Holy Mountain.
    """

    name = "holyMountainSpider"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': str(download_delay)
    }

    def start_requests(self):

        urls = [
            'https://holymountainbrewing.com/beers'
        ]

        logging.getLogger(__name__)

        for url in urls:
            # logging.info(
            #     '================================================================')
            # logging.info('scraping ' + url)
            # logging.info(
            #     '================================================================')

            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):

        logging.getLogger(__name__)
        current_section = Section.UNKNOWN

        # grab each entry listed
        if response is not None:

            for section in response.css('div.grid-100'):

                if 'h1' in section.extract():
                    availbility = section.xpath('./h1/text()').extract()

                    if TAP_STRING in availbility:
                        current_section = Section.ON_TAP    
                    elif IN_HOUSE_STRING in availbility:
                        current_section = Section.IN_HOUSE
                    elif TO_GO_STRING in availbility:
                        current_section = Section.TO_GO
                    else:
                        current_section = Section.UNKNOWN

                elif 'beer-output' in section.extract():

                    if 'h3' in section.extract():
                        name = section.css('div.beer-output-data').xpath('./h3/text()').extract()[0]
                        
                        style = ''
                        
                        if 'h4' in section.extract():
                            tmp = section.css('div.beer-output-data').xpath('./h4/text()').extract()
                            if len(tmp) > 0:
                                style = tmp[0]
                        
                        if name is not None:

                            full_name = ' - '.join((current_section.name, name, style)).encode('utf-8').strip()
                            hash_id = hashlib.md5(full_name).hexdigest()

                            yield {
                                'name': full_name,
                                'id': hash_id
                            }
