import scrapy
import datetime
import logging
from random import *

#scrapy runspider belgianHappinessSpider.py -o output.json
#https://shop.cantillon.be/en/
#https://shop.cantillon.be/en/beers/49-exceptional-cuvee-cantillon.html
#https://www.reddit.com/r/atlbeer/comments/5bzoc4/ratlbeer_random_daily_discussion_november_09_2016/
#https://shop.cantillon.be/en/27-beers
#https://shop.cantillon.be/en/29-special-beer-packs
#https://shop.cantillon.be/en/special-beer-packs/51-grape-cantillon.html

#released around noon pacific

dateEntry = False

class BelgianHappinessSpider(scrapy.Spider):

    name = "belgianHappinessSpider"
    
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY' : '8'
    }

    def start_requests(self):
    	#this will add duplicates in the output file
		urls = [
			'https://shop.cantillon.be/en/'
		]

		for url in urls:
			logging.info( '================================================================' )
			logging.info( 'scraping ' + url )
			logging.info( '================================================================' )

			yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

		global dateEntry

		#grab each entry listed
		if response is not None:

	 		for beer in response.css('div.product-item'):

				beerName = beer.xpath('.//span[@class="title"]/text()').extract()
				id       = beer.css('.add-to-cart').xpath('./@data-alpha').extract()

				if not dateEntry:
					dateEntry = True
					yield {
						'creationDate' : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
					}
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

