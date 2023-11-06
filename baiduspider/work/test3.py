from selenium import webdriver
import pprint
import mysql.connector
import time
from baiduspider.util import convert_time
from baiduspider.work.dateformat import format_date



filter_words = ['上海', '上海市', '上海公司', '公司上海', '公司信息','公司', '集团', '有限', '责任', '股份', '有限公司', '科技公司', '股份公司', '公司股份',
                '股份有限公司', '有限责任公司', '科技有限公司', '技术有限公司', '信息技术有限公司', '信息科技有限公司', '电子有限公司', '(上海)信息', '公司控股',
                '电子', '软件', '信息', '技术', '科技', '信息技术', '科技信息', '电子信息', '电子技术', '电子技术', '信息科技', '上海科技', '科技股份',
                 '系统', '电动', '控股', '电商', '电子商务', '网络', '航空', '航空公司', '旅游', '基金', '电子上海', '科学技术',
                '医务', '医药', '药业', '医疗', '制药', '药物', '通讯', '通信', '投资', '环境', '制造',
                '汽车', '光刻', '光刻机', '中国', '中国投资', '光刻设备', '张江', '教育', '建设', '软件开发', '生物', '智能', '工程', '设计', '企业', '研发',
                '生物', '机器人']
# 连接到MySQL服务器
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="bd_spider",
    connection_timeout=10
)
cursor = conn.cursor()
select_query = "SELECT id, company, simple_name, date FROM company_bdzixun2_copy1"
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
        print(string)
        update_query = 'UPDATE company_bdzixun2_copy1 SET company = %s, simple_name = %s WHERE id = %s '
        cursor.execute(update_query, (company, string, id))
        conn.commit()
    # 日期格式化
    # if date:
    #     d = format_date(date)
    #     update_query = 'UPDATE company_bdzixun2_copy1 SET date = %s WHERE id = %s '
    #     cursor.execute(update_query, (d, id))
    #     conn.commit()



# d = format_date('2022年8月31日')
# d = format_date('4月17日')
# d = format_date('今天')
# d = format_date('昨天')
# d = format_date('前天')
# d = format_date('12小时前')
# d = format_date('12分钟前')
# print(d)
