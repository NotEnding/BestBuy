# -*- coding: utf-8 -*-#
# Name: first_to_get_site_url_v2
# Description:  
# Date: 2019/10/23
"""
在解析某个品类超过100页时,会返回404页面,该页面上可以解析出全部的site url
"""

import os
import sys
from lxml import etree

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from api.ApiRequest import ApiRequest
from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


class BestbuyErrorHandle(ApiRequest):

    def __init__(self):
        super().__init__()

    def __parse(self,text):
        html_element = etree.HTML(text)
        a_result = html_element.xpath('//a/@href')
        site_list = []
        for a in a_result:
            if a.__contains__("/site"):
                site_list.append(a)
            else:
                continue
        return site_list


    def handle(self,url):
        response = self.answer_the_url(url)
        if response.status_code == 404:
            site_list = self.__parse(response.text)
            for site in site_list:
                if site.startswith('/site'):
                    url = 'https://www.bestbuy.com' + site
                    dbservice.redis_conn.sadd("bestbuy_site_urls",url)
                elif site.startswith('https://www.bestbuy.com'):
                    dbservice.redis_conn.sadd("bestbuy_site_urls", site)
                else:
                    continue






if __name__ == '__main__':
    url = "https://www.bestbuy.com/site/music/vinyl-records/pcmcat197800050048.c?id=pcmcat197800050048&cp=101"
    BestbuyErrorHandle().handle(url)