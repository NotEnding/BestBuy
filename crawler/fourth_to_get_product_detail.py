# -*- coding: utf-8 -*-#
# Name: fourth_to_get_product_detail
# Description:  
# Date: 2019/10/22
"""
获取商品的详情信息
商品summaries:https://www.bestbuy.com/api/1.0/product/summaries?includeInactive=false&skus=6295310
商品price:https://www.bestbuy.com/pricing/v1/price/item?catalog=bby&context=Product-Page&salesChannel=LargeView&skuId=6295310
"""
import datetime
import os
import sys

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from api.ApiRequest import ApiRequest
from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger
from settings import PRODUCT_SUMMARIES, PRODUCT_PRICE

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


class GetProductDetail(ApiRequest):

    def __init__(self):
        super().__init__()

    def __parse_product_detail(self, sku_id):
        # 首先获取summaries信息
        summaries_url = PRODUCT_SUMMARIES.format(str(sku_id))
        logger.info("商品详情信息URL:{}".format(summaries_url))
        summaries_response = self.answer_the_url(summaries_url)
        if summaries_response.status_code == 200:
            product_info = summaries_response.json()[0]
            # 将URL更新,添加域名
            product_info['url'] = "https://www.bestbuy.com" + product_info['url']
            # 添加价格信息
            price_url = PRODUCT_PRICE.format(str(sku_id))
            logger.info("商品价格信息URL:{}".format(price_url))
            price_response = self.answer_the_url(price_url)
            if price_response.status_code == 200:
                # 合成一个product_info
                product_info['productPrice'] = price_response.json()
            else:
                product_info['productPrice'] = ""
            return product_info
        else:
            return None

    def get_product_detail(self, sku_id):
        product_info = self.__parse_product_detail(sku_id)
        if product_info:
            # 创建时间
            create_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            product_info['create_time'] = create_time
            try:
                # 先去重
                dbservice.db['products'].find_one_and_delete({"skuId": product_info["skuId"]})
                dbservice.db['products'].insert_one(product_info)
                logger.info("商品详情信息入库成功,sku_id:{}".format(str(sku_id)))
            except Exception as e:
                logger.error("商品详情信息入库失败,sku_id:{},错误原因:{}".format(str(sku_id), str(e)))
                # 加入到出错的队列
                dbservice.redis_conn.sadd("insert_detail_database_error_skuId", sku_id)
        else:
            logger.info("商品sku_id:{},未获取到对应的详情信息".format(str(sku_id)))
