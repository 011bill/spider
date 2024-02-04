import pandas as pd
from baiduspider.settings import EXCEL_PAHT, READ_COLUMN


# 读取列生成列表，配置文件中读取文件目录和列名
def columns_to_list():
    if ".xlsx" in EXCEL_PAHT:
        df = pd.read_excel(EXCEL_PAHT)
    elif ".csv" in EXCEL_PAHT:
        df = pd.read_csv(EXCEL_PAHT)
    else:
        print("Please enter CSV or Excel file.")
    # df[df.index >= 1020][READ_COLUMN]  # 从第几行开始
    # return list(df[df.index >= 250][READ_COLUMN])
    return list(df[READ_COLUMN])





