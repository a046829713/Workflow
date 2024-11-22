from django.core.cache import cache
from .DataTransformer import Transformer
import numpy as np
import pandas as pd

def get_cached_consume_data():
    consume_data = cache.get('consume_data')
    if consume_data is None:
        consume_data = Transformer().getconsume(datetype='month')
        consume_data = Transformer.get_dayvalue_intervial(consume_data)
        cache.set('consume_data', consume_data, 1500)
    return consume_data

def filter_consume_data(consume_data, prod_name_and_number):
    if prod_name_and_number:
        return consume_data[consume_data.index == prod_name_and_number]
    return consume_data.loc[np.random.choice(consume_data.index, size=200, replace=False)]

def filter_time_split(consume_data:pd.DataFrame, start_date, end_date):
    new_df = pd.DataFrame()
    for col in consume_data.columns:
        checkcol = col[:4] + '-' + col[4:] + '-01'
        if checkcol >= start_date and checkcol <= end_date:
            new_df = pd.concat([new_df, consume_data[col]],axis=1)


    return new_df


def calculate_correction_dict(result_dict, start_date, end_date):
    """
        單純取得月份區間區間
    """
    Correction_dict = {}
    set_count = {}
    for prod_no, first_day in result_dict.items():
        if first_day in set_count:
            month_range = set_count[first_day]
        else:
            month_range = Transformer.get_month_range(start_date, end_date, first_day)
            set_count[first_day] = month_range
        Correction_dict[prod_no] = month_range
    return Correction_dict

def calculate_sum_days_map(consume_data, Correction_dict):
    sum_days_map = {}
    set_count = {}
    for prod_no in consume_data.index:
        sum_days = 0
        month_range = Correction_dict[prod_no]
        for each_column in consume_data.columns:
            if each_column in month_range:
                if each_column in set_count:
                    each_month_day = set_count[each_column]
                else:
                    each_month_day = Transformer.get_workdays(int(each_column[:4]), int(each_column[-2:]))
                    set_count[each_column] = each_month_day
                sum_days += each_month_day
        sum_days_map[prod_no] = sum_days
    return sum_days_map

def calculate_consume_map(consume_data, Correction_dict):
    consume_map = {}
    for i in range(consume_data.shape[0]):
        consume = 0
        prod_no = consume_data.iloc[i].name
        month_range = Correction_dict[prod_no]
        for each_month in consume_data.iloc[i].index:
            if each_month in month_range:
                consume += consume_data.iloc[i][each_month]
        consume_map[prod_no] = consume
    return consume_map

def calculate_merge_mean_daily_value(sum_days_map, consume_map):
    merge_mean_daily_value = {}
    for prod_no, sum_days in sum_days_map.items():
        if sum_days == 0:
            merge_mean_daily_value[prod_no] = 0
        else:
            merge_mean_daily_value[prod_no] = consume_map[prod_no] / sum_days
    return merge_mean_daily_value