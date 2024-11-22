from Database import SQL_operate
from Packing.models import Sticker as model_Sticker

class Sticker_data():
    """
        用來連結資料庫並且轉換數據
    """

    def __init__(self) -> None:
        self.db = SQL_operate.DB_operate('YBIT')
        self.MIS_YBICO_db = SQL_operate.DB_operate('MIS')

    def main(self):
        # 取得ERP 所有的貼紙資料 # 料號 品名 供應商 透過ERP PROD 裡面的自訂文字欄位09 來判斷所有的標籤貼紙	       
        PROD_df = self.db.get_pd_data("select PROD_NO,PROD_NAME,FACT_NO from PROD where PROD_OTC09 = '標籤貼紙'")
        # 讀取廠商資料
        FACT_df = self.db.get_pd_data("select FACT_NO,FACT_NA from FACT ") 
        self.out_df = PROD_df.merge(FACT_df,how='left')
        

    def create_sticker_model(self):
        # 先從資料庫中取出所有已存在的 PROD_NO
        existing_prod_nos = set(model_Sticker.objects.values_list('PROD_NO', flat=True))
        # 建立對應的貼紙資料
        for _prod_no in self.out_df['PROD_NO']: 
            # 檢查是否已存在該 PROD_NO
            if _prod_no not in existing_prod_nos:                
                sticker = model_Sticker(PROD_NO=_prod_no)
                sticker.save()
                print(f'產品{_prod_no},的貼紙模型已成功建立。')
                
                

    def getresponsibilities(self):
        pass

