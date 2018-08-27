import scrapy
import datetime
import logging
from random import *

#scrapy runspider belgianHappinessSpider.py -o output.json

class BelgianHappinessSpider(scrapy.Spider):
	
	logger        = logging.getLogger(__name__)
	name          = "belgianHappinessSpider"
	downloadDelay = randint(2,4)

	custom_settings = {
	    'COOKIES_ENABLED': 'false',
	    'DOWNLOAD_DELAY': str( downloadDelay )
	}

	def start_requests(self):
    	#this will add duplicates in the output file
		urls = [
			#'https://www.belgianhappiness.com/limited-editions',
		    'https://www.belgianhappiness.com/beers' #url for all beer
			#'https://www.belgianhappiness.com/beers?formid=product-filter-form&specs=style%2Calcohol-by-volume-range%2Ccolour%2Cbottle-content%2Csubstyle&new=no&search=&items-per-page=1000&page=1'
		]

		for url in urls:
			logging.info( '================================================================' )
			logging.info( 'scraping ' + url )
			logging.info( '================================================================' )

			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):

		logger = logging.getLogger(__name__)

		#grab each entry listed
		if response is not None:

	 		for beer in response.css('div.product-item'):

				beerName = beer.xpath('.//span[@class="title"]/text()').extract()
				id       = beer.css('.add-to-cart').xpath('./@data-alpha').extract()

				if not id:
					logging.warning( 'cannot add ' + str( beerName ) + ', no ID! (out of stock)' )
				else:
					yield {
						'name'  : beerName[0],
						'id'    : id[0] #can't treat this id as an int
					}

		links     = response.css('div.pager').css('.next').xpath('./@href').extract()
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

