from Database import SQL_operate
from Company.models import Form,CustomUser
from QualityAssurance.models import AbnormalFactna,AbnormalMK
import json
import sys
import numpy as np
# 创建数据库操作对象
db = SQL_operate.DB_operate(sqltype='MIS')
ERP_db = SQL_operate.DB_operate(sqltype='YBIT')

def changemakname(name) ->str:
    out_str = name
    
    if name =='铣床':
        out_str = '銑床'
    if name =='噴黑漆' or name=='噴漆'or name=='雷射'or name=='磨肉厚'or name=='沖字'or name=='磨刃口' \
    or name=='除銹噴砂'or name=='細拋'or name=='磷酸錳'or name=='滲油磨除並噴漆.' or name=='噴砂除鏽' or name=='退火至8度'\
        or name=='打上"1"記號' or name=='裁切'or name=='整形'or name=='抛除刮傷.'or name=='修長度'or name=='去漆':
        out_str = '重工'
    if name =='除銹':
        out_str = '除鏽'
    if name =='烤漆(灰色)':
        out_str = '烤漆'

    if out_str is None:
        out_str = ''
    return out_str

def changefactname(name) ->str:
    out_str = name
    if name == '吉昌':
        out_str = '吉昌工業'
    if name == '優進':
        out_str = '優進(實進)'
    if name == '大裕':
        out_str = '大裕電鍍廠'
    if name == '萬勝鴻':
        out_str = '萬勝鴻實業'
    if name == '展昕' or name=='守宬':
        out_str = '守宬(展昕)'
    if name == '3F(雷射)' or name=='育仟(雷射)'or name=='雷射':
        out_str = '育仟'
    if name == '河清':
        out_str = '河清金屬'
    if name == '元貝(雷射)'or name=='二樓產線' or name=='裝配二組'or name=='裝配一組'or name=='產線1組' or name=='二F':
        out_str = '元貝'
    if name == '亞柏(噴砂)':
        out_str = '亞柏'
    if name == '同徫行':
        out_str = '同偉行'
    if name == '沅泰':
        out_str = '沅泰工業'
    if name == '進溢':
        out_str = '進溢(晉邑)'
    if name == '730847':
        out_str = '有宏'
    if name == '惠豐':
        out_str = '惠豐熱處理'
    if name == '阡世鋒' or name=='阡四峰':
        out_str = '千裕峰'
    if name == '鴻億' or name == '鴻溢':
        out_str = '鴻鎰'
    if name == '耀賢':
        out_str = '耀賢(宗毅)'
    if name == '兆偉':
        out_str = '兆煒'
    
    if name == '亞伯':
        out_str = '亞柏'
    if name == '巨笠':
        out_str = '巨岦'
    if name == '晶帷'or name == '晶瑋'or name == '晶偉':
        out_str = '晶幃'
    if name == '靖盈':
        out_str = '靖盈(新濟)'
    if name == '弘銳':
        out_str = '弘銳工業'
    if name == '阡蕙':
        out_str = '仟蕙'
    
    
    if name == '噴砂' or name =='電鍍' or name =='同偉行+駿泰' or name=='金忠'  or name=='nan' or name=='家庭代工' or name=='鴻鎰+育千'or name=='鴻鎰OR山杰'or name=='(等待確認)'or name=='品保':
        return ''
    
    return out_str



# 编写 SQL 查询，选择所有需要的列，并将 '狀態' 列转换为 nvarchar
query = """
SELECT 
    [編號], 
    [日期], 
    CONVERT(nvarchar, [狀態]) AS [狀態], 
    CONVERT(nvarchar, [產品編號(重工前)]) AS[產品編號(重工前)], 
    CONVERT(nvarchar, [品名規格(重工前)]) AS[品名規格(重工前)], 
    CONVERT(nvarchar, [產品編號(重工後)]) AS[產品編號(重工後)], 
    CONVERT(nvarchar, [品名規格(重工後)]) AS[品名規格(重工後)], 
    [數量], 
    CONVERT(nvarchar, [重工項目]) AS[重工項目],
    CONVERT(nvarchar, [重工原因]) AS[重工原因], 
    CONVERT(nvarchar, [開單者]) AS[開單者],
    CONVERT(nvarchar,[付費單位]) AS[付費單位], 
    CONVERT(nvarchar,[責任單位]) AS[責任單位],
    CONVERT(nvarchar,[重工訊息來源]) AS[重工訊息來源],    
    CONVERT(nvarchar,[來源備註]) AS[來源備註], 
    CONVERT(nvarchar,[重工後處置]) AS[重工後處置], 
    CONVERT(nvarchar,[備註]) AS[備註],
    CONVERT(nvarchar,[IO單號]) AS[IO單號] 
FROM [abnormal]
"""


# 使用查询获取数据
abnormal_df = db.get_pd_data(query)

abnormalfactname_df  = db.get_pd_data("""select [ID],
                                      項次,
                                      CONVERT(nvarchar,[factoryname]) AS[factoryname],
                                      mak,
                                      CombinID,
                                      單價,
                                      總價 
                                      from abnormalfactname""")   


FACT_df = ERP_db.get_pd_data("""select FACT_NO,FACT_NA from FACT""")
ROUT_df = ERP_db.get_pd_data("""select ROUT_NO,ROUT_NA from ROUT""")




abnormalmk_df = db.get_pd_data("""select MK單號, CombinID, 備註 from abnormalmk""")


all_user = CustomUser.objects.all()

for i in range(abnormal_df.shape[0]):
    if abnormal_df.iloc[i]['狀態'] == '結案':
        data = {"form_id_Per": "",
                "estimated_completion_date": "",
                }
        
        data['prod_no_before'] = abnormal_df.iloc[i]['產品編號(重工前)']
        data['prod_name_before'] = abnormal_df.iloc[i]['品名規格(重工前)']
        data['prod_no_after'] = abnormal_df.iloc[i]['產品編號(重工後)']
        data['prod_name_after'] = abnormal_df.iloc[i]['品名規格(重工後)']
        data['quantity'] = abnormal_df.iloc[i]['數量']
        data['paying_unit'] = abnormal_df.iloc[i]['付費單位']
        data['responsible_unit'] = abnormal_df.iloc[i]['責任單位']
        data['heavy_industry_information'] = abnormal_df.iloc[i]['重工訊息來源']
        data['source_notes'] = abnormal_df.iloc[i]['來源備註']
        data['pay_after_heavy_work'] = abnormal_df.iloc[i]['重工後處置']
        data['remark'] = abnormal_df.iloc[i]['備註']
        data['io_number'] = abnormal_df.iloc[i]['IO單號']
        data['rebuild_reason'] = abnormal_df.iloc[i]['重工原因']
        data['Heavy_industry_projects'] = abnormal_df.iloc[i]['重工項目']
        for key in data:
            if data[key] is None:
                data[key] = ""
        
       
        
        
        # 取得對應的廠商代碼
        fact_data = {"factmk_name0-TOTAL_FORMS": "1",
                "factmk_name0-INITIAL_FORMS": "0",
                "factmk_name0-MIN_NUM_FORMS": "0",
                "factmk_name0-MAX_NUM_FORMS": "1000",
                "factmk_name0-0-Factname": "",
                "factmk_name0-0-ROUTname": "",
                "factmk_name1-TOTAL_FORMS": "1",
                "factmk_name1-INITIAL_FORMS": "0",
                "factmk_name1-MIN_NUM_FORMS": "0",
                "factmk_name1-MAX_NUM_FORMS": "1000",
                "factmk_name1-0-Factname": "",
                "factmk_name1-0-ROUTname": "",
                "factmk_name2-TOTAL_FORMS": "1",
                "factmk_name2-INITIAL_FORMS": "0",
                "factmk_name2-MIN_NUM_FORMS": "0",
                "factmk_name2-MAX_NUM_FORMS": "1000",
                "factmk_name2-0-Factname": "",
                "factmk_name2-0-ROUTname": "",
                "factmk_name3-TOTAL_FORMS": "1",
                "factmk_name3-INITIAL_FORMS": "0",
                "factmk_name3-MIN_NUM_FORMS": "0",
                "factmk_name3-MAX_NUM_FORMS": "1000",
                "factmk_name3-0-Factname": "",
                "factmk_name3-0-ROUTname": "",
                "factmk_name4-TOTAL_FORMS": "1",
                "factmk_name4-INITIAL_FORMS": "0",
                "factmk_name4-MIN_NUM_FORMS": "0",
                "factmk_name4-MAX_NUM_FORMS": "1000",
                "factmk_name4-0-Factname": "",
                "factmk_name4-0-ROUTname": "",
                "factmk_name5-TOTAL_FORMS": "1",
                "factmk_name5-INITIAL_FORMS": "0",
                "factmk_name5-MIN_NUM_FORMS": "0",
                "factmk_name5-MAX_NUM_FORMS": "1000",
                "factmk_name5-0-Factname": "",
                "factmk_name5-0-ROUTname": "",
                "factmk_name6-TOTAL_FORMS": "1",
                "factmk_name6-INITIAL_FORMS": "0",
                "factmk_name6-MIN_NUM_FORMS": "0",
                "factmk_name6-MAX_NUM_FORMS": "1000",
                "factmk_name6-0-Factname": "",
                "factmk_name6-0-ROUTname": "",
                "factmk_name7-TOTAL_FORMS": "1",
                "factmk_name7-INITIAL_FORMS": "0",
                "factmk_name7-MIN_NUM_FORMS": "0",
                "factmk_name7-MAX_NUM_FORMS": "1000",
                "factmk_name7-0-Factname": "",
                "factmk_name7-0-ROUTname": "",
                "factmk_name8-TOTAL_FORMS": "1",
                "factmk_name8-INITIAL_FORMS": "0",
                "factmk_name8-MIN_NUM_FORMS": "0",
                "factmk_name8-MAX_NUM_FORMS": "1000",
                "factmk_name8-0-Factname": "",
                "factmk_name8-0-ROUTname": "",
                "factmk_name9-TOTAL_FORMS": "1",
                "factmk_name9-INITIAL_FORMS": "0",
                "factmk_name9-MIN_NUM_FORMS": "0",
                "factmk_name9-MAX_NUM_FORMS": "1000",
                "factmk_name9-0-Factname": "",
                "factmk_name9-0-ROUTname": "",}
        
        rw_number = abnormal_df.iloc[i]['編號']
        filrer_df = abnormalfactname_df[abnormalfactname_df['ID'] == rw_number]
        
        if not filrer_df.empty:
            for each_i in range(filrer_df.shape[0]):
                factoryname = filrer_df.iloc[each_i]['factoryname']
                factoryname = changefactname(factoryname)
                makename = filrer_df.iloc[each_i]['mak']
                makename = changemakname(makename)

                fact_no = ''
                rout_no = ''
                
                if not factoryname:
                    fact_data[f"factmk_name{each_i}-0-Factname"] = fact_no
                else:                
                    fact_no = FACT_df[FACT_df['FACT_NA'] == factoryname]['FACT_NO'].iloc[0]
                    fact_data[f"factmk_name{each_i}-0-Factname"] = fact_no

                if not makename:
                    fact_data[f"factmk_name{each_i}-0-ROUTname"] = rout_no
                else:
                    rout_no = ROUT_df[ROUT_df['ROUT_NA']== makename]['ROUT_NO'].iloc[0]
                    fact_data[f"factmk_name{each_i}-0-ROUTname"] = rout_no
                
                if fact_data[f"factmk_name{each_i}-0-Factname"] and not fact_data[f"factmk_name{each_i}-0-ROUTname"]:
                    fact_data[f"factmk_name{each_i}-0-ROUTname"] = '07'
                
            
                abnormalfactna = AbnormalFactna()
                abnormalfactna.form_id = rw_number
                
                abnormalfactna.item = '0' + str(each_i + 1)
                abnormalfactna.factoryno = fact_no   
                abnormalfactna.factoryname = factoryname   
                abnormalfactna.makeno = rout_no   
                abnormalfactna.makename = makename                
                abnormalfactna.unit_price =  None if np.isnan(filrer_df.iloc[each_i]['單價']) else filrer_df.iloc[each_i]['單價']
                abnormalfactna.total_price = None if np.isnan(filrer_df.iloc[each_i]['總價']) else filrer_df.iloc[each_i]['總價']
                if fact_no or rout_no:  
                    abnormalfactna.save()
                    
                    
                if not abnormalmk_df[abnormalmk_df['CombinID'] == rw_number + '-' + str(each_i + 1)].empty:
                    abnormalmk = AbnormalMK()
                    print(abnormalmk_df[abnormalmk_df['CombinID'] == rw_number + '-' + str(each_i + 1)])
                    abnormalmk.mk_number = abnormalmk_df[abnormalmk_df['CombinID'] == rw_number + '-' + str(each_i + 1)]['MK單號'].iloc[0]
                    abnormalmk.form_id = rw_number
                    abnormalmk.item = '0' + str(each_i + 1)
                    _remark = abnormalmk_df[abnormalmk_df['CombinID'] == rw_number + '-' + str(each_i + 1)]['備註'].iloc[0]
                    abnormalmk.remarks = '' if _remark is None else _remark
                    abnormalmk.save()
                
        data.update(fact_data)        
        

        # 使用 filter 和 first 來尋找用戶，如果找不到用戶則返回 None
        applicant_username = all_user.filter(FullName=abnormal_df.iloc[i]['開單者']).first()
        applicant_username = applicant_username.username if applicant_username else 'Administrator'
        
        form = Form()        
        form.form_id = rw_number
        form.form_name = '重工單'
        form.applicant = applicant_username
        form.result = abnormal_df.iloc[i]['狀態']
        form.application_date = abnormal_df.iloc[i]['日期'].split()[0].replace("-","")
        # form.closing_date
      
        form.version_number = 'A'
        form.data =data
        # form.parents_form_id
        # form.resourcenumber
        # form.relationshipnumber

        form.save()
        print(form.applicant)        
        print('*'*120)
        		
        
        