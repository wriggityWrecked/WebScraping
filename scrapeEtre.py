import scrapy

class EtreSpider(scrapy.Spider):

    name = "etreBeerSpider"
    
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
	 			
	 			print str( beer )

	 			print str( beer.css('td').xpath('@class') )

	 			#id used for hashmap
				id       = beer.xpath('./a/@href').extract()

				#grab the long name
				beerName = beer.xpath('./a/text()').extract()


				#cleanup for json storage
				id       = ''.join( id ).strip()
				id       = id[7:]
				beerName = ''.join( beerName ).strip()

				#filter out location in the name
				# if "Redwood City" != beerName and "Hollywood" != beerName and "San Francisco" != beerName and 'Read More ' not in beerName :
				# 	yield {
				# 		'name'  : beerName,
				# 		'id' : int( id )
				# 	}

		links     = response.xpath('//div[@class="floatLeft"]/a[contains(text(),"next")]/@href').extract()
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

