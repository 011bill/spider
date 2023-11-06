import pandas as pd
import mysql.connector
import time


# 连接到 MySQL 数据库
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="bd_spider"
)

# 查询语句
query = "SELECT * FROM company_bdzixun_copy2"

# 使用 pandas 从 MySQL 数据库中检索数据
data = pd.read_sql(query, con=db_connection)

# 关闭数据库连接
db_connection.close()

# 将数据导出到 Excel 文件
data.to_excel("data.xlsx", index=False)

print("数据已导出到 output.xlsx 文件.")
