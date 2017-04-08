import scrapy
import datetime
import logging
from random import *

dateEntry = False

#can run with scrapy runspider biabSpider.py -o output.json

class BelgiumInABox(scrapy.Spider):

    name = "belgiumInABox"
    
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY' : '8'
    }

    def start_requests(self):
		urls = [
			'https://belgiuminabox.com/shop/470-beer#/'
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

	 		for beer in response.css('div.pro_second_box'):

				beerName   = str( beer.css('a.product-name').xpath('text()').extract() )
				available  = str( beer.xpath('.//div[@itemprop="offers"]').xpath('.//span[@class]').extract() )
				link       = str( beer.xpath('.//a/@href').extract() )

				#get the id
				link = link.replace("https://belgiuminabox.com/shop/", "")
				i    = link.find('/') + 1
				j    = link.find('-', i)
				id   = int( link[i:j] )

				if not dateEntry:
					dateEntry = True
					yield {
						'creationDate' : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
					}
				if 'out of stock' in available.lower():
					logging.warning( 'cannot add ' + str( beerName ) + ', (out of stock)' )
				else:
					yield {
						'name'  : beerName,
						'id'    : id
					}

		links     = response.xpath('.//div[@class="pagination clearfix"]').xpath('.//ul[@class="pagination clearfix li_fl"]').xpath('.//li[@class="pagination_next"]').xpath('.//a/@href').extract()
		next_page = None

		#did we find a link?
		if len( links ) > 0:
			next_page = 'https://belgiuminabox.com' + links[0];

		if next_page is not None:	
			next_page = response.urljoin( next_page )
			logging.info( '================================================================' )
			logging.info( 'scraping ' + str( next_page ) )
			logging.info( '================================================================' )
			yield scrapy.Request(next_page, callback=self.parse)

