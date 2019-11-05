# -*- coding: utf-8 -*-#
# Name: settings
# Description:  
# Date: 2019/10/15
import os

# base dir
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 获取项目所在目录

# conf dir
CONF_DIR = os.path.join(BASE_DIR, "conf")  # 存储配置信息
if not os.path.exists(CONF_DIR):
    os.mkdir(CONF_DIR)

# log dir
LOG_DIR = os.path.join(BASE_DIR, "log")  # 日志存放目录
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# base url
BASE_URL = 'https://www.bestbuy.com/'

# product_summaries
PRODUCT_SUMMARIES = "https://www.bestbuy.com/api/1.0/product/summaries?includeInactive=false&skus={}"

# product_price
PRODUCT_PRICE = "https://www.bestbuy.com/pricing/v1/price/item?catalog=bby&context=Product-Page&salesChannel=LargeView&skuId={}"