import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pandas as pd
import os
import logging
token = 'TOKEN_HERE'

class Gumtree2009PoloSpider(scrapy.Spider):
    name = 'gumtree_polo_western_cape'
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
                    'location': location,
                    'time_added': time_added,
                    'description_excerpt': description,
                    'image_url': image_url,
                }

        next_page = response.css('.icon-pagination-right::attr(href)').get()
        i = 1
        if next_page is not None:
            i = i + 1
            print('Page' + str(i))
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)


process = CrawlerProcess(settings={
    'FEED_FORMAT': 'csv',
    'FEED_URI': 'posts.csv'
})



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Gumtree Scraping bot! Type '/rescrape' to scrape.")


def rescrape(update, context):
    try:
        os.remove("/Users/pst-home/Workspace/Hardrive/Personal_HD/Software/Random_Software/Matt_Scraper/scrapy_project/posts.csv")
    except:
        pass
    context.bot.send_message(chat_id=update.effective_chat.id, text="Scraping Gumtree for black 2009 polos...")
    process.crawl(Gumtree2009PoloSpider)
    process.start()  # the script will block here until the crawling is finished
    context.bot.send_message(chat_id=update.effective_chat.id, text="Successful scrape. type /find_polos to view results")


def find_polos(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Processing most recent Gumtree data...")
    df = pd.read_csv('posts.csv')
    relevant = df[df['title'].str.contains('2009|black')]
    for index, row in relevant.iterrows():
        msg = row.title + '\n\n'
        msg = msg + 'Description: ' + row.description_excerpt + '\n\n'
        msg = msg + 'Time added: ' + row.time_added + '\n\n'
        msg = msg + 'Location: ' + row.location + '\n\n'
        msg = msg + row.image_url + '\n\n'
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

scrape_handler = CommandHandler('rescrape', rescrape)
dispatcher.add_handler(scrape_handler)

main_handler = CommandHandler('find_polos', find_polos)
dispatcher.add_handler(main_handler)

updater.start_polling()
