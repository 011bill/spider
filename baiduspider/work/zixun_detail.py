import time
from baiduspider import BaiduSpider
from gne import GeneralNewsExtractor
import mysql.connector
from baiduspider.work.utils import search_by_selenium


if __name__ == '__main__':
    begin = int(time.time())
    # 连接到MySQL服务器
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bd_spider",
        connection_timeout=10
    )
    current_page = 1
    page_size = 10
    start = (current_page-1) * page_size
    cursor = conn.cursor()
    # flag(是否爬取到正文：0为爬取，1已爬取)，filter(0：保留，1：过滤)
    select_query = "SELECT id, company, url, retry FROM company_bdzixun2_copy1 WHERE filter = 0 and flag = 0 and retry < 10 limit %s, %s"
    cursor.execute(select_query, (start, page_size))
    records = cursor.fetchall()

    print('==================开始执行 '+str(cursor.rowcount)+'条 =================')
    success_count = 0
    error_count = 0
    total_count = 0
    for row in records:
        start = int(time.time())
        total_count += 1
        id, company, url, retry = row
        err = None
        if url:
            data_url_ = url.replace("https://", "http://")
            time.sleep(3)
            try:
                # if data_url_.find('10jqka.com.cn') != -1 or data_url_.find('cnstock.com') != -1:
                #     html_content = BaiduSpider().search_url(data_url_, encoding='gbk')
                # elif data_url_.find('finance.eastmoney.com') != -1 or data_url_.find('caijing.com.cn') != -1:
                #     html_content = BaiduSpider().search_url(data_url_, encoding='utf-8')
                # elif data_url_.find('baijiahao.baidu.com') != -1:
                #     html_content = search_url_by_selenium(data_url_)
                # else:
                #     html_content = BaiduSpider().search_url(data_url_)
                # html_content = BaiduSpider().search_url(data_url_)
                html_content = search_by_selenium(url)
            except Exception as e:
                err = "get response error:" + str(e)
                retry += 1
                flag = 0
                error_count += 1
                # 更新公司资讯列表
                update_query = "UPDATE company_bdzixun2_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                cursor.execute(update_query, (0, retry, err, id))
                conn.commit()
                print(str(total_count) + ' ' + str(url) + ' == 爬取网页失败, error:' + str(e))
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
                    update_query = "UPDATE company_bdzixun2_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                    cursor.execute(update_query, (0, retry, err, id))
                    print(str(total_count)+' '+str(url)+" == 正文抽取失败，error:" + str(e))
                    continue
                if "百度安全验证" in result['title']:
                    err = "百度安全验证：" + result['content']
                    retry += 1
                    flag = 0
                    error_count += 1
                    # 更新公司资讯列表
                    update_query = "UPDATE company_bdzixun2_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                    cursor.execute(update_query, (0, retry, err, id))
                    print(str(total_count)+' '+str(url)+" == 正文抽取失败，error:" + str(err))
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
                update_query = "UPDATE company_bdzixun2_copy1 SET flag = %s, retry = %s, err = %s WHERE id = %s"
                cursor.execute(update_query, (1, retry, err, id))
                conn.commit()
                success_count += 1
                print(str(total_count)+' '+str(url)+' == 正文抽取并入库成功' + ",耗时：" + str(int(time.time()) - start))
    cursor.close()
    conn.close()
    print("执行结束 ==> 总条数:" + str(total_count) + ",成功:" + str(success_count) + ",失败:" + str(error_count) +
          ",耗时：" + str(int(time.time()) - begin))

# 1~50