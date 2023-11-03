# 导入BaiduSpider
import time

from baiduspider import BaiduSpider
from pprint import pprint
import pandas as pd
import openpyxl
import json
import mysql.connector
import uuid


# 标题内容问题（404，下载app），高亮字体，异常数据分析
# 是否爬取
if __name__ == '__main__':
    # 指定Excel文件路径
    excel_file = "D:\work\企业名称.xlsx"
    # 读取Excel文件
    df = pd.read_excel(excel_file, engine='openpyxl', header=None)  # 不指定列名
    # 提取第一列的数据
    first_column_data = df.iloc[:, 0]
    # 将列数据转换为列表
    company_names = first_column_data.tolist()
    # 打印企业名称列表
    dataList = []
    # 连接到MySQL服务器
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bd_spider",
        connection_timeout=10
    )
    # 创建游标
    cursor = conn.cursor()

    count_all = 0
    count_mysql = 0
    for name in company_names:
        # 实例化BaiduSpider
        spider = BaiduSpider()
        # 搜索网页
        try:
            result = spider.search_news(name, sort_by='time', pn=5).plain
        except Exception:
            print(str(name) + " ===> 抓取数据失败")
        count_company = 0
        count_company_mysql = 0
        for data in result:
            count_company += 1
            count_all += 1
            # pprint(data)
            id = str(uuid.uuid4())
            company = name
            simple_name = ','.join(data['highlight_font'])
            title = data['title']
            author = data['author']
            date = data['date']
            des = data['des']
            url = data['url']
            cover = data['cover']
            collect_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # 查询是否已存在相同URL的记录
            select_query = "SELECT * FROM company_bdzixun WHERE url = %s"
            cursor.execute(select_query, (url,))
            existing_record = cursor.fetchone()

            if existing_record is None:
                insert_query = "INSERT INTO company_bdzixun (id, company, simple_name, title, author, date, des, url, cover, flag, filter, retry, err, remark, collect_date) " \
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (id, company, simple_name, title, author, date, des, url, cover, 0, 0, 0, None, None, collect_date))
                conn.commit()
                count_mysql += 1
                count_company_mysql += 1
        time.sleep(1)
        print(name+" ==> 抓取条数：" + str(count_company) + "，入库条数：" + str(count_company_mysql))


    # 提交更改并关闭连接
    cursor.close()
    conn.close()
    print(" ============= 执行完成 ============= \n 总抓取条数："+str(count_all)+"，导入mysql条数：" + str(count_mysql))
