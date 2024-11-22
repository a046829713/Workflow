"""

This .py is use for build daily value of cronjobs.

           PROD_NO   2020   2021   2022   2023   2024
0      102-M03-08Z   2.42  12.82  18.78   8.98  23.50
1           11-525   3.52   0.89    NaN    NaN    NaN
2           11-609  22.20  30.46  21.49  26.79  23.12
3           11-612   8.62    NaN    NaN    NaN    NaN
4           11-640   1.69   0.50    NaN    NaN    NaN
...            ...    ...    ...    ...    ...    ...
15440   YYPD307-03    NaN    NaN    NaN    NaN   0.12
15441   YYTD610-02    NaN    NaN    NaN    NaN   8.47
15442   YYTF113-01    NaN    NaN    NaN    NaN   5.07
15443      ZUD-002    NaN    NaN    NaN    NaN   0.01
15444      ZZW-A17    NaN    NaN    NaN    NaN   1.51

"""

from .DataTransformer import Transformer
from . import common
import datetime
import time
import pandas as pd
from Database import SQL_operate
from workFlow.AlertMsg import LINE_Alert
import numpy as np

def calculate_every_prod_no_use_day_group_by_year(Correction_dict):
    """
        為了要取得每個料號各年度的需要除的天數

    """
    new_dict = {}
    set_count = {}

    for key, value in Correction_dict.items():
        mergeby_year = {}
        for each_column in value:
            year = each_column[:4]
            if each_column in set_count:
                each_month_day = set_count[each_column]
            else:
                each_month_day = Transformer.get_workdays(
                    int(year), int(each_column[-2:]))
                set_count[each_column] = each_month_day

            if year in mergeby_year:
                mergeby_year[year] += each_month_day
            else:
                mergeby_year[year] = each_month_day

        new_dict[key] = mergeby_year

    return new_dict


def get_dayvalue(data: dict, sum_years_days: dict):
    """ 
    取得日用量計算

    Args:
        data (dict): 
        {
        ('ZZZ-901-001', '2020'): -15.0,
        ('ZZZ-901-001', '2021'): -41.0,
        ('ZZZ-901-001', '2022'): -22.0,
        ('ZZZ-901-002', '2020'): -3.0,
        ('ZZZ-901-002', '2021'): -37.0,
        ('ZZZ-901-002', '2022'): -17.0,
        ('ZZZ-901-003', '2020'): -11.0,
        ('ZZZ-901-003', '2021'): -62.0,
        ('ZZZ-901-003', '2022'): -45.0
        .......
        }
    """

    out_dict = {}

    for each_index, each_value in data.items():
        symbol = each_index[0]
        year = each_index[1]

        workday = sum_years_days[symbol][year]

        if year in out_dict:
            if workday == 0:
                out_dict[year].update({symbol: 0})
            else:
                out_dict[year].update({symbol: round(each_value / workday, 2)})
        else:
            if workday == 0:
                out_dict.update({year: {symbol: 0}})
            else:
                out_dict.update(
                    {year: {symbol: round(each_value / workday, 2)}})
    return out_dict


def clean_PROD_NO(s: pd.Series):
    change_list = []
    for i in s.to_list():
        if i.replace(" ", "") != i:
            change_list.append(i)

    return change_list


def update_daily_value():
    """
        原本是在ERPAPI的project裡面
        後搬移至此負責每日更新日用量資訊    
    """
    result_dict = Transformer().get_product_first_day()


    start_date = '2020-04-01'
    end_date = str(datetime.datetime.now().date())
    
    
    Correction_dict = common.calculate_correction_dict(
        result_dict, start_date, end_date)
    
    
    sum_years_days = calculate_every_prod_no_use_day_group_by_year(Correction_dict)
    data = get_dayvalue(Transformer().getconsume(
        datetype='year'), sum_years_days)
    df = pd.DataFrame().from_dict(data, orient='index')
    df = df.T
    df.index.name = "PROD_NO"
    df.reset_index(inplace=True)
    change_list = clean_PROD_NO(df["PROD_NO"])
    filter = df['PROD_NO'].apply(lambda x: True if x in change_list else False)
    df = df[~filter]


    MIS_db = SQL_operate.DB_operate('MIS')
    # 如果資料庫已經不夠使用要添加新年份
    dailyvalue_df = MIS_db.get_pd_data("select * from dailyvalue")
    dailyvaluelist = dailyvalue_df.columns.to_list()
    if len(dailyvaluelist) != len(tuple(df.iloc[0].to_list())):
        for i in range(30):
            if str(2020 + i) not in dailyvaluelist:
                MIS_db.change_db_data(
                    f"ALTER TABLE dbo.dailyvalue ADD [{2020 + i}] float")
                break

    MIS_db.change_db_data("delete from dailyvalue")
    
    df.fillna(0, inplace=True)    
    
    try:
        MIS_db.put_pd_data(df, table_name='dailyvalue', exists='replace')
        print("更新成功")
        LINE_Alert().req_line_alert("每日dailyvalue 維護成功")
    except:
        LINE_Alert().req_line_alert("警告:每日dailyvalue維護失敗")
    
def update_daily_yearly_data():
    """
    更新每日和每年数据，计算产品实际使用天数和该年度的工作天数。
        output:
                料號    年份     消耗量    產品首次入庫日  產品實際使用天數  該年度總天數  日用量(消耗量/產品實際使用天數)  日用量(消耗量/該年度總天數)
        0      102-M03-08Z  2020   476.0 2020-03-31       198     262           2.404040         1.816794
        1      102-M03-08Z  2021  3204.0 2020-03-31       261     261          12.275862        12.275862
        2      102-M03-08Z  2022  4695.0 2020-03-31       260     260          18.057692        18.057692
        3      102-M03-08Z  2023  2246.0 2020-03-31       260     260           8.638462         8.638462
        4      102-M03-08Z  2024  3061.0 2020-03-31       262     262          11.683206        11.683206
        ...            ...   ...     ...        ...       ...     ...                ...              ...
        47041  ZZZ-901-002  2021    37.0 2020-11-25       261     261           0.141762         0.141762
        47042  ZZZ-901-002  2022    17.0 2020-11-25       260     260           0.065385         0.065385
        47043  ZZZ-901-003  2020    11.0 2020-10-29        46     262           0.239130         0.041985
        47044  ZZZ-901-003  2021    62.0 2020-10-29       261     261           0.237548         0.237548
        47045  ZZZ-901-003  2022    45.0 2020-10-29       260     260           0.173077         0.173077
    """
    start_date = '2020-01-01'
    end_date = str(datetime.date.today())

    transformer = Transformer()
    consume_data = transformer.getconsume(datetype='year')
    consume_data = transformer.change_data_from_dict_tuple(consume_data)

    # 获取每个物料的第一天
    result_dict = Transformer().get_product_first_day()

    # 将产品映射到首次使用日期
    consume_data['FirstUseDate'] = consume_data['Product'].map(result_dict)
    consume_data['FirstUseDate'] = pd.to_datetime(consume_data['FirstUseDate'], format="%Y%m%d")
    
    # 创建年度的起始和结束日期
    consume_data['YearStartDate'] = pd.to_datetime(consume_data['Year'] + '0101', format='%Y%m%d')
    consume_data['YearEndDate'] = pd.to_datetime(consume_data['Year'] + '1231', format='%Y%m%d')

    # 计算实际的开始日期
    consume_data['FirstUseYear'] = consume_data['FirstUseDate'].dt.year.astype(str)
    consume_data['StartDate'] = np.where(
        consume_data['FirstUseYear'] == consume_data['Year'],
        consume_data['FirstUseDate'],
        consume_data['YearStartDate']
    )


    # 计算实际使用天数
    consume_data['ReallyUseDay'] = np.where(
        consume_data['StartDate'] > consume_data['YearEndDate'],
        0,
        np.busday_count(
            consume_data['StartDate'].values.astype('datetime64[D]'),
            consume_data['YearEndDate'].values.astype('datetime64[D]') + np.timedelta64(1, 'D')
        )
    )

    # 预先计算每年的工作天数
    years = consume_data['Year'].unique()
    year_map = {}
    for year in years:
        start_date = np.datetime64(f'{year}-01-01')
        end_date = np.datetime64(f'{year}-12-31') + np.timedelta64(1, 'D')  # 包含结束日期
        working_days = np.busday_count(start_date, end_date)
        year_map[year] = working_days

    # 映射每年的工作天数
    consume_data['ThisYearDay'] = consume_data['Year'].map(year_map)



    consume_data['ExactDayValue'] = (consume_data['Value'] / consume_data['ReallyUseDay'])
    consume_data['AllYearDayValue'] = (consume_data['Value'] / consume_data['ThisYearDay'])
    
    
    consume_data = consume_data[['Product' , 'Year'  , 'Value' ,'FirstUseDate',  'ReallyUseDay' , 'ThisYearDay' ,  'ExactDayValue'  ,'AllYearDayValue']]
    consume_data.rename(columns={"Product":"料號",
                                 "Year":"年份",
                                 "Value":"消耗量",
                                 "FirstUseDate":"產品首次入庫日",
                                 "ReallyUseDay":"產品實際使用天數",
                                 "ThisYearDay":"該年度總天數",
                                 "ExactDayValue":"日用量(消耗量/產品實際使用天數)",
                                 "AllYearDayValue":"日用量(消耗量/該年度總天數)",
                                 },inplace=True)
    MIS_db = SQL_operate.DB_operate('MIS')
    consume_data.fillna(0, inplace=True)
    MIS_db.put_pd_data(consume_data,table_name='dailyYearlyValue',exists="replace")