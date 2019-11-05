# -*- coding: utf-8 -*-#
# Name: first_to_get_site_url_v1
# Description:  
# Date: 2019/10/16

"""
通过请求 https://www.bestbuy.com/ 页面，获取该页面上返回的 site url,解析该页面下的商品
eg:https://www.bestbuy.com/site/home-security-safety/smart-locks-garage-control/pcmcat1477674617379.c?id=pcmcat1477674617379
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

from settings import BASE_URL

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


class GetSiteUrl(ApiRequest):

    def __init__(self):
        super().__init__()

    def __parse(self, text):
        html_element = etree.HTML(text)
        result = html_element.xpath('//*/@href')
        urls = []
        # 提取与商品有关的链接
        for res in result:
            if res.__contains__("/site"):
                if res.startswith("https://www.bestbuy.com/site/"):
                    urls.append(res)
                else:
                    url = "https://www.bestbuy.com" + res
                    urls.append(url)
            else:
                continue
        return urls

    def get_site_url(self):
        resposne = self.answer_the_url(BASE_URL)
        if resposne.status_code == 200:
            urls = self.__parse(resposne.text)
            if urls:
                success_count = 0
                for url in urls:
                    try:
                        dbservice.redis_conn.sadd("bestbuy_site_urls", url)
                        success_count += 1
                    except Exception as e:
                        logger.info("site url加入队列失败,error:{}".format(str(e)))
                logger.info("获取site url成功,共计获取到{}个site url".format(str(success_count)))
            else:
                logger.info("{} 页面未解析到任何category url")


if __name__ == '__main__':
    GetSiteUrl().get_site_url()
