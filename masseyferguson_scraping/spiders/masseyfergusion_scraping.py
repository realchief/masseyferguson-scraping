from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request
from lxml import html

import scrapy
from scrapy.item import Item, Field
import re
import json


class SiteProductItem(Item):
    product_name = Field()
    images = Field()
    feature = Field()
    specification = Field()


class MasseyfergusionScraper (scrapy.Spider):
    name = "scrapingdata"
    allowed_domains = ['www.masseyferguson.us']
    START_URL = 'http://www.masseyferguson.us/products.html'
    DOMAIN_URL = 'http://www.masseyferguson.us'
    settings.overrides['ROBOTSTXT_OBEY'] = False
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/57.0.2987.133 Safari/537.36"}

    def start_requests(self):
        yield Request(url=self.START_URL,
                      callback=self.parse_page,
                      dont_filter=True
                      )

    def parse_page(self, response):

        page_links = response.xpath('//a[@class="frameImg"]/@href').extract()

        for p_link in page_links:
            if 'https' in p_link:
                sub_link = p_link
            else:
                sub_link = self.DOMAIN_URL + p_link
            yield Request(url=sub_link, callback=self.parse_product, dont_filter=True, headers=self.headers)

    def parse_product(self, response):
        product = SiteProductItem()

        product_name = self._parse_name(response)
        product['product_name'] = product_name

        images = self._parse_images(response)
        product['images'] = images

        feature = self._parse_feature(response)
        product['feature'] = feature

        specification = self._parse_specification(response)
        product['specification'] = specification

        yield product

    @staticmethod
    def _parse_name(response):
        title = response.xpath('//title/text()').extract()
        return title[0].strip() if title else None

    def _parse_images(self, response):
        images = []
        asset_images = response.xpath('//div[@class="frameImg"]//img/@data-lazy').extract()
        if asset_images:
            for image in asset_images:
                image = self.DOMAIN_URL + image
                images.append(image)
        return images

    @staticmethod
    def _parse_feature(response):
        price = response.xpath('//span[contains(@id,"priceblock")]/text()').extract()
        return price[0].split('-')[0] if price else None

    @staticmethod
    def _parse_specification(response):
        original_price = response.xpath('//span[contains(@class,"a-text-strike")]/text()').extract()
        if not original_price:
            original_price = response.xpath('//span[contains(@id,"priceblock")]/text()').extract()
        return original_price[0].split('-')[0] if original_price else None
