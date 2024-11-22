import re
from Database import SQL_operate
from QualityAssurance.models import AbnormalFactna

def get_item_dict(parser_data: list):
    """
    a = [{'item': '00', 'factoryno': '110226'}, {'item': '00', 'makeno': '03'},
        {'item': '01', 'factoryno': '110226'}, {'item': '01', 'makeno': '19'},
        {'item': '02', 'factoryno': '110227'}, {'item': '02', 'makeno': '04'}]

    Args:
        parser_data (list): _description_
    """

    all_dict = {}

    for i in parser_data:
        # 統一加上1
        key = '0' + str(int(i['item']) + 1)
        all_dict.setdefault(key, {})
        all_dict[key].update(i)
        all_dict[key].pop('item', None)  # 移除 'item' 鍵，如果存在

    return all_dict

def generate(post_data: dict):
    factpattern = r"factmk_name(\d+)-0-Factname"
    routpattern = r"factmk_name(\d+)-0-ROUTname"

    out_list = []
    for key, value in post_data.items():
        if 'factmk_name' in key and 'Factname' in key and value:
            out_dict = {}
            match = re.search(factpattern, key)
            if match:
                item = '0' + str(match.group(1))
                out_dict['item'] = item
                out_dict['factoryno'] = value
                out_list.append(out_dict)
        
        if 'factmk_name' in key and 'ROUTname' in key and value:
            out_dict = {}
            match = re.search(routpattern, key)
            if match:
                item = '0' + str(match.group(1))
                out_dict['item'] = item
                out_dict['makeno'] = value
                out_list.append(out_dict)

    return out_list

def create_abnormal(key, value:dict, form_id:str, FACT_map, ROUT_map):
    abnormalfactna = AbnormalFactna()
    abnormalfactna.form_id = form_id
    abnormalfactna.item = key
    abnormalfactna.factoryno = value['factoryno']
    abnormalfactna.factoryname = FACT_map[value['factoryno']]
    abnormalfactna.makeno = value['makeno']
    abnormalfactna.makename = ROUT_map[value['makeno']]        
    abnormalfactna.save()

def delete_abnormalna(key, form_id:str):
    abnormalfactnas = AbnormalFactna.objects.filter(form_id = form_id, item = key)
    abnormalfactnas[0].delete()

def create_abnormalfactna(post_data: dict, form_id: str):
    print(post_data)    
    out_list = generate(post_data)
    item_data = get_item_dict(out_list)
    ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")

    FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
    FACT_map = {fact_no: fact_na for fact_no, fact_na in FACT_df.values}

    ROUT_df = ERP_sql.get_pd_data("select ROUT_NO,ROUT_NA from ROUT")
    ROUT_map = {rout_no: rout_na for rout_no, rout_na in ROUT_df.values}
    
    for key, value in item_data.items():
        create_abnormal(key, value,form_id,FACT_map,ROUT_map)


def count_diff_map(MKQTY_map: dict, mk_matchs: list):
    """
        用來計算製令未開數量

    Args:
        all_num
        MKQTY_map (dict): {'MK202311090050': 700.0, 'MK202311090051': 100.0, 'MK202311090053': 100.0, 'MK202311100037': 248.0}
        mk_matchs (list): 
        # MK單號 母單編號 + 令次 母單製作數量
        [('MK202311090050', 'RWF2023111500005-03',"3"),
            ('MK202311090051', 'RWF2023111500005-01',"3"),
            ('MK202311090053', 'RWF2023111500005-02',"3"), ('MK202311100037', 'RWF2023111500005-03',"3")]

    Returns:
        _type_: _description_
    """
    # 計算各MK的獨立缺口
    histroy_map = {}
    out_map = {}
    # 按 MK單號進行排序
    sorted_data = sorted(mk_matchs, key=lambda x: x[0])
    for eachrow in sorted_data:
        mknumber = eachrow[0]
        form_id_item =  eachrow[1]
        total_num = int(eachrow[2])
        if mknumber in MKQTY_map:
            this_mkqty = MKQTY_map[mknumber]
            # 可以跨MK取量,找到上次所記錄的最後一個數值
            if form_id_item in histroy_map:
                last_mkqty = histroy_map[form_id_item]
                histroy_map[form_id_item] = this_mkqty + last_mkqty
            else:
                histroy_map[form_id_item] = this_mkqty
                last_mkqty = 0                
            out_map[mknumber] = total_num - (this_mkqty + last_mkqty)
    return out_map

def getMK_Data(mk_number):
    ERPsql = SQL_operate.DB_operate(sqltype='YBIT')
    MAKEdf = ERPsql.get_pd_data('select MAKE_NO,MAKE_QTY,MKOK_YN from MAKE')

    
    MKQTY_map = {make_no: make_qty for make_no,
                    make_qty in MAKEdf[['MAKE_NO','MAKE_QTY']].values if make_no in mk_number}

    MKQTY_map = {make_no: MKQTY_map[make_no]
                    for make_no in sorted(MKQTY_map)}
    
    small_map ={
        "1":"未結",
        "2":"已結",
        "3":"特結",
    }
    MKYN_map = {make_no: small_map[make_yn] for make_no,
                    make_yn in MAKEdf[['MAKE_NO','MKOK_YN']].values if make_no in mk_number}
    
    return MKQTY_map,MKYN_map


