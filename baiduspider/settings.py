# 数据库信息配置
DATABASE = 'spider'
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': DATABASE
}

# excel路径
# EXCEL_PAHT = 'D:/work/spider/企业信息20240123.xlsx'
EXCEL_PAHT = 'D:/work/spider/企业名称.xlsx'
READ_COLUMN = '企业名称'

# 熊猫代理
URL_PROXY = 'http://route.xiongmaodaili.com/xiongmao-web/api/glip?' \
            'secret=351c271365f514b36e71004731706ec7&' \
            'orderNo=GL20240130102547J610iY4D&' \
            'count=1&' \
            'isTxt=0&' \
            'proxyType=1&' \
            'returnAccount=1'

# 消息推送地址
URL_PUSH = 'https://www.pushplus.plus/send/'
TOKEN = '2d54af40b0344b45b93275c13d07dc33'

