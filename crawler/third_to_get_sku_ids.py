# -*- coding: utf-8 -*-#
# Name: third_to_get_sku_ids
# Description:  根据第二步获取到的sub_site_url，获取页面上的skus id
# Date: 2019/10/21

"""
根据第二步获取到的sub_site_url，获取页面上的sku_ids
"""

import os
import sys
from multiprocessing.pool import Pool
from lxml import etree
import re
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


class GetSkuIds(ApiRequest):

    def __init__(self):
        super().__init__()

    def __parse_page(self, html_text):
        """
        :return: 返回页数
        """
        # 获取商品,返回页数
        html_element = etree.HTML(html_text)
        pages_info = html_element.xpath('//div[@class="left-side"]/span/text()')
        if pages_info:
            numbers = re.findall(r'\d+', pages_info[0])
            current_page = numbers[0]
            page_size = numbers[1]
            total = numbers[-1]
            if int(total) % int(page_size) == 0:
                total_page = int(total) // int(page_size)
            else:
                total_page = int(total) // int(page_size) + 1
        else:
            total_count = html_element.xpath('//span[@class="item-count"]/text()')
            if total_count:
                total = re.findall(r"\d+", total_count[0])
                if total:
                    # 默认以24为page size
                    if int(total[0]) % 24 == 0:
                        total_page = int(total[0]) // 24
                    else:
                        total_page = int(total[0]) // 24 + 1
                else:
                    pass
            else:
                pass
        # 当total_page 超过100页时，以100页为最大页数
        total_pages = total_page if total_page <= 100 else 100
        return total_pages

    def __parse_skuIds(self, html_text):
        """
        :param html_text:解析页面上的
        :return:
        """
        # 获取页面上的sku id
        result = re.findall(r'data-sku-id="(\d+)"', html_text, re.DOTALL)
        if result:
            # 去重
            sku_lists = list(set(result))
        return sku_lists

    def get_skuIds(self, url):
        resposne = self.answer_the_url(url)
        if resposne.status_code == 200:
            total_pages = self.__parse_page(resposne.text)
            if total_pages:
                for page in range(1, total_pages + 1):
                    link = url + "&cp=" + str(page)
                    resp = self.answer_the_url(link)
                    if resp.status_code == 200:
                        sku_lists = self.__parse_skuIds(resp.text)
                        if sku_lists:
                            count = 0
                            for sku_id in sku_lists:
                                dbservice.redis_conn.sadd("bestbuy_sku_ids", sku_id)
                                count += 1
                            logger.info("{} 页面,总计{}个sku_id加入队列成功".format(link, str(count)))
                        else:
                            logger.info("{} 页面未解析到sku_id".format(link))
                    else:
                        logger.info("请求{}页面失败,请检查".format(link))
                        dbservice.redis_conn.sadd("bestbuy_parse_error_url", link)
            else:
                logger.info("该{}页面未解析到商品sku_id信息".format(url))
        elif resposne.status_code == 404:
            pass
        else:
            logger.info("请求{}页面失败,请检查".format(url))
            dbservice.redis_conn.sadd("bestbuy_parse_error_url", url)


# run task
def run_task(url):
    GetSkuIds().get_skuIds(url)


if __name__ == '__main__':
    while True:
        bestbuy_site_length = dbservice.redis_conn.scard("bestbuy_sub_site_urls")
        if bestbuy_site_length != 0:
            po = Pool(2)
            for i in range(2):
                site_url = dbservice.redis_conn.spop("bestbuy_sub_site_urls")
                if site_url:
                    po.apply_async(run_task, args=(site_url,))
                else:
                    continue
            time.sleep(random.random() * 2)
            po.close()
            po.join()
        else:
            logger.info("全部sku id获取完成")
            break
    logger.info('任务执行完毕，全部商品sku id获取完成')
