# -*- coding: utf-8 -*-#
# Name: ProductDetailRunner
# Description:  
# Date: 2019/10/24
"""
获取商品详情接口
"""
import os
import random
import sys
import time
from multiprocessing.pool import Pool

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger
from crawler.fourth_to_get_product_detail import GetProductDetail

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


# 任务处理函数
def script_task(sku_id):
    GetProductDetail().get_product_detail(sku_id)


if __name__ == '__main__':
    while True:
        bestbuy_skuIds_length = dbservice.redis_conn.scard("bestbuy_sku_ids")
        if bestbuy_skuIds_length != 0:
            po = Pool(2)
            for i in range(2):
                sku_id = dbservice.redis_conn.spop("bestbuy_sku_ids")
                if sku_id:
                    po.apply_async(script_task, args=(sku_id,))
                else:
                    continue
            time.sleep(random.random() * 2)
            po.close()
            po.join()
        else:
            logger.info("全部sku详情获取完成")
            break
    logger.info('任务执行完毕，全部商品详情信息获取完成')
