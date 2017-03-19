import scrapy

productKey = '_id='

#can run with scrapy runspider etreSpider.py -o output.json

class EtreSpider(scrapy.Spider):

    name = "etreBeerSpider"
    
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY': '4'
    }
    
    def start_requests(self):
		urls = [
		    'http://www.bieresgourmet.be/catalog/index.php?main_page=products_all&disp_order=6' #url for all beer
		]

		for url in urls:
			print '================================================================'
			print 'scraping ' + url
			print '================================================================'

			yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

		#grab each entry listed
		if response is not None:

	 		for beer in response.xpath('//td[@class="main"]'):

				beerName = beer.xpath('a/strong/text()').extract()
				beerName = ''.join( beerName ).strip()
	 			link     = str( beer.xpath('a/@href').extract() )

				if len( beerName) > 0 :

		 			#need to get the id from the link, e.g.
		 			#[u'http://www.bieresgourmet.be/catalog/index.php?main_page=product_info&cPath=67_68_110&products_id=2208&zenid=17066b3269e6175c03e880b341bdb85f']
		 			productIndex   = link.find( productKey )
		 			ampersandIndex = link.find( '&' , productIndex )
		 			productIndex  += len(productKey) 
		 			id             = link[productIndex : ampersandIndex] 

					#filter
					yield {
						'name'  : beerName,
						'id'    : int( id ) 
					}

		links     = response.xpath('//div[@class="navSplitPagesLinks forward"]/a[contains(text(),"Next")]/@href').extract()
		next_page = None

		#did we find a link?
		if len( links ) > 0:
			next_page = links[0];

		if next_page is not None:	
			next_page = response.urljoin( next_page )
			print '================================================================'
			print 'scraping ' + str( next_page )
			print '================================================================'
			yield scrapy.Request(next_page, callback=self.parse)
