from Database import SQL_operate
import datetime


class Slow_Moving():
    """
        用來連結資料庫並且轉換數據
    """

    def __init__(self) -> None:
        self.db = SQL_operate.DB_operate('YBIT')
        self.MIS_YBICO_db = SQL_operate.DB_operate('MIS')

    def _filter_no_Z(self, value):
        return not value.startswith('Z') or value.startswith('ZM')

    def main(self):
        """
            希望可以快速讓使用者知道使用量和消耗量
            現貨庫存明細:

        """
        # 過濾納入MRP計算的倉庫
        STRG_df = self.db.get_pd_data(
            "SELECT STRG_NO,STRG_T1 FROM STRG where STRG_T1='1'")

        STRG_NO_list = STRG_df['STRG_NO'].to_list()

        # 產品庫存 # 單倉庫存數量
        PDST_df = self.db.get_pd_data(
            "SELECT PROD_NO, STRG_NO, PROD_QTY FROM PDST")

        PDST_df = PDST_df[PDST_df['STRG_NO'].apply(
            lambda x: True if x in STRG_NO_list else False)]

        # 將不同倉庫的量相加起來
        PDST_df = PDST_df.groupby('PROD_NO')['PROD_QTY'].sum().reset_index()

        # MBAT_QTY (生產批量), BULW_QTY(MOQ) PROD_CTS(標準單位總成本)
        PROD_df = self.db.get_pd_data(
            "SELECT PROD_NO, PROD_NAME, PROD_CTS, PROD_U, MBAT_QTY, BULW_QTY,SAFE_QTY FROM PROD")

        PDST_df = PDST_df.merge(PROD_df, left_on='PROD_NO', right_on='PROD_NO')

        self.PDST_df = PDST_df[PDST_df['PROD_NO'].apply(self._filter_no_Z)]

        return self.PDST_df

    def _change_date_day(self, date_str):
        if date_str is None:
            return 0
        else:
            _datestr = datetime.datetime.strptime(date_str, "%Y%M%d")
            return (datetime.datetime.today() - _datestr).days / 365

    def count_NoM(self, last_date_record: dict):
        self.PDST_df['NoM(年)'] = self.PDST_df['PROD_NO'].apply(
            lambda x: last_date_record.get(x))
        self.PDST_df['NoM(年)'] = self.PDST_df['NoM(年)'].apply(
            self._change_date_day)
        return self.PDST_df

    def min_main(self, prod_no):
        """
            希望可以快速讓使用者知道各倉別使用量和消耗量
            更輕量化

        """
        # 過濾納入MRP計算的倉庫
        STRG_df = self.db.get_pd_data(
            "SELECT STRG_NO, STRG_NA, STRG_T1 FROM STRG where STRG_T1='1'")

        STRG_NO_list = STRG_df['STRG_NO'].to_list()

        # 產品庫存 # 單倉庫存數量
        PDST_df = self.db.get_pd_data(
            f"SELECT PROD_NO, STRG_NO, PROD_QTY FROM PDST where PROD_NO='{prod_no}'")

        PDST_df = PDST_df[PDST_df['STRG_NO'].apply(
            lambda x: True if x in STRG_NO_list else False)]

        # 先和倉庫合併取得倉庫名稱
        PDST_df = PDST_df.merge(STRG_df, left_on='STRG_NO', right_on='STRG_NO')
        PDST_df = PDST_df[['PROD_NO', 'STRG_NO', 'PROD_QTY', 'STRG_NA']]

        # MBAT_QTY (生產批量), BULW_QTY(MOQ) PROD_CTS(標準單位總成本)
        PROD_df = self.db.get_pd_data(
            f"SELECT PROD_NO, PROD_NAME, PROD_CTS, PROD_U, MBAT_QTY, BULW_QTY FROM PROD where PROD_NO='{prod_no}'")

        PDST_df = PDST_df.merge(PROD_df, left_on='PROD_NO', right_on='PROD_NO')

        self.PDST_df = PDST_df
        return self.PDST_df
