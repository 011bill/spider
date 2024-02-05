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
        # 取消延迟，轮询爬取多个网站
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
        # 打印日志变量
        count_baidu = 0
        count_sougou = 0
        count_360 = 0
        source_list = []
        status = 1
        message = 'success'
        index = 0
        # 获取资讯列表
        for url in website:
            source = get_source(url)
            # zixun_list = get_spider_data(company_, ip_, execute_id, url)
            zixun_list = []
            try:
                zixun_list = get_spider_data(ip_, url)
            except Exception as e:
                index += 1
                # 所有网站都爬取失败
                if index == len(website):
                    status = 0
                    message = f'error:{e}'
                    select = mysql.select('proxy_log', ['fail'], f'proxy=\'{ip_}\'')
                    fail = select[0][0]
                    fail += 1
                    mysql.update('proxy_log', {'fail': fail}, f'proxy=\'{ip_}\'')
                continue
            source_list.append(source)
            if '百度' == source:
                count_baidu = len(zixun_list)
            if '搜狗' == source:
                count_sougou = len(zixun_list)
            if '360' == source:
                count_360 = len(zixun_list)
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
                save_count = 0
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
                    save_count += 1
        # 添加日志
        zixun_log = {
            'id': str(uuid.uuid4()),
            'execute_id': execute_id,
            'company': company_,
            'status': status,
            'message': message,
            'source': ','.join(map(str, source_list)),
            'use_proxy': 1 if ip_ else 0,
            'create_date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        mysql.insert('zixun_log', zixun_log)
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}，{company_}，耗时：{time.time() - start_time:.1f}秒'
              f' --> {message}， 数据 --> 百度：{count_baidu}， 搜狗：{count_sougou}， 360：{count_360}')
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
    print(f'\n ======================= 执行完成，{total_count}家公司，失败：{fail_count}，总数据量：{total_data_count}，入库：{insert_db_count}，'
          f'耗时：{spend_time/60:.1f}分，结束时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} ====================')
    push_message('执行完成通知',
                 f'执行完成，{total_count}家公司，失败：{fail_count}，总数据量：{total_data_count}，入库：{insert_db_count}')
