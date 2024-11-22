from anytree.exporter import DictExporter
from anytree import Node
from dateutil.rrule import rrule, DAILY
from datetime import date
import pandas as pd
import time
import copy
import datetime 
import calendar


def get_children(prodbomdf: pd.DataFrame, product_no: str):
    """
    透過母階料號循環取得子階料號
        product_no:'P24300-BW-01'

        # LK_PROD_NO 母 LK_PROD_NO1 子
    """
    def general_node(root_name: str, parent_node):
        # children_node_list = prodbomdf[prodbomdf['LK_PROD_NO'] == root_name]['LK_PROD_NO1'].to_list()
        children_node_list = [
            item for item in prodbomdf.loc[prodbomdf['LK_PROD_NO'] == root_name, 'LK_PROD_NO1']]
        # for item in children_node_list:
        #     num_list = prodbomdf[(prodbomdf['LK_PROD_NO'] == root_name) & (prodbomdf['LK_PROD_NO1'] == item)]['STND_QTYX'].to_list()
        #     children_node = Node(item, parent=parent_node, num=num_list[0])
        #     general_node(item, children_node)
        for item in children_node_list:
            num_list = prodbomdf.loc[(prodbomdf['LK_PROD_NO'] == root_name) & (
                prodbomdf['LK_PROD_NO1'] == item), 'STND_QTYX']
            children_node = Node(item, parent=parent_node,
                                 num=num_list.iloc[0])
            general_node(item, children_node)

    # 第一個節點
    root_name = product_no
    root = Node(root_name, num=1.0)  # 成品件為1

    # 執行
    general_node(root_name, root)

    exporter = DictExporter()
    return exporter.export(root)

def clean_num(child_data: dict):
    # mother num
    mother_num = None
    out_list = []

    def repeat_clean(childdata, mother_num):

        for key_name, value in childdata.items():

            if key_name == 'num':
                if mother_num is None:
                    num = value
                else:
                    num = mother_num * value

            if key_name == 'name':
                out_list.append([value, num])

            if key_name == 'children':
                for each_ in value:
                    repeat_clean(each_, num)

    repeat_clean(child_data, mother_num)
    return out_list


def clean_mk(child_list: list):
    """將製程刪除"""
    out_list = []
    for i in child_list:

        if '[' in i or ']' in i[0]:
            continue
        else:
            out_list.append(i)

    return out_list


def get_open_materials_children(prodbomdf: pd.DataFrame, product_no: str):
    """
    透過母階料號循環取得子階料號
        product_no:'P24300-BW-01'

        # LK_PROD_NO 母 LK_PROD_NO1 子
        
        判斷配料展開方式(斷階,跳階)
    """
    def general_node(root_name: str, parent_node):
        children_node_list = [
            item for item in prodbomdf.loc[prodbomdf['LK_PROD_NO'] == root_name, 'LK_PROD_NO1']]
        for item in children_node_list:
            MBOM_T1_list = prodbomdf.loc[(prodbomdf['LK_PROD_NO'] == root_name) & (
                prodbomdf['LK_PROD_NO1'] == item), 'MBOM_T1']
            children_node = Node(item, parent=parent_node,
                                 T1=MBOM_T1_list.iloc[0])
            general_node(item, children_node)

    # 第一個節點
    root_name = product_no
    root = Node(root_name, T1=1.0)  # 成品件為1
    # 執行
    general_node(root_name, root)
    exporter = DictExporter()
    return exporter.export(root)