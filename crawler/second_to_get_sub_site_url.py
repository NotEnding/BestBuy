# -*- coding: utf-8 -*-#
# Name: second_to_get_sub_site_url
# Description:  
# Date: 2019/10/23
"""
通过第一步获取到的大类site url 获取全部的带筛选条件下的 sub_site_url
"""

import os
import sys
from multiprocessing.pool import Pool
from lxml import etree
import time
import random

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


class GetSubSiteUrl(ApiRequest):

    def __init__(self):
        super().__init__()

    def get_sub_site_url(self, url):
        resposne = self.answer_the_url(url)
        if resposne.status_code == 200:
            html_element = etree.HTML(resposne.text)
            a_href = html_element.xpath('//div[@class="facet-section"]//a/@href')
            if a_href:
                count = 0
                for a in a_href:
                    if a.startswith("https://www.bestbuy.com"):
                        dbservice.redis_conn.sadd("bestbuy_sub_site_urls", a)
                        count += 1
                    else:
                        logger.info(f"href:{a}")
                        continue
                logger.info("{} 下总计获得 {} 个sub_site ".format(url, str(count)))
            else:
                logger.info(f"{url}未获取到sub_site")


# 处理函数
def run_task(url):
    GetSubSiteUrl().get_sub_site_url(url)


if __name__ == '__main__':
    while True:
        bestbuy_site_length = dbservice.redis_conn.scard("bestbuy_site_urls")
        if bestbuy_site_length != 0:
            po = Pool(2)
            for i in range(2):
                site_url = dbservice.redis_conn.spop("bestbuy_site_urls")
                if site_url:
                    po.apply_async(run_task, args=(site_url,))
                else:
                    continue
            time.sleep(random.random() * 2)
            po.close()
            po.join()
        else:
            logger.info("全部sub_site_url获取完成")
            break
    logger.info('任务执行完毕，全部商品sub_site_url获取完成')
