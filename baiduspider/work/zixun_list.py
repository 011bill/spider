import time
from baiduspider import BaiduSpider
import pandas as pd
import mysql.connector
import uuid
from datetime import datetime, timedelta

# 过滤简称词典
filter_words = ['上海', '(上海)', '上海(', '北京', '上海市', '上海公司', '公司上海', '公司信息', '公司', '集团', '有限', '责任', '股份',
                '有限公司', '科技公司', '股份公司', '公司股份', '股份有限公司', '有限责任公司', '科技有限公司', '技术有限公司',
                '信息技术有限公司', '信息科技有限公司', '电子有限公司', '(上海)信息', '公司控股', '科技股份',
                '电子', '软件', '信息', '技术', '科技', '信息技术', '科技信息', '电子信息', '电子技术', '电子技术', '信息科技', '上海科技',
                '系统', '电动', '控股', '电商', '电子商务', '网络', '航空', '航空公司', '旅游', '基金', '电子上海', '科学技术',
                '医务', '医药', '药业', '医疗', '制药', '药物', '通讯', '通信', '投资', '环境', '制造', '汽车', '光刻', '光刻机',
                '中国', '中国投资', '光刻设备', '张江', '教育', '建设', '软件开发', '生物', '智能', '工程', '设计', '企业', '研发',
                '生物', '机器人', '金融', '商业', '广告', '管理', '服务', '发展', '保险', '科技(', '医学', '能源', '物联网', '科技上海']

# 日期格式词典
date_formats = [
    "%Y-%m-%d",
    "%Y.%m-%d",
    "%Y-%m-%d %H∶%M",
    "%Y年%m月%d日%H:%M",
    "%Y/%m/%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M",
    "%Y.%m.%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%Y.%m.%d %H:%M:%S",
    "%Y年%m月%d日",
    "%m月%d日",
    "%m月%d日 %H:%M",
    "%m月%d日%H:%M:%S",
    "%m月%d日 %H:%M:%S",
    "%Y年%m月%d日 %H:%M",
    "%Y年%m月%d日%H:%M",
    "%Y/%m/%d",
    "%Y年%m月%d日 %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S",
    "%a %b %d %H:%M:%S",
    "%b %d %H:%M:%S",
]


# 过滤简称
def filter_simple_name(simple_name):
    if simple_name:
        split = simple_name.replace('\n', '').replace(' ', '').split(',')
        unique_list = list(set(split))
        for s in unique_list:
            if len(s) == 1:
                unique_list.remove(s)
            elif company == s:
                unique_list.remove(s)
            elif '公司' in s:
                unique_list.remove(s)
        # 去除unique_list中包含filter_words的元素
        result = [x for x in unique_list if x not in filter_words]
        string = ','.join(result)
        return string


# 日期格式转换
def transform(date_string, type):
    date_string = date_string.strip()   # 去收尾空格
    current_year = datetime.now().year
    date = None
    # 咨询列表 日期格式:%Y-%m-%d
    if type == 1:
        format = '%Y-%m-%d'
        if '年' in date_string:
            # 包含年份的日期格式，例如：2019年12月2日
            date = datetime.strptime(date_string, "%Y年%m月%d日")
        elif '今天' in date_string:
            date = datetime.now()
        elif '昨天' in date_string:
            # 昨天
            date = datetime.now() - timedelta(days=1)
        elif '前天' in date_string:
            # 前天
            date = datetime.now() - timedelta(days=2)
        elif '分钟前' in date_string:
            # X分钟前，例如：50分钟前
            minutes = int(date_string.split('分钟前')[0])
            date = datetime.now() - timedelta(minutes=minutes)
        elif '小时前' in date_string:
            hours = int(date_string.split('小时前')[0])
            date = datetime.now() - timedelta(hours=hours)
        elif '天前' in date_string:
            # X天前，例如：5天前
            days = int(date_string.split('天前')[0])
            date = datetime.now() - timedelta(days=days)
        else:
            # 没有年份的日期格式，例如：5月16日
            date = datetime.strptime(date_string, "%m月%d日")
            date = date.replace(year=current_year)
    # 正文日期格式：%Y-%m-%d %H:%M:%S
    elif type == 2:
        format = '%Y-%m-%d %H:%M:%S'
        for date_format in date_formats:
            try:
                date = datetime.strptime(date_string, date_format)
                if date.year == 1900:
                    date = date.replace(year=current_year)
                break
            except ValueError:
                continue

    return date.strftime(format)


if __name__ == '__main__':
    begin = int(time.time())
    # 指定Excel文件路径
    excel_file = "D:\work\spider\企业信息20240123.xlsx"
    # df = pd.read_excel(excel_file, engine='openpyxl', header=None)  # 不指定列名
    # first_column_data = df.iloc[:, 0]  # 提取第一列的数据
    sheet_name = 'sheet1'
    column_name = '企业名称'
    # 读取指定列的数据
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    # 检查指定列是否存在
    if column_name in df.columns:
        # selected_column = df[df.index >= 721][column_name] #从第几行开始
        selected_column = df[column_name]
    else:
        print("列 '{column_name}' 不存在于工作表 '{sheet_name}' 中。")
    # 将列数据转换为列表
    company_names = selected_column.tolist()
    # company_names = ['雷蛇电脑游戏技术（上海）有限公司']
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bd_spider",
        connection_timeout=10
    )
    cursor = conn.cursor()

    count_all = 0
    count_mysql = 0
    count_fail = 0
    count_data = 0
    for company_name in company_names:
        t = int(time.time())
        count_data += 1
        # 搜索网页
        try:
            time.sleep(5)
            result = BaiduSpider().search_news(company_name, sort_by='time', pn=1).plain
        except Exception as e:
            insert_query = "INSERT INTO company_bdzixun_0123 (id, company, simple_name, title, author, date, des, url, cover, flag, filter, retry, err, remark, collect_date) " \
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
            company = company_name.replace('（', '(').replace('）', ')')
            simple_name = ','.join(data['highlight_font']).replace('（', '(').replace('）', ')')
            if simple_name:
                simple_name = filter_simple_name(simple_name)
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
            select_query = "SELECT * FROM company_bdzixun_0123 WHERE url = %s"
            cursor.execute(select_query, (url,))
            existing_record = cursor.fetchone()

            if existing_record is None:
                insert_query = "INSERT INTO company_bdzixun_0123 (id, company, simple_name, title, author, " \
                               "date, des, url, cover, flag, filter, retry, err, remark, collect_date) " \
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (
                    id, company, simple_name, title, author, date, des, url, cover, 0, 0, 0, None, None, collect_date))
                conn.commit()
                count_mysql += 1
                count_company_mysql += 1
        print(company_name + " ==> 抓取：" + str(count_company) +
              "，入库：" + str(count_company_mysql) + '   耗时：' + str(int(time.time()) - t))

    # 提交更改并关闭连接
    cursor.close()
    conn.close()
    time = int(time.time()) - begin
    print("\n ======================= 执行完成： 公司：" + str(count_data) + "，总条数：" + str(count_all) + "，失败：" + str(count_fail) +
          "，入库：" + str(count_mysql) + "，耗时：" + str(time) + "======================= ")


# 0~200 ==> 943
# 200~400 执行完成：总抓取条数：862，失败：0，入库：807耗时：742
# 399~500 执行完成：共执行 101 家公司，总抓取条数：429，失败：0，入库：383耗时：372
# 500~510 执行完成：共执行 10 家公司，总抓取条数：41，失败：0，入库：37耗时：39
# 510~722
# 722~end  执行完成：共执行 1404 家公司，总抓取条数：3938，失败：0，入库：3021耗时：8092
