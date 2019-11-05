import os
import sys
import requests
import time
import random
import yaml
from fake_useragent import UserAgent

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from settings import CONF_DIR
from auxiliary.LogRecord import Logger

logger = Logger().logger


class ApiRequest:
    """
    抓取信息基类
    """

    def __init__(self):
        self.time_out = 20  # 访问链接超时设置
        self.num = 0  # 计算访问次数，用于访问次数限制
        self.proxies = {
            'http': 'http://192.168.2.251:1080',
            'https': 'https://192.168.2.251:1080',
        }

    def answer_the_url(self, url):
        """
        :param url: request url
        :return: return response
        """
        use_time = 0  # 计算同一个链接访问限制，当访问同一链接超过10次时就跳过该链接
        response = None
        # 读取source文件,获取headers
        with open(CONF_DIR + '/conf.yaml', 'r') as f:
            config_dict = yaml.load(f, Loader=yaml.FullLoader)
        headers_dict = config_dict["headers"]
        # headers_dict['user-agent'] = UserAgent().random
        while True:
            try:
                if self.num >= 500:
                    # 超过500次，等待10s
                    time.sleep(10)
                    self.num = 0
                response = requests.get(url=url, timeout=self.time_out, headers=headers_dict, proxies=self.proxies)
                self.num += 1
                break
            except Exception as e:
                time.sleep(random.random() * 2.0 + 0.3)
                use_time += 1
                if use_time > 10:
                    logger.error("<answer_the_url>" + str(e) + url)
                    break
                time.sleep(60)
                continue
        return response
