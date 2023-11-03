import requests
import chardet
import mysql.connector

# data_url_ = 'http://stock.10jqka.com.cn/20221121/c643081110.shtml'
# data_url_ = 'http://news.10jqka.com.cn/20230802/c43698127.shtml'
# data_url_ = 'http://stock.10jqka.com.cn/20221226/c643852486.shtml'
# data_url_ = 'http://www.eet-china.com/mp/a256178.html'
data_url_ = 'http://m.10jqka.com.cn/sn/20231030/44914999.shtml'
# url = str(input('输入要获取编码的网站'))
# req = requests.get(data_url_)
# html = req.content
# chardet = chardet.detect(html)['encoding']
# print(chardet)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="bd_spider",
    connection_timeout=10
)
cursor = conn.cursor()
select_query = "SELECT id, company, url FROM company_bdzixun WHERE filter = 0 and flag = 0 and retry < 10"
cursor.execute(select_query)
records = cursor.fetchall()
for row in records:
    id, company, url = row
    print(id,company)
