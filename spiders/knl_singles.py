"""KNL Coming Soon Spider implementation.

Example:
    $ scrapy runspider knl_coming_soon.py -o output.json

Big thanks to https://stackoverflow.com/questions/42947417/scrapy-extract-items-from-table

"""

import datetime
import logging
import scrapy
import hashlib



class KnlSinglesSpider(scrapy.Spider):
    """Simple extension of scrapy.Spider for KnL.
    """

    name = "knlSingles"
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
            #'https://www.klwines.com/p/i?i=630036',
            #'https://www.klwines.com/p/i?i=1497554',
            #'https://www.klwines.com/p/i?i=1113012',
            #'https://www.klwines.com/p/i?i=1080857',
            #'https://www.klwines.com/p/i?i=1052771',
            #'https://www.klwines.com/p/i?i=1139604',
            #'https://www.klwines.com/p/i?i=1113012', # EHT BP
            #'https://www.klwines.com/p/i?i=1431726',
            #'https://www.klwines.com/p/i?i=993302', # ORVW
            #'https://www.klwines.com/p/i?i=1454988', # elmer 100
            #'https://www.klwines.com/p/i?i=1047799', #  107
            #'https://www.klwines.com/p/i?i=1502154', # smBLE
            #'https://www.klwines.com/p/i?i=1011879', #m10
            #'https://www.klwines.com/p/i?i=991511', #pvw15
            #'https://www.klwines.com/p/i?i=1508017', # old fitz 14
            #'https://www.klwines.com/p/i?i=1506823', # OF150
            'https://www.klwines.com/p/i?i=1520200', # eht pick
            'https://www.klwines.com/p/i?i=1139604', #stagg jr
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
            for item in response.css("div.alignC"):
                if item is not None:

                    name = response.xpath('//div[@class="result-desc"]/h1').extract()[0].strip().replace("                            ", "")
                    link = response.request.url
                    #id = response.xpath('//div[@class="result-desc"]/span[@class="SKUInformation"]/text()').extract()[0].strip().replace("SKU #", "")

                    # get the inventory
                    #button = item.xpath('./a/@title').extract()

                    cart_button = item.xpath('./input/@id').extract()

                    if len(cart_button) <= 0 or not 'Image3' in str(cart_button):
                        name = "*(OUT OF STOCK)* " + name

                    name = name.replace('<h1>', '').replace('</h1>', '').replace('\r\n', '') + '\n'
                    yield {
                        'name': name + ": " + link,
                        'id': hashlib.md5(name.encode('utf-8')).hexdigest()
                    }









