import datetime
import logging
import scrapy
import hashlib

class PaFineWine(scrapy.Spider):


    name = "paFineWIne"
    download_delay = 0
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
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
            'http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/CategoryProductsListingView?langId=-1&storeId=10051&catalogId=10051&advancedSearch=&sType=SimpleSearch&categoryId=1334015&searchType=1002&facet=&searchTermScope=&searchTerm=&metaData=&resultCatEntryType=&filterFacet=&manufacturer=&emsName=&gridPosition=&resultsPerPage=300&minPrice=&maxPrice=&sortBy=5&disableProductCompare=false&ajaxStoreImageDir=%2fwcsstore%2fWineandSpirits%2f&filterTerm=&variety=Bourbon&categoryType=Spirits&enableSKUListView=&ddkey=ProductListingView'
        ]

        logging.getLogger(__name__)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)

    def parse(self, response):
        count = 0
        logging.getLogger(__name__)
        # grab each entry listed
        if response is not None:
            for item in response.css('div.productImgOne'):
                print(item)
                name = item.xpath('./a/img/@title').extract()
                print(name)
                print(item.xpath('./div[@class="ribbon-red"]').extract())
                #print("-------")
                #link = 'http://www.finewineandgoodspirits.com/' + item.xpath('./@href').extract()[0]
                #name = '[' + name + '](' + link + ')'

                ##yield {
                #    'name': name,
                #    'id': hashlib.md5(name.encode('utf-8')).hexdigest()
                #}
                count += 1
        print('count ' + str(count))









