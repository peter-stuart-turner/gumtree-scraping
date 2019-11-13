import scrapy


class TestSpider(scrapy.Spider):
    name = 'test_spider'
    start_urls = [
        'https://www.gumtree.co.za/s-western-cape/polo/v1l3100001q0p1'
    ]

    def parse(self, response):
        advert_elements = response.css('div.related-item')
        for ad in advert_elements:
            title = ad.css(' .title span::text').get()
            description = ad.css('.description-text span::text').get()
            location = ad.css('.location-date span::text').extract_first()
            time_added = ad.css('.creation-date span::text').extract_first()
            image_url = ad.css('img.lazyload::attr(data-src)').get()
            # if self.is_worth_proceeding(title, description):
            yield {
                    'title': title,
                    'time_added': time_added,
                    'description_excerpt': description,
                    'image_url': image_url,
                }

        next_page = response.css('.icon-pagination-right::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)




