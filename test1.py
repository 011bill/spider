# 导入BaiduSpider
import time

from baiduspider import BaiduSpider
from pprint import pprint
from gne import GeneralNewsExtractor
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#标题内容问题（404，下载app），高亮字体，异常数据分析

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

    driver.quit()

    return page_source
    # 输出页面源代码
    # print(page_source)


if __name__ == '__main__':
    # 打开JSON文件
    with open("data.json", "r") as json_file:
        # 读取JSON文件内容
        data_all = json.load(json_file)
    with open("detail.json", "r") as json_file:
        # 读取JSON文件内容
        dataList = json.load(json_file)

    success_count = 0
    error_count = 0
    total_count = 0
    retry_count = 0
    for company in data_all:
        data_company = company['data']
        company = company['company']
        if data_company:
            for data in data_company:
                total_count += 1
                if data and data['flag'] == 0 and data['retry'] < 10:
                    retry_count += 1
                    data_url_ = data['url']
                    id_ = data['id']
                    if data_url_:
                        data_url_ = data_url_.replace("https://", "http://")
                        print(data_url_+'   -------   '+str(total_count))
                        time.sleep(1)
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
                            data['err'] = "get response error:" + str(e)
                            data['retry'] += 1
                            error_count += 1
                            continue

                        if html_content:
                            extractor = GeneralNewsExtractor()
                            try:
                                result = extractor.extract(html_content,
                                                           noise_node_list=['//div[@class="comment-list"]'])
                            except Exception as e:
                                data['err'] = "get detail error:" + str(e)
                                data['retry'] += 1
                                error_count += 1
                                continue
                            if "百度安全验证" in result['title']:
                                data['err'] = "百度安全验证：" + result['content']
                                data['retry'] += 1
                                error_count += 1
                                continue
                            result['id'] = id_
                            result['collect_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            result['company'] = company
                            data['err'] = None
                            pprint(result)
                            dataList.append(result)
                            data['flag'] = 1
                            success_count += 1

    with open("detail.json", "w") as outfile:
        json.dump(dataList, outfile)

    with open("data.json", "w") as outfile:
        json.dump(data_all, outfile)

    print("导出完成 ==> 总条数:" + str(total_count) + ",重试条数:" + str(retry_count) + ",成功:" + str(success_count) + ",失败:" + str(
        error_count))
