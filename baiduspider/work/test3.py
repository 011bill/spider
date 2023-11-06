from selenium import webdriver
import pprint
import mysql.connector
import time



filter_words = ['上海', '上海市', '上海公司', '公司上海', '公司信息','公司', '集团', '有限', '责任', '股份', '有限公司', '科技公司', '股份公司', '公司股份', '科技股份',
                '股份有限公司', '有限责任公司', '科技有限公司', '技术有限公司', '信息技术有限公司', '信息科技有限公司', '电子有限公司', '(上海)信息', '公司控股',
                '电子', '软件', '信息', '技术', '科技', '信息技术', '科技信息', '电子信息', '电子技术', '信息科技', '上海科技', '科学技术', '电子上海',
                 '系统', '电动', '控股', '医务', '医药', '医疗', '药物', '通讯', '通信', '投资', '环境', '电商', '电子商务', '网络', '航空', '航空公司', '旅游', '基金',
                '汽车', '光刻', '光刻机', '中国', '中国投资', '光刻设备']
# 连接到MySQL服务器
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="bd_spider",
    connection_timeout=10
)
cursor = conn.cursor()
select_query = "SELECT id, company, simple_name, date FROM company_bdzixun_copy2"
cursor.execute(select_query)
records = cursor.fetchall()

for row in records:
    id, company, simple_name, date = row
    simple_name = simple_name.replace('（', '(').replace('）', ')')
    company = company.replace('（', '(').replace('）', ')')
    # 过滤简称
    if simple_name:
        split = simple_name.replace('\n','').replace(' ','').split(',')
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
        update_query = 'UPDATE company_bdzixun_copy2 SET company = %s, simple_name = %s WHERE id = %s '
        cursor.execute(update_query, (company,string, id))
        conn.commit()
    # 日期格式化
    # if date:
