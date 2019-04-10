# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
import json, re, os
import configparser
#reactor.suggestThreadPoolSize(15)

conf=configparser.ConfigParser()
conf.read('config.config')

page_num=conf.getint('number','page_num')

class Spider(scrapy.Spider):
    name = "stocksnap"
    save_path = "./images/"
    start_urls = []
    url = "https://stocksnap.io/api/load-photos/date/asc/"

    for i in range(1, page_num+1):
        start_urls.append(url + str(i))

    def parse(self, response):
        img_items = json.loads(response.body)['results']
        for item in img_items:
            if not os.path.exists(self.save_path + item['img_id'] + '.jpg'):
                yield scrapy.Request(url="https://stocksnap.io/photo/" + item['img_id'], callback=self.photo_info)
            else:
                print(item['img_id'] + "已下载，跳过")

    def photo_info(self, response):
        csrf = response.css("form > input[type='hidden']:nth-child(1)::attr(value)").extract_first()
        imgid = response.css("form > input[type='hidden']:nth-child(2)::attr(value)").extract_first(),
        # print("csrf=" + csrf + "photoid=" + imgid[0])
        # print(response.headers['content-type'].decode())
        # print(response.request.headers.getlist('Cookie'))
        yield FormRequest(url='https://stocksnap.io/photo/download', formdata={'_csrf': csrf, 'photoId': imgid[0]},
                          callback=self.photo_save)

    def photo_save(self, response):
        disposition = response.headers.getlist('Content-Disposition')[0]
        p1 = r"([^=]+)\.([^;]+)"
        pattern1 = re.compile(p1)
        filename = pattern1.findall(disposition.decode())
        # print(filename)
        name = filename[0][0].replace("StockSnap_", "")
        fileHandle = open(self.save_path + name + '.' + filename[0][1], 'wb')
        fileHandle.write(response.body)
        fileHandle.close()

