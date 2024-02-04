import time
import uuid
from urllib.parse import quote
from baiduspider.utils.database import MySQL
from baiduspider.utils.exceluitl import columns_to_list
from baiduspider.utils.proxy import get_proxy, get_spider_data, get_source, push_message
from baiduspider.utils.transform import get_simple_name, filter_simple_name, transform_date, transform_company_name

if __name__ == '__main__':
    begin = int(time.time())
    # 读取公司列表
    excel_data_list = columns_to_list()
    # 设置变量
    total_count = len(excel_data_list)  # 爬取总数
    fail_count = 0  # 失败条数
    total_data_count = 0  # 总爬数据量
    insert_db_count = 0  # 入库数据量
    # 连接mysql
    mysql = MySQL()
    # 表名
    # 添加执行记录
    execute_id = str(uuid.uuid4())
    execute_data = {
        'id': execute_id,
        'start_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'total': total_count
    }
    mysql.insert('execute_log', execute_data)

    print(f'==================== 开始执行，执行总数：{total_count}，开始时间：'
          f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} ====================')

    for company_ in excel_data_list:
        start_time = time.time()
        # time.sleep(1)
        # TODO 取消延迟，轮询爬取多个网站
        website = [
            # 百度
            f"http://www.baidu.com/s?tn=news&wd={quote(company_)}&pn=0&rtt=4&medium=0&cl=2",
            # 搜狗
            f'http://www.sogou.com/sogou?interation=1728053249&interV=&pid=sogou-wsse-8f646834ef1adefa&page=1&ie=utf8&query={quote(company_)}',
            # 360
            f'http://news.so.com/ns?j=0&rank=pdate&src=sort_time&scq=&q={quote(company_)}'
        ]
        # 取出一个代理
        ip_ = get_proxy()
        # 获取资讯列表
        for url in website:
            zixun_list = get_spider_data(company_, ip_, execute_id, url)
            source = get_source(url)
            if zixun_list:
                # 数据入库
                for data in zixun_list:
                    total_data_count += 1
                    # 数据处理
                    company = transform_company_name(company_)
                    simple_name = None
                    if data['highlight']:
                        simple_name = get_simple_name(data['highlight'])
                        simple_name = filter_simple_name(simple_name, company)
                    date = data['date']
                    if date:
                        date = transform_date(date, 1)
                    # 过滤重复资讯
                    # 查询是否已存在相同URL的记录
                    url = data['url']
                    record = mysql.select('zixun', '*', 'url=\'' + url + '\'')
                    if len(record) == 0:
                        insert_zixun_data = {
                            'id': str(uuid.uuid4()),
                            'execute_id': execute_id,
                            'company': company,
                            'simple_name': simple_name,
                            'title': data['title'],
                            'author': data['author'],
                            'date': date,
                            'des': data['des'],
                            'url': url,
                            'cover': data['cover'],
                            'flag': 0,
                            'filter': 0,
                            'retry': 0,
                            'err': None,
                            'source': source,
                            'remark': None,
                            'collect_date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        }
                        mysql.insert('zixun', insert_zixun_data)
                        insert_db_count += 1
        end_time = time.time()
        print(f"单次执行耗时：{end_time - start_time:.6f} 秒")
    # 更新执行记录
    spend_time = int(time.time()) - begin
    execute_data = {
        'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'fail': fail_count,
        'data_count': total_data_count,
        'save_count': insert_db_count,
        'spend_time': spend_time
    }
    mysql.update('execute_log', execute_data, 'id=\'' + execute_id + '\'')
    mysql.close()
    print(f'\n ======================= 执行完成，{total_count}家公司，失败：{fail_count}，总数据量：{total_data_count}，'
          f'入库：{insert_db_count}，结束时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} ====================')
    push_message('执行完成通知',
                 f'执行完成，{total_count}家公司，失败：{fail_count}，总数据量：{total_data_count}，入库：{insert_db_count}')
