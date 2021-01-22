import datetime
import logging
import scrapy
import hashlib
import json
class PaFineWine(scrapy.Spider):


    name = "paFineWineComingSoon"
    download_delay = 0
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36', # for test
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
            'http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/CategoryProductsListingView?langId=-1&storeId=10051&catalogId=10051&advancedSearch=&sType=SimpleSearch&categoryId=1334015&searchType=1002&facet=&searchTermScope=&searchTerm=&metaData=&resultCatEntryType=&filterFacet=&manufacturer=&emsName=&gridPosition=&resultsPerPage=15&minPrice=&maxPrice=&sortBy=5&disableProductCompare=false&ajaxStoreImageDir=%2fwcsstore%2fWineandSpirits%2f&filterTerm=&variety=Bourbon&categoryType=Spirits&enableSKUListView=&ddkey=ProductListingView'
            #'http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/CatalogSearchResultView?storeId=10051&catalogId=10051&langId=-1&categoryId=1334015&variety=Bourbon&categoryType=Spirits&parent_category_rn=1334013&searchSource=E&sortBy=5&top_category=25208&pageView=&beginIndex=0#facet:10002671111091051101033283111111110&productBeginIndex:0&orderBy:&pageView:&minPrice:&maxPrice:&pageSize:45&'
            #'http://www.finewineandgoodspirits.com'
        ]

        logging.getLogger(__name__)
        my_data = {'facetId': 10002671111091051101033283111111110, 'resultType': 'products',
                   'face': 'ads_f10002_ntk_cs%3A%22Coming+Soon%22', 'categoryId': 1334015, 'storeId': 10051,
                   'catalogId': 10051, 'langId': -1, 'requesttype': 'ajax',
                   }
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False, method='POST', body=json.dumps(my_data))

    def parse(self, response):

        logging.getLogger(__name__)

        # grab each entry listed
        if response is not None:
            for item in response.css("a.catalog_item_name"):
                name = item.xpath('./text()').extract()[0]
                print(name)

                link = 'http://www.finewineandgoodspirits.com/' + item.xpath('./@href').extract()[0]

                name = '[' + name + '](' + link + ')'
                #yield {
                #    'name': name,
                #    'id': hashlib.md5(name.encode('utf-8')).hexdigest()
                #}









