from Database import SQL_operate
import pandas as pd
import copy
import datetime
import calendar
from datetime import timedelta
import time
from Production_management.models import HistoryDailyConsume
import json
from Company.utils.Debug_tool import debug
class Transformer():
    """
        用來連結資料庫並且轉換數據
    """

    def __init__(self) -> None:
        self.db = SQL_operate.DB_operate('YBIT')
        self.MIS_YBICO_db = SQL_operate.DB_operate('MIS')

    def get_product_day(self, keep='first') -> dict:
        """
        用STIO 取得物料進出日期，讓計算日期更加準確
        原本使用IVIOS，但是感覺沒有STIO這麼完整
        獲取料號的第一次或最後一次入庫日期。
        :param keep: 'first' 表示保留第一次出現的條目，'last' 表示保留最後一次出現的條目
        :return: 包含每個料號及其對應入庫日期的字典
        """
        order = 'ASC' if keep == 'first' else 'DESC'
        query = f"""
            WITH RankedSTIO AS (
                SELECT STIO_D, PROD_NO, 
                        ROW_NUMBER() OVER (PARTITION BY PROD_NO ORDER BY STIO_D {order}) as rn
                FROM STIO
            )
            SELECT PROD_NO, STIO_D
            FROM RankedSTIO
            WHERE rn = 1
        """
        STIO_df = self.db.get_pd_data(query)
        result_dict = STIO_df.set_index('PROD_NO')['STIO_D'].to_dict()
        return result_dict
    
    def get_product_first_day(self):
        """
        用STIO取得料號第一次入庫日期
        """
        return self.get_product_day(keep='first')

    def get_product_last_day(self):
        """
        物料呆滯年限，取得料號最後一次入庫日期
        """
        return self.get_product_day(keep='last')

    def getconsume(self, datetype: str) -> dict:
        """
            用來取得需求量(消耗量)
            SORC_T:來源類別
            公式:'委外發料' + '製令發料' +'出貨'
        Args:
            datatype (str, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        # STIO(庫存異動主檔)
        STIO_df = self.db.get_pd_data(
            "SELECT PROD_NO, STIO_D,  STIO_T1, STIO_QTY, SORC_T FROM STIO")

        MIOS_df = self.db.get_pd_data(
            "SELECT TABL_NO, MIOS_T, MIOS_NA1, MIOS_TK FROM MIOS")

        MIOS_df.rename(columns={"TABL_NO": "SORC_T",
                                "MIOS_T": "STIO_T1"}, inplace=True)

        new_df: pd.DataFrame = STIO_df.merge(
            MIOS_df, how='inner', on=['SORC_T', "STIO_T1"])

        filter_list = ['委外發料', '製令發料', '出貨']

        new_df = new_df[new_df['MIOS_NA1'].apply(lambda x: x in filter_list)]

        if datetype == 'month':
            new_df['Month'] = new_df['STIO_D'].apply(lambda x: x[:6])
            data = new_df['STIO_QTY'].groupby(
                [new_df['PROD_NO'], new_df['Month']]).sum()
        else:
            new_df['Year'] = new_df['STIO_D'].apply(lambda x: x[:4])
            data = new_df['STIO_QTY'].groupby(
                [new_df['PROD_NO'], new_df['Year']]).sum()

        return data.to_dict()

    @staticmethod
    def get_dayvalue_intervial(data: dict):
        """
            將資料吐出為總量
        Args:
            data (dict): _description_
        """
        allintervial = list(set([each_index[1]
                        for each_index, each_month in data.items()]))
        allintervial.sort()
        
        model_month = {i: 0.0 for i in allintervial}
        
        out_dict = {}

        for each_index, each_value in data.items():
            symbol = each_index[0]
            intervial = each_index[1]
            
            if symbol in out_dict:
                out_dict[symbol].update({intervial: each_value})
            else:
                Copy_model_month = copy.deepcopy(model_month)
                Copy_model_month.update({intervial: each_value})
                out_dict[symbol] = Copy_model_month

        # convert to DataFrame
        df = pd.DataFrame(out_dict)
        df = df.transpose()
        return df
    

    @staticmethod
    def get_month_range(start_date, end_date, first_day = None) -> list:
        """
            用來判斷每一個商品的月份區間

        Args:
            first_day (_type_): 20230101
            start_date (_type_): 2022-01-01
            end_date (_type_): 2024-12-31

        Returns:
            list: _description_
        """
        # 初始化月份列表
        months = []
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        if first_day is not None:
            first_day = datetime.datetime.strptime(first_day, "%Y%m%d")
            # 如果商品起始日期不在查詢範圍直接跳過
            if first_day > start and first_day > end:
                return months

            # 先判斷起始日期 和 結束日期
            # 狀況1
            if first_day > start:
                start = first_day
            else:
                # 如果商品出現的第一天比開始日期還要早，那就沒有任何影響
                pass

        # 從起始日期開始，每次增加一個月，直到達到或超過結束日期
        current = start
        while current <= end:
            months.append(current.strftime("%Y%m"))
            # 計算下一個月的第一天
            if current.month == 12:
                current = current.replace(year=current.year+1, month=1, day=1)
            else:
                current = current.replace(month=current.month+1, day=1)

        return months
    
    @staticmethod
    def get_workdays(year, month) -> int:
        # 確定月份的天數
        num_days = calendar.monthrange(year, month)[1]
        # 生成當月的所有日期
        days = [datetime.datetime(year, month, day)
                for day in range(1, num_days + 1)]
        # 過濾掉周末（星期六和星期日）
        return len([day for day in days if day.weekday() < 5])

    def date_range(self,start_date,end_date) -> list:
        """
            取得開始時間 和 結束時間中的每一天
        """
        out_list = []
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        current_date = start_date
        while current_date <= end_date:
            out_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return out_list
    
    def daily_value_history(self):
        """
            每日更新日用量歷史數據，
            以今天開始往前3年
            (動態呈現)
            目前打算設計給副總使用
            使用月週期的工作日

            此函數:
                用於每日排程更新資料庫
        """
        # 取得每個物料的第一天
        result_dict = self.get_product_first_day()

        consume_data = self.getconsume(datetype='month')
        consume_data = self.get_dayvalue_intervial(consume_data)        
        
        # 本次的目標時間為2024-01-01 (指指定時間)
        dates = self.date_range(start_date='2023-10-01',end_date='2023-12-31')        

        # 及時回補
        # latest_record = HistoryDailyConsume.objects.latest('date')
        # next_date = str(latest_record.date + timedelta(days=1))
        # today = str(datetime.datetime.today().date())        
        # dates = self.date_range(start_date=next_date,end_date=today)
        

        for each_date in dates:
            # 初始化最後日期
            end_date = each_date
            # 往前推3年
            start_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=-1095)
            start_date = start_date.strftime('%Y-%m-%d')
            Correction_dict = {}
            for prod_no, first_day in result_dict.items():
                month_range = Transformer.get_month_range(start_date, end_date, first_day)
                Correction_dict.update({prod_no: month_range})
            
            daily_value_map ={}            
            for prod_no in consume_data.index:
                sum_days = 0  # 個別記錄每個產品的總工作天數
                sum_consumes = 0 # 個別記錄每個產品的消耗量
                month_range = Correction_dict[prod_no]  # 每個產品新的查詢週期
                for each_column in consume_data.columns:
                    if each_column in month_range:
                        # 各月份天數
                        each_month_day = Transformer.get_workdays(
                            int(each_column[:4]), int(each_column[-2:]))

                        sum_days += each_month_day
                        sum_consumes += consume_data[each_column].loc[prod_no]
                
                daily_value_map[prod_no] = sum_consumes / sum_days if sum_days != 0 else 0 

            print(daily_value_map)
            print('*'*120)

            HDC = HistoryDailyConsume()
            HDC.date = each_date
            HDC.data = json.dumps(daily_value_map)
            HDC.save()


        

    def change_data_from_dict_tuple(self,data:dict):
        """
            data :
                {('102-M03-08Z', '2020'): 476.0, ('102-M03-08Z', '2021'): 3204.0, ('102-M03-08Z', '2022'): 4695.0, ('102-M03-08Z', '2023'): 2246.0 } 
            
            output:
                Product	    Year	Value
                102-M03-08Z	2020	476.0
                102-M03-08Z	2021	3204.0
                102-M03-08Z	2022	4695.0
                102-M03-08Z	2023	2246.0
        
        """
        # 將字典轉換為 DataFrame
        df = pd.DataFrame(list(data.items()), columns=['Product_Year', 'Value'])

        # 將 'Product_Year' 拆分成兩列 'Product' 和 'Year'
        df[['Product', 'Year']] = pd.DataFrame(df['Product_Year'].tolist(), index=df.index)

        # 刪除 'Product_Year' 列
        df = df.drop(columns=['Product_Year'])

        # 重新排列列的順序
        df = df[['Product', 'Year', 'Value']]
        
        return df
    

        