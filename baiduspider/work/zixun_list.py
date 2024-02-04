import random
import time
from baiduspider import BaiduSpider
import pandas as pd
import uuid
from baiduspider.work.utils import filter_simple_name, transform, conn_mysql, get_proxy, delete_proxy
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
        # selected_column = df[df.index >= 1753][column_name]  # 从第几行开始
        selected_column = df[column_name]
    else:
        print("列 '{column_name}' 不存在于工作表 '{sheet_name}' 中。")
    # 将列数据转换为列表
    company_names = selected_column.tolist()
    # company_names = ['国网上海能源互联网研究院有限公司']
    conn = conn_mysql()
    cursor = conn.cursor()

    strategy = 2  # 1延迟；2代理
    total_count = len(company_names)  # 爬取数据总数量
    total_data_count = 0
    insert_db_count = 0
    fail_count = 0
    batch_count = 0
    delay_min = 1
    delay_max = 10
    ban_delay = 30 * 60  # 封禁延迟30分钟
    act_start_time = time.localtime()
    start_time = time.localtime()
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", start_time)
    print('==================== 开始执行，执行总数：' + str(total_count) + '，开始时间：' + start_time_str + ' ====================')
    for company_name in company_names:
        if strategy == 1:
            proxy = None  # 代理
            delay = random.randint(delay_min, delay_max)  # 爬取间隔
            # 如果连续爬10分钟，随机暂停0~10分
            time_difference = (time.mktime(time.localtime()) - time.mktime(act_start_time)) / 60
            if time_difference > 10:
                print('==================== 已经连续执行10分，暂停' + str(delay) + '分，' + time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                              time.localtime()) + ' ====================')
                time.sleep(delay * 60)
                act_start_time = time.localtime()
        else:
            p = get_proxy().get("proxy")  # ip池随机获取一个ip
            proxy = {"http": "http://{}".format(p)}
            delay = random.randint(1, 3)  # 爬取间隔
        # 搜索网页
        try:
            t = int(time.time())
            time.sleep(delay)
            result = BaiduSpider().search_news(company_name, sort_by='time', pn=1, proxies=proxy).plain
        except Exception as e:
            # 添加爬取失败的公司信息
            cursor.execute(insert_company_log,
                           (str(uuid.uuid4()), company_name, 'error:' + str(e), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            conn.commit()
            fail_count += 1
            print(str(company_name) + " ==> 抓取失败，" + '错误信息：' + str(e) + "，" + str(proxy))
            # 添加百度封禁日志
            if '百度安全验证' == str(e) and strategy == 1:
                end_time = time.localtime()
                end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
                cursor.execute(insert_ban_log,
                               (str(uuid.uuid4()), start_time_str, end_time_str, str(delay_min) + '~' + str(delay_max),
                                batch_count, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                conn.commit()
                # 被封禁默认延迟10分钟，如果延迟结束时间间隔小与1分钟说明还未解封，则加大延迟
                time_difference = (time.mktime(end_time) - time.mktime(start_time))
                if time_difference < 10 * 60:
                    ban_delay += ban_delay
                else:
                    ban_delay = 30 * 60
                print('==================== 百度安全验证，延迟' + str(ban_delay / 60) + '分钟后继续，本次执行条数：' +
                      str(batch_count) + '，时间：' + start_time_str + '~' + end_time_str + ' ====================')
                time.sleep(ban_delay)
                # 重置开始时间
                act_start_time = time.localtime()
                start_time = time.localtime()
                start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", start_time)
                batch_count = 0
            else:
                delete_proxy(p)
            continue

        batch_count += 1
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
                               (id, company, simple_name, title, author, date, des, url, cover, 0, 0, 0, None, None,
                                collect_date))
                conn.commit()
                insert_db_count += 1
                count_company_mysql += 1
        print(company_name + " ==> 抓取：" + str(count_company) +
              "，入库：" + str(count_company_mysql) + '，耗时：' + str(int(time.time()) - t) + "，" + str(proxy))

    # 提交更改并关闭连接
    cursor.close()
    conn.close()
    time = int(time.time()) - begin
    print(
        "\n ======================= 执行完成： 公司：" + str(total_count) + "，总条数：" + str(total_data_count) + "，失败：" + str(
            fail_count) +
        "，入库：" + str(insert_db_count) + "，耗时：" + str(time) + "======================= ")
