# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DigikalaCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    product_id = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    rate = scrapy.Field()
    holder = scrapy.Field()
    date = scrapy.Field()
    buyer = scrapy.Field()
    comment_title = scrapy.Field()
    comment_body = scrapy.Field()
    advantages = scrapy.Field()
    disadvantages = scrapy.Field()
    likes = scrapy.Field()
    recommendation = scrapy.Field()
    pass
