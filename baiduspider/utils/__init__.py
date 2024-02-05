import mysql.connector
from baiduspider.settings import DATABASE, DB_CONFIG

# 连接到MySQL服务器
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
)

# 创建一个数据库
cursor = conn.cursor()
database_name = DATABASE
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

# 使用新数据库
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# 创建表
create_table_query = """
CREATE TABLE IF NOT EXISTS zixun (
    id VARCHAR(50) PRIMARY KEY,
    execute_id varchar(50) COMMENT '执行记录id',
    company VARCHAR(255) COMMENT '公司名',
    simple_name VARCHAR(255) COMMENT '简称',
    title VARCHAR(255) COMMENT '标题',
    author VARCHAR(50) COMMENT '作者',
    date VARCHAR(50) COMMENT '发布日期',
    des TEXT COMMENT '描述',
    url VARCHAR(500) COMMENT '详情链接',
    cover VARCHAR(500) COMMENT '封面图',
    flag VARCHAR(2) COMMENT '详情是否已爬（0否，1是）',
    filter VARCHAR(1) COMMENT '是否过滤/是否爬详情（0否，1是）',
    retry INT  COMMENT '爬取详情重试次数',
    err VARCHAR(255) COMMENT '爬取详情错误信息',
    source VARCHAR(255) COMMENT '来源',
    remark VARCHAR(255) COMMENT '备注',
    collect_date DATETIME COMMENT '采集时间'
);
CREATE TABLE IF NOT EXISTS zixun_detail (
    id VARCHAR(50) PRIMARY KEY COMMENT '资讯id',
    title VARCHAR(255) COMMENT '标题',
    author VARCHAR(50) COMMENT '作者',
    publish_time VARCHAR(255) COMMENT '发布时间',
    content LONGTEXT COMMENT '正文',
    images TEXT COMMENT '图片',
    url VARCHAR(255) COMMENT '详情链接',
    company VARCHAR(255) COMMENT '公司名',
    remark VARCHAR(255) COMMENT '备注',
    collect_date DATETIME COMMENT '采集时间'
);
CREATE TABLE IF NOT EXISTS execute_log (
  id varchar(50) PRIMARY KEY,
  start_time datetime COMMENT '开始时间',
  end_time datetime COMMENT '结束时间',
  total int COMMENT '执行总数',
  fail int COMMENT '失败条数',
  data_count int COMMENT '总爬取数据条数',
  save_count int COMMENT '入库数据条数',
  spend_time int COMMENT '耗时（秒）',
  remark varchar(255) COMMENT '备注'
);
CREATE TABLE IF NOT EXISTS proxy_log (
  id varchar(50) PRIMARY KEY,
  proxy varchar(50) COMMENT '代理',
  status varchar(1) COMMENT '状态 0不可用，1可用',
  message text COMMENT '信息',
  source varchar(255) COMMENT '来源',
  expire int COMMENT '有效期（分）',
  fail int COMMENT '失败条数',
  create_date datetime COMMENT '时间'
);
CREATE TABLE IF NOT EXISTS zixun_log (
  id varchar(50) PRIMARY KEY,
  execute_id varchar(50) COMMENT '执行id',
  company varchar(255) COMMENT '公司',
  status varchar(1) COMMENT '状态 0失败，1成功',
  message text COMMENT '信息',
  source varchar(255) COMMENT '来源',
  use_proxy varchar(1) COMMENT '使用代理（0未使用，1使用）',
  create_date datetime COMMENT '时间'
);
"""
cursor.execute(create_table_query)

# 关闭连接
cursor.close()
conn.close()
