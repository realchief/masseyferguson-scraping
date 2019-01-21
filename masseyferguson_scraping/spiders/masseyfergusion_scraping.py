from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request
from lxml import html

import scrapy
from scrapy.item import Item, Field
import re
import json


class SiteProductItem(Item):
    Manufacturer = Field()
    Year = Field()
    Model = Field()
    Images = Field()
    Features = Field()
    Implements = Field()
    Category = Field()
    Subcategory = Field()
    Specifications = Field()
    Price = Field()
    Pdf_literature = Field()


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
        product['Manufacturer'] = product_name

        images = self._parse_images(response)
        product['Images'] = images

        year = '2019'
        product['Year'] = year

        feature = self._parse_feature(response)
        product['Features'] = feature

        specification = self._parse_specification(response)
        product['Specifications'] = specification

        subcategory = ''
        product['Subcategory'] = subcategory

        price = ''
        product['Price'] = price

        model = self._parse_model(response)
        product['Model'] = model

        # product['Category'] = category
        # product['Implements'] = implements
        # product['Pdf_literature'] = pdf_literature

        yield product

    @staticmethod
    def _parse_name(response):
        title = response.xpath('//title/text()').extract()
        return title[0].strip() if title else None

    def _parse_model(self, response):

        models = []
        t_header = response.xpath('//table[contains(@class, "table-striped")]/thead/tr/th/text()').extract()
        t_body = response.xpath(
            '//table[contains(@class, "table-striped")]/div[contains(@class, "tablePar")]//tr').extract()
        if len(t_header) > 0:
            for body in t_body:
                tree_body = html.fromstring(body)
                spec_body_vals = tree_body.xpath('//tr/td/text()')
                if spec_body_vals:
                    model = self._clean_text(spec_body_vals[0])
                    models.append(model)
        return models

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
        features = response.xpath('//div[contains(@id,"Features")]//a[contains(@class, "btn-gold")]//text()').extract()
        return features

    def _parse_specification(self, response):
        result = []
        t_header = response.xpath('//table[contains(@class, "table-striped")]/thead/tr/th/text()').extract()
        t_body = response.xpath('//table[contains(@class, "table-striped")]/div[contains(@class, "tablePar")]//tr').extract()
        if len(t_header) > 0:
            for body in t_body:
                spec = {}
                tree_body = html.fromstring(body)
                spec_body_vals = tree_body.xpath('//tr/td/text()')

                for i in range(0, len(t_header) - 1):
                    spec_header = self._clean_text(t_header[i])
                    if spec_body_vals:
                        spec_body = self._clean_text(spec_body_vals[i])
                        spec[spec_header] = spec_body
                result.append(spec)
        return result


    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)