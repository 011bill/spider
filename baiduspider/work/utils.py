from selenium import webdriver
import mysql.connector
from datetime import datetime, timedelta
import pandas as pd
from selenium.webdriver.chrome.service import Service


filter_words = ['上海', '(上海)', '上海(', '北京', '上海市', '上海公司', '公司上海', '公司信息', '公司', '集团', '有限', '责任', '股份',
                '有限公司', '科技公司', '股份公司', '公司股份', '股份有限公司', '有限责任公司', '科技有限公司', '技术有限公司',
                '信息技术有限公司', '信息科技有限公司', '电子有限公司', '(上海)信息', '公司控股', '科技股份',
                '电子', '软件', '信息', '技术', '科技', '信息技术', '科技信息', '电子信息', '电子技术', '电子技术', '信息科技', '上海科技',
                '系统', '电动', '控股', '电商', '电子商务', '网络', '航空', '航空公司', '旅游', '基金', '电子上海', '科学技术',
                '医务', '医药', '药业', '医疗', '制药', '药物', '通讯', '通信', '投资', '环境', '制造', '汽车', '光刻', '光刻机',
                '中国', '中国投资', '光刻设备', '张江', '教育', '建设', '软件开发', '生物', '智能', '工程', '设计', '企业', '研发',
                '生物', '机器人', '金融', '商业', '广告', '管理', '服务', '发展', '保险', '科技(', '医学', '能源']


def conn_mysql():
    # 连接到MySQL服务器
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bd_spider",
        connection_timeout=10
    )


# 过滤简称
def filter_simple_name():
    conn = conn_mysql()
    cursor = conn.cursor()

    select_query = "SELECT id, company, simple_name, date FROM company_bdzixun_copy1"
    cursor.execute(select_query)
    records = cursor.fetchall()

    for row in records:
        id, company, simple_name, date = row
        simple_name = simple_name.replace('（', '(').replace('）', ')')
        company = company.replace('（', '(').replace('）', ')')
        # 过滤简称
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
            result = [x for x in unique_list if x not in filter_words]
            string = ','.join(result)
            update_query = 'UPDATE company_bdzixun_copy1 SET company = %s, simple_name = %s WHERE id = %s '
            cursor.execute(update_query, (company, string, id))
            conn.commit()
            print(id+'  ' + simple_name + '==>' + string)
    # 关闭连接
    cursor.close()
    conn.close()


# 格式化日期
def transform_date():
    conn = conn_mysql()
    cursor = conn.cursor()

    select_query = "SELECT id, date FROM company_bdzixun_copy1"
    cursor.execute(select_query)
    records = cursor.fetchall()
    for row in records:
        id, date = row
        if date:
            d = transform(date)
            update_query = 'UPDATE company_bdzixun_copy1 SET date = %s WHERE id = %s '
            cursor.execute(update_query, (d, id))
            conn.commit()
            print(id+'  ' + date + '==>' + str(d))
    # 关闭连接
    cursor.close()
    conn.close()


def export_excel():
    conn = conn_mysql()
    # 查询语句
    query = "SELECT * FROM company_bdzixun_detail_test"
    # 使用 pandas 从 MySQL 数据库中检索数据
    data = pd.read_sql(query, con=conn)
    # 关闭数据库连接
    conn.close()
    # 将数据导出到 Excel 文件
    data.to_excel("../../data.xlsx", index=False)
    print("数据已导出到 data.xlsx 文件.")


def transform(date_string):
    current_year = datetime.now().year

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

    return date.strftime("%Y-%m-%d")


# 启动浏览器的无头模式 chromedriver下载地址：https://googlechromelabs.github.io/chrome-for-testing/
def search_by_selenium(url):
    service = Service(executable_path=r'../../chromedriver/win64-119/chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    # 获取页面的源代码
    page_source = driver.page_source
    driver.quit()
    return page_source
    # # 我们并不需要浏览器弹出
    # options = Options()
    # options.headless = True
    # # 启动浏览器的无头模式，访问
    # # ========================================
    # # 注意：这是Selenium 4.10.0以下写法，高版本见下面
    # # ========================================
    # driver = webdriver.Chrome('D:\work\chromedriver-win64\chromedriver-win64\chromedriver.exe', options=options)
    # # s = Service('D:\work\chromedriver-win64\chromedriver-win64\chromedriver.exe')
    # # driver = webdriver.Chrome(service=s, options=options)
    # driver.get(url)
    # # 获取页面的源代码
    # page_source = driver.page_source
    # driver.quit()
    # return page_source


def import_excel(path):
    df = pd.read_excel(path)
    conn = conn_mysql()
    cursor = conn.cursor()
    update_query = 'UPDATE company_bdzixun2_copy1 SET filter = %s WHERE id = %s '
    for index, row in df.iterrows():
        id_ = row['id']
        filter_ = row['filter1']
        if filter_ == 0:
            filter_ = 1
        else:
            filter_ = 0
        cursor.execute(update_query, (filter_, id_))
        print(id_+'  ==>  filter:'+str(filter_))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()