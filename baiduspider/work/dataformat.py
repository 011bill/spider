from datetime import datetime, timedelta


def format_date(date_string):
    current_year = datetime.now().year

    if '年' in date_string:
        # 包含年份的日期格式，例如：2019年12月2日
        date = datetime.strptime(date_string, "%Y年%m月%d日")
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
    elif '天前' in date_string:
        # X天前，例如：5天前
        days = int(date_string.split('天前')[0])
        date = datetime.now() - timedelta(days=days)
    else:
        # 没有年份的日期格式，例如：5月16日
        date = datetime.strptime(date_string, "%m月%d日")
        date = date.replace(year=current_year)

    return date.strftime("%Y-%m-%d")

# 测试不同格式的日期
date_strings = [
    "2019年12月2日",
    "昨天10:16",
    "5月16日",
    "5天前",
    "昨天",
    "前天",
    "50分钟前"
]

for date_string in date_strings:
    formatted_date = format_date(date_string)
    print(formatted_date)
