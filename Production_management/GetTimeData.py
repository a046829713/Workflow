import pandas as pd
from Database import SQL_operate
import json
import numpy as np


class GetTimeDataTransformer():
    def __init__(self) -> None:
        self.app = SQL_operate.DB_operate(sqltype='YBIT')
        self.MBOM_df = self.app.get_pd_data(
            'SELECT PROD_NO, MBOM_NO, PROD_NO1,RBOM_NO FROM MBOM')
        self.all_MKtime = pd.DataFrame()
        self.TimeUseList = []

    def get_day(self, each_prod) -> str:
        """

            將所有的製程時間保留下來
            可以傳入MKtime
        """

        # 換成天
        MK_time = self.RBOM_df[self.RBOM_df['PROD_NO']
                               == each_prod][['PROD_NO', 'RBOM_NO', 'RBOM_HR4', 'RBOM_HR4U']].copy()

        MK_time: pd.DataFrame

        for i in MK_time['RBOM_HR4U']:
            if i not in ['D', 'H']:
                raise ValueError("資料可能有誤 請洽資訊課")

        MK_time['RBOM_HR4'] = MK_time.apply(
            lambda x: x['RBOM_HR4'] if x['RBOM_HR4U'] == 'D' else x['RBOM_HR4']/24, axis=1)

        self.all_MKtime = pd.concat([self.all_MKtime, MK_time])

        result = sum(MK_time['RBOM_HR4'].to_list())

        if np.isnan(result):
            return "0.0"

        out_str = str(result)
        # 少個.會導致後面的判斷錯誤
        if "." not in out_str:
            out_str = out_str + '.0'

        return out_str

    def catch_prod(self, prods: list):
        out_dict = {}
        if len(prods) == 0:
            return {}
        else:
            for each_prod in prods:

                symbol_list = self.MBOM_df[self.MBOM_df['PROD_NO']
                                           == each_prod]['PROD_NO1'].to_list()

                sumtime = self.get_day(each_prod)
                if symbol_list:
                    if sumtime:
                        out_dict.update(
                            {each_prod: {sumtime: self.catch_prod(symbol_list)}})
                    else:
                        out_dict.update(
                            {each_prod: self.catch_prod(symbol_list)})
                else:
                    out_leadtime = self.PROD_df[self.PROD_df['PROD_NO']
                                                == each_prod]['LEAD_TIME'].iloc[0]

                    if np.isnan(out_leadtime):
                        out_dict.update(
                            {each_prod: "0.0"})
                    else:
                        out_dict.update(
                            {each_prod: str(out_leadtime)})

            return out_dict

    def getdata(self, symbol):
        prods = self.MBOM_df[self.MBOM_df['PROD_NO']
                             == symbol]['PROD_NO1'].to_list()

        return {symbol: {self.get_day(symbol): self.catch_prod(prods)}}

    def get_time_merge(self, symbol_data):
        """ 用來取得 Time的加總 """

        all_dict = {}

        while True:
            if symbol_data:
                out_dict = {}

                def get_dict_sum(data: dict):
                    """
                        將料號的時候,遞迴加總起來
                    """
                    for key, value in data.items():
                        if "." in value:
                            out_dict.update({key: value})

                        if type(value) == dict:
                            get_dict_sum(value)

                    return out_dict

                each_filter = get_dict_sum(symbol_data)
                all_dict.update(each_filter)

                def boyhook(data):
                    for each_symbol in data:

                        if each_symbol in each_filter:
                            # 檢查
                            for _i in data:
                                if _i not in each_filter:
                                    return data

                            # 檢查
                            value = list(data.values())
                            new_value = [float(i)
                                         for i in value if i is not None]
                            if new_value:
                                return str(max(new_value))

                        elif "." in list(data.keys())[0] and "." in list(data.values())[0]:
                            return str(float(list(data.keys())[0]) + float(list(data.values())[0]))
                        # elif "." in list(data.keys())[0]:

                        return data

                symbol_data = json.loads(json.dumps(
                    symbol_data), object_hook=boyhook)

                if isinstance(symbol_data, str):
                    break

        return all_dict

    def GetResult(self, symbol):
        self.timedata = self.getdata(symbol)
        
        return self.get_time_merge(self.timedata)

    def checkiftimeenough(self, _data, time, motherkey=None):
        for key, data in _data.items():
            try:
                # 若為數字計算剩餘時間
                lasttime = time - float(key)
                if isinstance(data, dict) and lasttime >= 0:
                    self.checkiftimeenough(data, lasttime, motherkey)
                else:
                    self.TimeUseList.append([motherkey, ""])
            except:
                # 若不為數字要做甚麼 繼續開車,且沒有撞到山壁
                if isinstance(data, dict):
                    self.checkiftimeenough(data, time, key)
                else:
                    lasttime = time - float(data)
                    if lasttime < 0:
                        self.TimeUseList.append([motherkey, key])

    def cleantimeenough(self, data):
        """
        有子件看子件 沒子件看母件
        [['S2900-02', 'S2900R-02A']
        ['S2900-02', 'S2900R-02B']
            ['S2900-03Y', '']
            ['S2910-07', 'S2910-07X']
            ['S29000', 'S2900-09']
            ['S29000', 'S2910-10']
            ['S2910-12', '']
            ['S29000', 'S2900-13']
            ['S29000', 'S2900-14']
            ['S2900-19', '']
            ['S29000', 'S2500-20']
            ['S2900Y-01Y', '']
            ['S2900-04', 'S2900-04Y']
            ['S2900Y-04-AA', 'S2900-05']
            ['S2900-06', '']
            ['S2900-08Y', '']
            ['S2900-08-BB', 'S2900-15']
            ['S2900-08-BB', 'S2900-16']
            ['S2900-17', 'S2900-17Y']
            ['S2900-18', 'S2900-18Y']]"""

        return [i[1] if i[1] else i[0] for i in data]
