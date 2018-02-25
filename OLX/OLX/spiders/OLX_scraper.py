import scrapy


class OLX_spider(scrapy.Spider):
    name = 'olx_scraper'

    # define starting url
    def start_requests(self):
        url = 'https://www.olx.pl/praca/'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + tag + '/'
        yield scrapy.Request(url, self.parse)

    # parse job pages
    def parse(self, response):
        # follow links to job details
        for href in response.css('td.offer a.link::attr(href)'):
                request = response.follow(href, callback = self.parse_details)
                yield request

        # follow pagination links
        yield response.follow(response.css('a.link.pageNextPrev::attr(href)')[-1], callback = self.parse)

    # parse job details
    def parse_details(self, response):
        def extract_with_css(query):
            result = response.css(query).extract_first()
            if result is None:
                return ''
            else:
                return result.strip()

        if(len(response.css('div.offer-titlebox__details em::text').extract()) > 2):
            added = response.css('div.offer-titlebox__details em::text').extract()[2].strip().split(', ')[1][:-1]
        else:
            added = response.css('div.offer-titlebox__details em::text').extract_first().strip().split(', ')[1][:-1]


        yield {
            'title' :  extract_with_css('div.offer-titlebox h1::text'),
            'city' : extract_with_css('div.offer-titlebox__details a.show-map-link strong::text').split(', ')[0],
            'added' : added,
            'offer_id' : extract_with_css('div.offer-titlebox__details em small::text').split(': ')[1],
            'working_hours' : response.css('ul.offer-parameters a strong::text').extract()[0],
            'type_of_contract' : response.css('ul.offer-parameters a strong::text').extract()[1],
            'salary' : extract_with_css('div.price-label strong.x-large.not-arranged::text') + '  ' +
                       extract_with_css('div.price-label strong.x-large.not-arranged span.nowrap::text'),
            'number_of_views' : extract_with_css('div.pdingtop10 strong::text'),
        }