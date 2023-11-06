# 导入BaiduSpider
import time

from baiduspider import BaiduSpider
import pandas as pd
import mysql.connector
import uuid

# 标题内容问题（404，下载app），高亮字体，异常数据分析
# 是否爬取
if __name__ == '__main__':
    begin = int(time.time())
    # 指定Excel文件路径
    excel_file = "D:\work\重点企业工商信息(1).xlsx"
    # df = pd.read_excel(excel_file, engine='openpyxl', header=None)  # 不指定列名
    # first_column_data = df.iloc[:, 0]  # 提取第一列的数据
    sheet_name = '照面信息'
    column_name = '企业名称'
    # 读取指定列的数据
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    # 检查指定列是否存在
    if column_name in df.columns:
        selected_column = df[column_name].iloc[399:500]
    else:
        print(f"列 '{column_name}' 不存在于工作表 '{sheet_name}' 中。")
    # 将列数据转换为列表
    company_names = selected_column.tolist()
    # 打印企业名称列表
    # company_names = ['雷蛇电脑游戏技术（上海）有限公司']
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
    count_fail = 0
    count_data = 0
    for company_name in company_names:
        count_data += 1
        # 搜索网页
        try:
            time.sleep(3)
            result = BaiduSpider().search_news(company_name, sort_by='time', pn=1).plain
        except Exception as e:
            insert_query = "INSERT INTO company_bdzixun2 (id, company, simple_name, title, author, date, des, url, cover, flag, filter, retry, err, remark, collect_date) " \
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (
                str(uuid.uuid4()), company_name, None, None, None, None, None, None, None, -1, 0, 0, e, None,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            conn.commit()
            count_fail += 1
            print(str(company_name) + " ===> 抓取数据失败")

        count_company = 0
        count_company_mysql = 0
        for data in result:
            count_company += 1
            count_all += 1
            id = str(uuid.uuid4())
            company = company_name
            simple_name = ','.join(data['highlight_font'])
            title = data['title']
            author = data['author']
            date = data['date']
            des = data['des']
            url = data['url']
            cover = data['cover']
            collect_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 查询是否已存在相同URL的记录
            select_query = "SELECT * FROM company_bdzixun2 WHERE url = %s"
            cursor.execute(select_query, (url,))
            existing_record = cursor.fetchone()

            if existing_record is None:
                insert_query = "INSERT INTO company_bdzixun2 (id, company, simple_name, title, author, " \
                               "date, des, url, cover, flag, filter, retry, err, remark, collect_date) " \
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (
                    id, company, simple_name, title, author, date, des, url, cover, 0, 0, 0, None, None, collect_date))
                conn.commit()
                count_mysql += 1
                count_company_mysql += 1
        print(company_name + " ==> 抓取条数：" + str(count_company) + "，入库条数：" + str(count_company_mysql))

    # 提交更改并关闭连接
    cursor.close()
    conn.close()
    time = int(time.time()) - begin
    print("\n ======================= 执行完成：共执行 " + str(count_data) + " 家公司，总抓取条数：" + str(count_all) + "，失败：" + str(count_fail) +
          "，入库：" + str(count_mysql) + "耗时：" + str(time) + "======================= " )


# 0~200 ==> 943
# 200~400 执行完成：总抓取条数：862，失败：0，入库：807耗时：742
# 399~500 执行完成：共执行 101 家公司，总抓取条数：429，失败：0，入库：383耗时：372