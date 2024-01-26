import time
from baiduspider import BaiduSpider
import pandas as pd
import uuid
from baiduspider.work.utils import filter_simple_name, transform, conn_mysql, get_proxy
from baiduspider.work.sql import insert_zixun, select_zixun_by_url, insert_company_log, insert_ban_log

if __name__ == '__main__':
    begin = int(time.time())
    # 指定Excel文件路径
    excel_file = "D:\work\spider\企业信息20240123.xlsx"
    # excel_file = "C:/Users/yxxue/Desktop/企业信息20240123.xlsx"
    # df = pd.read_excel(excel_file, engine='openpyxl', header=None)  # 不指定列名
    # first_column_data = df.iloc[:, 0]  # 提取第一列的数据
    sheet_name = 'Sheet1'
    column_name = '企业名称'
    # 读取指定列的数据
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    # 检查指定列是否存在
    if column_name in df.columns:
        selected_column = df[df.index >= 1007][column_name]  # 从第几行开始
        # selected_column = df[column_name]
    else:
        print("列 '{column_name}' 不存在于工作表 '{sheet_name}' 中。")
    # 将列数据转换为列表
    company_names = selected_column.tolist()
    # company_names = ['国网上海能源互联网研究院有限公司']
    conn = conn_mysql()
    cursor = conn.cursor()

    total_data_count = 0
    insert_db_count = 0
    fail_count = 0
    total_count = len(company_names)
    batch_count = 0
    delay = 1  # 爬取间隔3秒
    ban_delay = 10 * 60  # 封禁延迟10分钟
    start_time = time.localtime()
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", start_time)
    print('==================== 开始执行，执行总数：' + str(total_count) + '，开始时间：' + start_time_str + ' ====================')
    for company_name in company_names:
        # 如果连续爬30分钟，延迟2分钟
        time_difference = (time.mktime(time.localtime()) - time.mktime(start_time)) / 60
        if time_difference > 30:
            print('==================== 已经连续执行30分，休息' + delay + '分 ====================')
            time.sleep(delay * 60)
        t = int(time.time())
        batch_count += 1
        # 搜索网页
        try:
            time.sleep(delay)
            result = BaiduSpider().search_news(company_name, sort_by='time', pn=1).plain
            # proxy = get_proxy().get("proxy")
            # result = BaiduSpider().search_news(company_name, sort_by='time', pn=1,
            #                                    proxies={"http": "http://{}".format(proxy)}).plain
        except Exception as e:
            # 添加爬取失败的公司信息
            cursor.execute(insert_company_log,
                           (str(uuid.uuid4()), company_name, 'error:' + str(e), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            conn.commit()
            fail_count += 1
            print(str(company_name) + " ==> 抓取失败" + '错误信息：' + str(e))
            # 添加百度封禁日志
            if '百度安全验证' == e:
                end_time = time.localtime()
                end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
                cursor.execute(insert_ban_log,
                               (str(uuid.uuid4()), start_time_str, end_time_str, delay, batch_count, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                conn.commit()
                # 被封禁默认延迟10分钟，如果延迟结束时间间隔小与1分钟说明还未解封，则加大延迟
                time_difference = (time.mktime(end_time) - time.mktime(start_time))
                if time_difference < 60:
                    ban_delay += ban_delay
                print('==================== 百度安全验证，延迟' + str(ban_delay) + '分钟后继续，执行条数' +
                      str(batch_count) + '，时间：' + start_time + '~' + end_time + ' ====================')
                time.sleep(ban_delay)
                # 重置开始时间
                start_time = time.localtime()
                start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", start_time)
                batch_count = 0
            continue

        count_company = 0
        count_company_mysql = 0
        for data in result:
            count_company += 1
            total_data_count += 1
            id = str(uuid.uuid4())
            company = company_name.replace('（', '(').replace('）', ')')
            simple_name = ','.join(data['highlight_font']).replace('（', '(').replace('）', ')')
            if simple_name:
                simple_name = filter_simple_name(simple_name, company)
            title = data['title']
            author = data['author']
            date = data['date']
            if date:
                date = transform(date, 1)
            des = data['des']
            url = data['url']
            cover = data['cover']
            collect_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 查询是否已存在相同URL的记录
            cursor.execute(select_zixun_by_url, (url,))
            existing_record = cursor.fetchone()

            if existing_record is None:
                cursor.execute(insert_zixun,
                               (id, company, simple_name, title, author, date, des, url, cover, 0, 0, 0, None, None, collect_date))
                conn.commit()
                insert_db_count += 1
                count_company_mysql += 1
        print(company_name + " ==> 抓取：" + str(count_company) +
              "，入库：" + str(count_company_mysql) + '，耗时：' + str(int(time.time()) - t))

    # 提交更改并关闭连接
    cursor.close()
    conn.close()
    time = int(time.time()) - begin
    print(
        "\n ======================= 执行完成： 公司：" + str(total_count) + "，总条数：" + str(total_data_count) + "，失败：" + str(fail_count) +
        "，入库：" + str(insert_db_count) + "，耗时：" + str(time) + "======================= ")
