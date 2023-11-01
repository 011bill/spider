# 导入BaiduSpider
import time

from baiduspider import BaiduSpider
from pprint import pprint
from gne import GeneralNewsExtractor
import requests
import json

if __name__ == '__main__':
    # 打开JSON文件
    with open("data1.json", "r") as json_file:
    # with open("data.json", "r") as json_file:
        # 读取JSON文件内容
        data_all = json.load(json_file)

    dataList = []
    for company in data_all:
        data_company = company['data']
        if data_company:
            for data in data_company:
                data_url_ = data['url']
                id_ = data['id']
                if data_url_:
                    # 提取文章内容
                    data_url_ = data_url_.replace("https://", "http://")

                    html_content = BaiduSpider().search_url(data_url_)

                    extractor = GeneralNewsExtractor()
                    result = extractor.extract(html_content, noise_node_list=['//div[@class="comment-list"]'])
                    result['id'] = id_
                    result['collectDate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    pprint(result)
                    dataList.append(result)
                    time.sleep(3)


    with open("detail.json", "w") as outfile:
        json.dump(dataList, outfile)