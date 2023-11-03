import mysql.connector

# 连接到MySQL服务器
conn = mysql.connector.connect(
    host="localhost",  # MySQL服务器地址
    user="root",  # 您的用户名
    password="root"  # 您的密码
)

# 创建一个数据库
cursor = conn.cursor()
database_name = "bd_spider"
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

# 使用新数据库
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database=database_name  # 指定要使用的数据库
)
cursor = conn.cursor()

# 创建表
create_table_query = """
CREATE TABLE IF NOT EXISTS company_bdzixun (
    id VARCHAR(50) PRIMARY KEY,
    company VARCHAR(255),
    simple_name VARCHAR(255),
    title VARCHAR(255),
    author VARCHAR(50),
    date VARCHAR(50),
    des TEXT,
    url VARCHAR(255),
    cover VARCHAR(255),
    flag VARCHAR(1),
    filter VARCHAR(1),
    retry INT ,
    err VARCHAR(255),
    remark VARCHAR(255),
    collect_date DATETIME
);
CREATE TABLE IF NOT EXISTS company_bdzixun_detail (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(50),
    publish_time VARCHAR(255),
    content LONGTEXT,
    images VARCHAR(500),
    url VARCHAR(255),
    company VARCHAR(255),
    remark VARCHAR(255),
    collect_date DATETIME
)
"""
cursor.execute(create_table_query)

# 关闭连接
cursor.close()
conn.close()
