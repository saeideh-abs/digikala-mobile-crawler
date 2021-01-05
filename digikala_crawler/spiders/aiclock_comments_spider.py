# save 'sortby' in a variable
# check if current page is last page

# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from digikala_crawler.items import DigikalaCrawlerItem


class StorageCommentsSpider(scrapy.Spider):
    name = 'camera_comments_spider'
    i = 0
    # sort by most visited by default
    start_urls = ['https://www.digikala.com/search/category-camera/?sortby=7']

    def parse(self, response):
        products_link = response.css('ul.c-listing__items li div.c-product-box a.c-product-box__img')
        yield from response.follow_all(products_link, callback=self.parse_product)

        current_page = response.css('.c-listing ul.c-pager__items li .is-active::attr(data-page)').get()
        next_page = int(current_page) + 1
        next_page_url = response.css('.c-listing ul.c-pager__items li a.is-active') \
            .xpath('../following-sibling::li[1]//a/@href').extract_first()
        if next_page < 277 and next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_product(self, response):
        self.i += 1
        print("product number ", self.i)

        url = response.request.url
        product_id = url.split('/')[4].split('-')[1]
        brand = response.css('section.c-product__info .c-product__directory .product-brand-title::text').get()
        category = response.css('section.c-product__info .c-product__directory  ul li:nth-child(2) a::text').get()
        product_title = response.css('section.c-product__info .c-product__title::text').get()
        title_splitted = product_title.split('مدل')
        if len(title_splitted) == 2:
            model = title_splitted[1]
        else:
            model = product_title
        rate = response.css('.c-product__engagement .c-product__engagement-rating::text').get()

        comments_url = 'https://www.digikala.com/ajax/product/comments/{}'.format(product_id)
        comment_request = response.follow(comments_url, self.parse_comments)
        comment_request.meta['product_id'] = product_id
        comment_request.meta['brand'] = brand
        comment_request.meta['category'] = category
        comment_request.meta['model'] = model
        comment_request.meta['rate'] = rate
        yield comment_request

    def parse_comments(self, response):
        self.logger.info(f"\n **************************************************************\n")
        item = DigikalaCrawlerItem()
        for comment in response.css('ul.c-comments__list li section'):
            item['product_id'] = response.meta.get('product_id')
            item['brand'] = response.meta.get('brand').strip()
            item['category'] = response.meta.get('category')
            item['model'] = response.meta.get('model').strip()
            rate = response.meta.get('rate')
            if rate is not None:
                item['rate'] = rate.strip()
            item['holder'] = comment.css('div.aside .c-comments__user-shopping .cell-name::text').get().strip()
            item['date'] = comment.css('div.aside .c-comments__user-shopping li:nth-child(2) div.cell::text').get() \
                .strip().split('در تاریخ')[1]
            item['buyer'] = comment.css('div.aside .c-comments__user-shopping .c-comments__buyer-badge::text').get()
            comment_title = comment.css('div.article .header div::text').get()
            if comment_title is not None:
                item['comment_title'] = comment_title.strip()
            else:
                item['comment_title'] = ''
            comment_body = comment.css('div.article p::text').get()
            if comment_body is not None:
                item['comment_body'] = comment_body.strip()
            else:
                item['comment_body'] = ''
            item['advantages'] = comment.css('div.article .c-comments__evaluation-positive ul li::text').getall()
            item['disadvantages'] = comment.css('div.article .c-comments__evaluation-negative ul li::text').getall()
            item['likes'] = comment.css('div.article .footer .btn-like::attr(data-counter)').get()
            recommendation = comment.css('div.aside .c-message-light::attr(class)').get()
            if recommendation is not None:
                item['recommendation'] = recommendation.split('c-message-light--')[1]
            else:
                item['recommendation'] = ""
            yield item

        current_page = response.css('.c-pager ul.c-pager__items li a.is-active::attr(data-page)').get()
        print("current page is:", current_page)
        if current_page is None:
            return
        next_page = int(current_page) + 1
        print("next page is:", next_page)
        next_page_url = response.css('.c-pager ul.c-pager__items li a.is-active') \
            .xpath('../following-sibling::li[1]//a/@href').extract_first()
        if next_page_url is not None:
            next_page_request = response.follow(next_page_url, self.parse_comments)
            next_page_request.meta['product_id'] = item['product_id']
            next_page_request.meta['brand'] = item['brand']
            next_page_request.meta['category'] = item['category']
            next_page_request.meta['model'] = item['model']
            next_page_request.meta['rate'] = rate
            yield next_page_request
