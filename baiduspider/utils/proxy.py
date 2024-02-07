import random
import time
import uuid
import requests
from urllib.parse import quote
from baiduspider import BaiduSpider
from baiduspider.settings import URL_PROXY, URL_PUSH, TOKEN
from baiduspider.utils.database import MySQL


def get_proxy():
    mysql = MySQL()
    # 查询在有效期内的代理
    select = mysql.select('proxy_log', ['proxy'], 'TIMESTAMPDIFF(MINUTE, create_date, NOW())<expire and status=1 and fail<3')
    mysql.close()
    if select:
        ip_ = select[0][0]
    else:
        ip_ = get_xiongmao_proxy(0)  # 取出一个代理
    return ip_


# 熊猫代理 https://www.xiongmaodaili.com/
def get_xiongmao_proxy(retry_count):
    # 重试次数，如果连续取出10个ip都不可用，发送通知
    retry_count += 1
    # 开始生效时间
    get_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    response = requests.get(URL_PROXY, verify=False, allow_redirects=False)
    # 检查响应状态码
    if response.status_code == 200:
        data = response.json()
        # 检查是否存在有效的数据
        if 'obj' in data and isinstance(data['obj'], list) and len(data['obj']) > 0:
            ip = data['obj'][0].get('ip')
            port = data['obj'][0].get('port')
            # 检查IP和端口是否存在
            if ip and port:
                result = f'{ip}:{port}'
                # 检查代理是否可用
                if check_proxy(result, get_time):
                    return result
                else:
                    if retry_count % 5 == 0:
                        push_message('熊猫代理通知', f'已连续取出{retry_count}个无效代理，将暂停10分钟，请注意查看！')
                        time.sleep(10 * 60)
                    print('重新获取代理...')
                    get_xiongmao_proxy(retry_count)
            else:
                print('Error: Missing IP or port in the response')
        else:
            print('Error: Missing or invalid data in the response')
    else:
        print(f'Error: {response.status_code}')


def push_message(title, message):
    data = {
        "token": TOKEN,
        "title": title,
        "content": message
    }
    response = requests.post(URL_PUSH, json=data)
    if response.status_code == 200:
        print("消息推送成功:", response.text)
    else:
        print("消息推送失败:", response.text)


HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*', 'Connection': 'keep-alive', 'Accept-Language': 'zh-CN,zh;q=0.8'}


def check_proxy(proxy_, get_time):
    status = 0
    message = 'success'
    proxies = {"http": "http://{proxy}".format(proxy=proxy_)}
    try:
        r = requests.get("http://www.baidu.com/", headers=HEADER, proxies=proxies, timeout=10)
        if r.status_code == 200 and len(r.content) > 200:
            status = 1
            return True
        else:
            message = f'error: status_code:{r.status_code},content:{r.content}'
            return False
    except Exception as e:
        message = f'error:{e}'
        return False
    finally:
        # 保存记录
        mysql = MySQL()
        proxy_data = {
            'id': str(uuid.uuid4()),
            'proxy': proxy_,
            'status': status,
            'message': message,
            'source': 'https://www.xiongmaodaili.com/',
            'expire': 5,
            'fail': 0,
            'create_date': get_time
        }
        mysql.insert('proxy_log', proxy_data)
        mysql.close()
        print(f'代理：{proxy_}，状态：{message}')


def get_source(url):
    if 'www.baidu.com' in url:
        return '百度'
    if 'www.sogou.com' in url:
        return '搜狗'
    if 'news.so.com' in url:
        return '360'


def get_spider_data(company_, ip_, execute_id, url):
    source = get_source(url)
    proxy = None
    if ip_:
        proxy = {"http": "http://{}".format(ip_)}
    retry_count = 3  # 重试次数
    status = 1
    message = 'success'
    while retry_count > 0:
        try:
            parse_data = []
            response = BaiduSpider().get_response(url, proxy)
            # 解析html
            try:
                parse_data = BaiduSpider().parse_html(response, source).plain
                status = 1
                message = 'success'
                return parse_data
            except Exception as e:
                status = 0
                message = f'error: {e}'
                return None
        except Exception as e:
            retry_count -= 1
            status = 0
            message = f'error:{e}'
        finally:
            # 添加成功或失败日志
            if retry_count == 0 or status == 1:
                mysql = MySQL()
                zixun_log_data = {
                    'id': str(uuid.uuid4()),
                    'execute_id': execute_id,
                    'company': company_,
                    'status': status,
                    'message': message,
                    'source': source,
                    'use_proxy': 1 if proxy else 0,
                    'create_date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                mysql.insert('zixun_log', zixun_log_data)
                mysql.close()
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}，{company_} --> {message}，'
                      f'目标网站：{source}，条数：{len(parse_data)} ')
    return None


def get_spider_data(ip_, url):
    source = get_source(url)
    proxy = None
    if ip_:
        proxy = {"http": "http://{}".format(ip_)}
    retry_count = 3  # 重试次数
    # 失败重试
    while retry_count > 0:
        try:
            response = BaiduSpider().get_response(url, proxy)
            # 解析html
            parse_data = BaiduSpider().parse_html(response, source).plain
            return parse_data
        except Exception as e:
            retry_count -= 1
            if retry_count == 0:
                raise e


# get_spider_data('丹华水利环境技术（上海）有限公司', None, '',
#                 f'http://news.so.com/ns?j=0&rank=pdate&src=sort_time&scq=&q={quote("丹华水利环境技术（上海）有限公司")}')
# get_spider_data('联想（上海）计算机科技有限公司', None, '',
#                 f'http://www.sogou.com/sogou?interation=1728053249&interV=&pid=sogou-wsse-8f646834ef1adefa&page=1&ie=utf8&query={quote("联想（上海）计算机科技有限公司")}')

# url = 'https://www.sogou.com/link?url=LeoKdSZoUyBbNIk-BraG2Ssi_ilAVudj8YtXrd2wnsKzbYJU-Jfo5Un6ySK7MTmd&k=35&h=T'
# resp = requests.get(url,headers=HEADER)
#
# print(resp.content.decode('utf8'))

# print(check_proxy('123.245.249.128:14836', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

# proxy = {"http": "http://{}".format('42.177.116.235:12882')}
# response = BaiduSpider().get_response(f'http://news.so.com/ns?j=0&rank=pdate&src=sort_time&scq=&q={quote("丹华水利环境技术（上海）有限公司")}',
#                                       proxy)
# print(response)