from datetime import datetime, timedelta


date_formats = ["%Y-%m-%d", "%Y.%m-%d", "%Y-%m-%d %H∶%M", "%Y年%m月%d日%H:%M", "%Y/%m/%d %H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M", "%Y.%m.%d %H:%M", "%Y/%m/%d %H:%M:%S",
                "%Y.%m.%d %H:%M:%S",
                "%m月%d日", "%m月%d日 %H:%M", "%m月%d日%H:%M:%S", "%m月%d日 %H:%M:%S", "%Y年%m月%d日 %H:%M",
                "%Y年%m月%d日%H:%M",
                "%Y/%m/%d", "%Y年%m月%d日", "%Y年%m月%d日 %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%a %b %d %H:%M:%S", "%b %d %H:%M:%S"]

filter_words = ['上海', '(上海)', '上海(', '(上海', '北京', '上海市', '上海公司', '公司上海', '公司信息', '公司', '集团', '有限', '责任',
                '有限公司', '科技公司', '股份公司', '公司股份', '股份有限公司', '有限责任公司', '科技有限公司', '技术有限公司', '股份',
                '信息技术有限公司', '信息科技有限公司', '电子有限公司', '(上海)信息', '公司控股', '科技股份', '科技(上海)', '半导体(上海)',
                '电子', '软件', '信息', '技术', '科技', '信息技术', '科技信息', '电子信息', '电子技术', '电子技术', '信息科技', '上海科技',
                '系统', '电动', '控股', '电商', '电子商务', '网络', '航空', '航空公司', '旅游', '基金', '电子上海', '科学技术', '半导体',
                '制药', '药物', '通讯', '通信', '投资', '环境', '制造', '汽车', '光刻', '光刻机', '医务', '医药', '药业', '医疗',
                '中国', '中国投资', '光刻设备', '张江', '教育', '建设', '软件开发', '生物', '智能', '工程', '设计', '企业', '研发',
                '生物', '机器人', '金融', '商业', '广告', '管理', '服务', '发展', '保险', '科技(', '医学', '能源', '物联网', '科技上海',
                '卫星', '中心', '学校', '民办', '科学', '科学院', '银行', '征信', '研究所', '销售', '芯', '人工智能', '生物科技', '生物技术',
                '网络科技', '服饰', '创新', '旅游', '健康', '医疗健康', '电子(', '产业', '上海)', '开发', '文化', '食品', '化妆品', '化学',
                '新材料', '安全', '创业', '检测', '新能源', '集成电路', '研究中心', '医疗器械', '互联网', '农业', '医药有限公司', '农业',
                '生物(', '设备', '材料', '(有限']


# 过滤简称
def filter_simple_name(simple_name, company):
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
        # 去除unique_list中包含filter_words的元素
        result = [x for x in unique_list if x not in filter_words]
        string = ','.join(result)
        return string


# 格式化日期 type=1 咨询列表, type=2 正文
def transform_date(date_string, type):
    date_string = date_string.strip()
    current_year = datetime.now().year
    date = None
    # 咨询列表 日期格式:%Y-%m-%d
    if type == 1:
        format = '%Y-%m-%d'
        if '年' in date_string:
            # 包含年份的日期格式，例如：2019年12月2日
            date = datetime.strptime(date_string, "%Y年%m月%d日")
        elif '今天' in date_string:
            date = datetime.now()
        elif '昨天' in date_string:
            # 昨天
            date = datetime.now() - timedelta(days=1)
        elif '前天' in date_string:
            # 前天
            date = datetime.now() - timedelta(days=2)
        elif '分钟前' in date_string:
            # X分钟前，例如：50分钟前
            minutes = int(date_string.split('分钟前')[0])
            date = datetime.now() - timedelta(minutes=minutes)
        elif '小时前' in date_string:
            hours = int(date_string.split('小时前')[0])
            date = datetime.now() - timedelta(hours=hours)
        elif '天前' in date_string:
            # X天前，例如：5天前
            days = int(date_string.split('天前')[0])
            date = datetime.now() - timedelta(days=days)
        elif '年' not in date_string and '月' in date_string and '日' in date_string:
            # 没有年份的日期格式，例如：5月16日
            date = datetime.strptime(date_string, "%m月%d日")
            date = date.replace(year=current_year)
        elif ':' in date_string:
            date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
        else:
            date = datetime.strptime(date_string, "%Y-%m-%d")
    # 正文日期格式：%Y-%m-%d %H:%M:%S
    elif type == 2:
        format = '%Y-%m-%d %H:%M:%S'
        for date_format in date_formats:
            try:
                date = datetime.strptime(date_string, date_format)
                if date.year == 1900:
                    date = date.replace(year=current_year)
                break
            except ValueError:
                continue
    return date.strftime(format)


def get_simple_name(data):
    return ','.join(data).replace('（', '(').replace('）', ')')


def transform_company_name(company_name):
    return company_name.replace('（', '(').replace('）', ')')