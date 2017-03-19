import scrapy
import datetime

#scrapy runspider belgianHappinessSpider.py -o output.json

dateEntry = False

class BelgianHappinessSpider(scrapy.Spider):

    name = "belgianHappinessSpider"
    
    custom_settings = {
        'COOKIES_ENABLED': 'false',
        'DOWNLOAD_DELAY' : '4'
    }

    def start_requests(self):
    	#this will add duplicates in the output file
		urls = [
			'https://www.belgianhappiness.com/limited-editions',
		    'https://www.belgianhappiness.com/beers' #url for all beer
		]

		for url in urls:
			print '================================================================'
			print 'scraping ' + url
			print '================================================================'

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
				yield {
					'name'  : beerName,
					'id'    : id #can't treat this id as an int
				}

		links     = response.css('div.pager').css('.next').xpath('./@href').extract()
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

