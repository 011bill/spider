import json
from baiduspider import BaiduSpider
from gne import GeneralNewsExtractor
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def add_company():
    # 打开JSON文件
    with open("data.json", "r") as json_file:
        # 读取JSON文件内容
        data_all = json.load(json_file)
    with open("detail.json", "r") as json_file:
        # 读取JSON文件内容
        dataList = json.load(json_file)

    for data in dataList:
        id_ = data['id']
        for data_ in data_all:
            company = data_['company']
            for data__ in data_['data']:
                if id_ == data__['id']:
                    data['company'] = company

    with open("detail.json", "w") as outfile:
        json.dump(dataList, outfile)

    # with open("data.json", "w") as outfile:
    #     json.dump(data_all, outfile)


def ascii_to_utf8():
    with open("data.json", "r") as json_file:
        # 读取JSON文件内容
        data_all = json.load(json_file)
    with open("detail.json", "r") as json_file:
        # 读取JSON文件内容
        dataList = json.load(json_file)

    with open("detail.json", "w", encoding="utf8") as outfile:
        json.dump(dataList, outfile, ensure_ascii=False)

    with open("data.json", "w", encoding="utf8") as outfile:
        json.dump(data_all, outfile, ensure_ascii=False)


def clear_err():
    with open("data1.json", "r") as json_file:
        # 读取JSON文件内容
        data_all = json.load(json_file)
    for data in data_all:
        for data_ in data['data']:
            data_['flag'] = 0
            data_['err'] = None
            # if data_['flag'] == 1:
            #     pass

    with open("data1.json", "w") as outfile:
        json.dump(data_all, outfile)


def by_selenium(url):
    # 我们并不需要浏览器弹出
    options = Options()
    options.headless = True

    # 启动浏览器的无头模式，访问
    # ========================================
    # 注意：这是Selenium 4.10.0以下写法，高版本见下面
    # ========================================
    # driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver = webdriver.Chrome('D:\work\chromedriver-win64\chromedriver-win64\chromedriver.exe', options=options)
    driver.get(url)

    # 获取页面的源代码
    page_source = driver.page_source

    return page_source
    # 输出页面源代码
    print(page_source)

    driver.quit()


if __name__ == '__main__':
    # data_url_ = 'http://stock.10jqka.com.cn/20221121/c643081110.shtml'
    # data_url_ = 'http://news.10jqka.com.cn/20230802/c43698127.shtml'
    # data_url_ = 'http://stock.10jqka.com.cn/20221226/c643852486.shtml'
    # data_url_ = 'http://www.eet-china.com/mp/a256178.html'
    data_url_ = 'http://m.10jqka.com.cn/sn/20231030/44914999.shtml'
    encoding = None
    try:
        # if '10jqka.com.cn' or 'cnstock.com' in data_url_:
        if data_url_.find('10jqka.com.cn') != -1 or data_url_.find('cnstock.com') != -1:
            html_content = BaiduSpider().search_url(data_url_, encoding='gbk')
        # elif 'finance.eastmoney.com' or 'caijing.com.cn' in data_url_:
        elif data_url_.find('finance.eastmoney.com') != -1 or data_url_.find('caijing.com.cn') != -1:
            html_content = BaiduSpider().search_url(data_url_, encoding='utf-8')
        # elif 'baijiahao.baidu.com' in data_url_:
        elif data_url_.find('baijiahao.baidu.com') != -1:
            html_content = by_selenium(data_url_)
        else:
            html_content = BaiduSpider().search_url(data_url_)
    except Exception as e:
        print(e)
    extractor = GeneralNewsExtractor()
    result = extractor.extract(html_content, noise_node_list=['//div[@class="comment-list"]'])
    pprint(result)
    # clear_err()



