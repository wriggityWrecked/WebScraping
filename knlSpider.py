import scrapy
import datetime
import logging

#scrapy runspider knlSpider.py -o output.json

dateEntry = False

class KnLBeerSpider(scrapy.Spider):

	logger = logging.getLogger(__name__)
	name   = "knlBeerSpider"
    
	custom_settings = {
		'COOKIES_ENABLED': 'false',
		'DOWNLOAD_DELAY': '8'
	}

	def start_requests(self):
		urls = [
		    'http://www.klwines.com/Products/r?&r=4294956886+82&&o=3&z=False' #url for all beer
		]

		for url in urls:
			logging.info( '================================================================' )
			logging.info( 'scraping ' + url )
			logging.info( '================================================================' )

			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):

		logger = logging.getLogger(__name__)
		global dateEntry

		#grab each entry listed
		if response is not None:

	 		for beer in response.css('div.result-desc'):

	 			if beer is not None:
		 			#id used for hashmap
					id       = beer.xpath('./a/@href').extract()

					#grab the long name
					beerName = beer.xpath('./a/text()').extract()

					#cleanup for json storage
					id       = ''.join( id ).strip()
					id       = id[7:]
					beerName = ''.join( beerName ).strip()

					#filter out location in the name
					if "Redwood City" != beerName and "Hollywood" != beerName and "San Francisco" != beerName and 'Read More ' not in beerName :

						if not dateEntry:
							dateEntry = True
							yield {
								'creationDate' : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
							}

						yield {
							'name'  : beerName,
							'id' : int( id )
						}

		links     = response.xpath('//div[@class="floatLeft"]/a[contains(text(),"next")]/@href').extract()
		next_page = None

		#did we find a link?
		if len( links ) > 0:
			next_page = links[0];

		if next_page is not None:	
			next_page = response.urljoin( next_page )
			logging.info( '================================================================' )
			logging.info( 'scraping ' + str( next_page ) )
			logging.info( '================================================================' )
			yield scrapy.Request(next_page, callback=self.parse)

