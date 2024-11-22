from anytree import Node
from anytree.exporter import  JsonExporter
from collections import defaultdict
from Database import SQL_operate
from .GetTimeData import GetTimeDataTransformer
import numpy as np
import pandas as pd
from .count import get_children, clean_num, clean_mk, get_open_materials_children


class TreeTransformer(GetTimeDataTransformer):
    """
    GetJsonTreeData
        用來取得BOM表資料及leadTime的匯總
    """

    def __init__(self) -> None:
        super().__init__()
        self._get_init()
        self._getMakename()

    def getTreeData(self, prod_no: str):
        TimeData = self.GetResult(prod_no)

        self.produce_consume(prod_no)
        self.OpenMaterials(prod_no)

        root_name = prod_no
        if root_name in TimeData:
            root = Node(root_name, Time=TimeData[root_name], Make_CN_name='', order_out_price='', prod_name=self.get_prod_na(
                root_name), safe_qty=self.get_safe_qty(root_name), fact_na="", usefull_qty=self.getQTYU(root_name), consume=self.getSTND_QTYX(root_name), MKtime='', openmaterials='')
        else:
            raise ValueError("資料錯誤請洽資訊人員")

        mask = self.df_v_prodbom1['LK_PROD_NO'] == root.name

        root_children_list = self.df_v_prodbom1[mask]['LK_PROD_NO1'].to_list()

        def general_node(node_list, parent_node):
            node_temp_list = []
            for item in node_list:

                # 創建子節點之內容
                if '[' in item:
                    children_node = Node(item, parent=parent_node,
                                         Time=TimeData.get(item, ""), Make_CN_name=self.getMakename(item),
                                         order_out_price=self.getPROD_C(item), prod_name='', safe_qty='', fact_na=self.get_factna(item),
                                         usefull_qty="", consume="", MKtime=self.getMaketime(item), openmaterials='')
                else:
                    children_node = Node(item, parent=parent_node,
                                         Time=TimeData.get(item, ""), Make_CN_name='',
                                         order_out_price='', prod_name=self.get_prod_na(item),
                                         safe_qty=self.get_safe_qty(item), fact_na="", usefull_qty=self.getQTYU(item),
                                         consume=self.getSTND_QTYX(item), MKtime='', openmaterials=self.getOpenMaterials(item))

                children_mask = self.df_v_prodbom1['LK_PROD_NO'] == item
                children_node_list = self.df_v_prodbom1[children_mask]['LK_PROD_NO1'].to_list(
                )
                temp_dict = defaultdict(dict)
                temp_dict['子階物料清單'] = children_node_list
                temp_dict['父節點'] = children_node
                node_temp_list.append(temp_dict)

            for item in node_temp_list:
                general_node(item['子階物料清單'], item['父節點'])

        # 執行
        general_node(root_children_list, root)

        # 用來畫圖
        # UniqueDotExporter(root, nodeattrfunc=lambda n: 'label="%s"' % ("<" + n.name + ">" + n.Time)
        #                   if n.Time else 'label="%s"' % (n.name)).to_picture("test.png")

        exporter = JsonExporter()
        return exporter.export(root)

        # data = exporter.export(root)

        # # 將 JSON 字符串寫入文件
        # with open('tree.json', 'w') as f:
        #     f.write(data)

    def _getMakename(self):
        """_summary_

        Args:
            prod_no (str): _description_

        Returns:
            _type_: {'PROD_NO': 'P24300-BW-01', 'RBOM_NO': '0010', 'RBOM_T1': '0001', 'ROUT_NO': '91', 'ROUT_NA': '包裝'}
        """
        app = SQL_operate.DB_operate(sqltype='YBIT')
        # PROD_C 單價
        self.RBOM_df = app.get_pd_data(
            'SELECT PROD_NO,RBOM_NO,RBOM_T1,ROUT_NO ,PROD_C,FACT_NO ,RBOM_HR4,RBOM_HR4U FROM RBOM')

        ROUT_df = app.get_pd_data('SELECT ROUT_NO,ROUT_NA FROM ROUT')

        self.Make_dF = self.RBOM_df.merge(
            ROUT_df, left_on='ROUT_NO', right_on='ROUT_NO')

        self.Make_dF = self.Make_dF.merge(
            self.FACT_df, left_on='FACT_NO', right_on='FACT_NO', how='left')

    def _get_init(self):
        """
            取得品名規格
        """
        # LK_PROD_NO 母 LK_PROD_NO1 子
        self.df_v_prodbom1 = self.app.get_pd_data(
            'select LK_PROD_NO, LK_PROD_NO1, STND_QTYX, MBOM_T1 from V_PRODBOM1')

        self.PROD_df = self.app.get_pd_data(
            'SELECT PROD_NO, PROD_NAME, SAFE_QTY, LEAD_TIME FROM PROD')

        self.FACT_df = self.app.get_pd_data(
            'SELECT FACT_NO,FACT_NA FROM FACT'
        )

        # """ 可用量預估速查(產品別) (庫存量-需求)"""
        self.V_PROD_QTYU_df = self.app.get_pd_data(
            'SELECT PROD_NO,LK_PROD_QTYU2 FROM V_PROD_QTYU'
        )

    def get_prod_na(self, PROD_NO: str):
        return self.PROD_df[self.PROD_df['PROD_NO'] == PROD_NO]['PROD_NAME'].values[0]

    def get_safe_qty(self, PROD_NO: str):
        out_qty = self.PROD_df[self.PROD_df['PROD_NO']
                               == PROD_NO]['SAFE_QTY'].values[0]

        if np.isnan(out_qty):
            return ""
        else:
            return out_qty

    def _get_open_materials(self, symobol_data):
        parser_key = []
        parser_value = []

        def test(data):
            for key, value in data.items():
                if key == 'children':
                    for each_ in value:
                        test(each_)
                if key == 'T1':
                    parser_key.append(value)
                if key == 'name':
                    parser_value.append(value)

        test(symobol_data)

        translate_map = {"1": "跳階",
                         "2": "斷階",
                         "3": "C類物料",
                         "4": "斷階續展"}

        dict_data = {k: v for v, k in list(zip(parser_key, parser_value)) if k}
        filtered_dict_data = {k: translate_map[str(
            int(v))] for k, v in dict_data.items() if v}

        return filtered_dict_data

    def OpenMaterials(self, each_symbol: str):
        """ 取得產品展開方式 """

        self.open_materials = self._get_open_materials(
            get_open_materials_children(self.df_v_prodbom1, each_symbol))
        return self.open_materials
    
    def getOpenMaterials(self, PROD_NO: str):

        return self.open_materials[PROD_NO]

    def getQTYU(self, PROD_NO: str):
        try:
            out_QTY = self.V_PROD_QTYU_df[self.V_PROD_QTYU_df['PROD_NO']
                                          == PROD_NO]['LK_PROD_QTYU2'].values[0]

            return out_QTY
        except:
            return 0.0

    def getSTND_QTYX(self, PROD_NO: str):
        """子階物料消耗量

        Args:
            PROD_NO (str): _description_
        """

        out_STND_QTYX = self.produce_consume_df[self.produce_consume_df['product_code']
                                                == PROD_NO]['num'].values[0]
        return out_STND_QTYX

    def getMakename(self, PROD_NO_ROUT: str):
        """
            取得製程的中文名稱

                return:包裝
        """
        PROD_NO = PROD_NO_ROUT.split('[')[0]
        RBOM_NO = PROD_NO_ROUT.split('[')[1].replace(']', '')

        # PROD_NO RBOM_NO ROUT_NA

        return self.Make_dF[(self.Make_dF['PROD_NO'] == PROD_NO) &
                            (self.Make_dF['RBOM_NO'] == RBOM_NO)]['ROUT_NA'].values[0]

    def getMaketime(self, PROD_NO_ROUT: str):
        """
            取得製程的時間

                return:包裝
        """
        PROD_NO = PROD_NO_ROUT.split('[')[0]
        RBOM_NO = PROD_NO_ROUT.split('[')[1].replace(']', '')

        maketime = self.all_MKtime[(self.all_MKtime['PROD_NO'] == PROD_NO) &
                                   (self.all_MKtime['RBOM_NO'] == RBOM_NO)]['RBOM_HR4'].values[0]

        if np.isnan(maketime):
            return ""
        else:
            return maketime

    def getPROD_C(self, PROD_NO_ROUT: str):
        """
            取得委外單價

                return:15.000
        """
        PROD_NO = PROD_NO_ROUT.split('[')[0]
        RBOM_NO = PROD_NO_ROUT.split('[')[1].replace(']', '')

        price = self.Make_dF[(self.Make_dF['PROD_NO'] == PROD_NO) &
                             (self.Make_dF['RBOM_NO'] == RBOM_NO)]['PROD_C'].values[0]

        if price == 0 or np.isnan(price):
            return ""

        return price

    def get_factna(self, PROD_NO_ROUT: str):
        """
            取得廠商名稱
        """
        PROD_NO = PROD_NO_ROUT.split('[')[0]
        RBOM_NO = PROD_NO_ROUT.split('[')[1].replace(']', '')

        Factna = self.Make_dF[(self.Make_dF['PROD_NO'] == PROD_NO) &
                              (self.Make_dF['RBOM_NO'] == RBOM_NO)]['FACT_NA'].values[0]

        if not Factna or isinstance(Factna, float):

            return ""
        else:

            return Factna

    def produce_consume(self, each_symbol):
        """
            產生每一個母階料號下面所有子物件的消耗數量        
            P27000-GH-02,5-A16,1.0
            P27000-GH-02,4-1015-10H,1.0
            P27000-GH-02,P3000-15,1.0
            P27000-GH-02,P1620-60,1.0
            P27000-GH-02,P1620-39,1.0
            P27000-GH-02,P1100-12,1.0
            P27000-GH-02,P1100-25,1.0
            P27000-GH-02,16-M06-10H,1.0
            P27000-GH-02,16-406,1.0
            P27000-GH-02,YP260U-02,1.0
            P27000-GH-02,YP260N-01,1.0
            P27000-GH-02,YP110W-01,1.0
            P27000-GH-02,YYP270-01,1.0
            S2440-20,S2440-20,1.0
        """
        data = clean_mk(clean_num(get_children(
            self.df_v_prodbom1, each_symbol)))
        self.produce_consume_df = pd.DataFrame(
            data, columns=['product_code', 'num'])

        self.produce_consume_df['mother_pd'] = each_symbol

    def getTimeCheckData(self, prod_no: str, useleadtime: str):
        self.checkiftimeenough(self.getdata(prod_no), int(useleadtime))
        return self.cleantimeenough(self.TimeUseList)


if __name__ == '__main__':

    # TreeTransformer().getdata('CA8630-H')
    print(TreeTransformer().getTreeData('W628TE0-RHE'))
