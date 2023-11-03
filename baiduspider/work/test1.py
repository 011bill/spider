# 导入BaiduSpider
import time

from baiduspider import BaiduSpider
from pprint import pprint
from gne import GeneralNewsExtractor
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import mysql.connector


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
    # 连接到MySQL服务器
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bd_spider",
        connection_timeout=10
    )
    cursor = conn.cursor()
    select_query = "SELECT id, company, url, retry FROM company_bdzixun_copy1 WHERE filter = 0 and flag = 0 and retry < 10"
    cursor.execute(select_query)
    records = cursor.fetchall()

    print('========开始执行=======')
    success_count = 0
    error_count = 0
    total_count = 0
    for row in records:
        total_count += 1
        id, company, url, retry = row
        err = None
        if url:
            data_url_ = url.replace("https://", "http://")
            time.sleep(1)
            try:
                if data_url_.find('10jqka.com.cn') != -1 or data_url_.find('cnstock.com') != -1:
                    html_content = BaiduSpider().search_url(data_url_, encoding='gbk')
                elif data_url_.find('finance.eastmoney.com') != -1 or data_url_.find('caijing.com.cn') != -1:
                    html_content = BaiduSpider().search_url(data_url_, encoding='utf-8')
                elif data_url_.find('baijiahao.baidu.com') != -1:
                    html_content = by_selenium(data_url_)
                else:
                    html_content = BaiduSpider().search_url(data_url_)
            except Exception as e:
                err = "get response error:" + str(e)
                retry += 1
                flag = 0
                error_count += 1
                # 更新公司资讯列表
                update_query = "UPDATE company_bdzixun_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                cursor.execute(update_query, (0, retry, err, id))
                print(str(url)+" ==== 抓取失败")
                continue

            if html_content:
                extractor = GeneralNewsExtractor()
                try:
                    result = extractor.extract(html_content, noise_node_list=['//div[@class="comment-list"]'])
                except Exception as e:
                    err = "get detail error:" + str(e)
                    retry += 1
                    flag = 0
                    error_count += 1
                    # 更新公司资讯列表
                    update_query = "UPDATE company_bdzixun_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                    cursor.execute(update_query, (0, retry, err, id))
                    print(str(url)+" ==== 抓取失败")
                    continue
                if "百度安全验证" in result['title']:
                    err = "百度安全验证：" + result['content']
                    retry += 1
                    flag = 0
                    error_count += 1
                    # 更新公司资讯列表
                    update_query = "UPDATE company_bdzixun_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                    cursor.execute(update_query, (0, retry, err, id))
                    print(str(url)+" ==== 抓取失败")
                    continue

                title = result['title']
                author = result['author']
                publish_time = result['publish_time']
                content = result['content']
                images = ','.join(result['images'])
                collect_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # 正文入库
                insert_query = "INSERT INTO company_bdzixun_detail (id, company, title, author, publish_time, content, url, images, remark, collect_date) " \
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (id, company, title, author, publish_time, content, url, images, None, collect_time))
                # 更新公司资讯列表
                update_query = "UPDATE company_bdzixun_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                cursor.execute(update_query, (1, retry, err, id))
                conn.commit()
                success_count += 1

                print(str(url)+" ==== 抓取成功")

    print("执行结束 ==> 总条数:" + str(total_count) + ",成功:" + str(success_count) + ",失败:" + str(error_count))
