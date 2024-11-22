import datetime
from Company.models import Form, Level, CustomUser, Process_history
import hashlib
import json
from typing import Optional, Union
from HumanResource.forms import LanguageAbilityFormset, JobResponsibilityFormSet, ToolFormSet, SkillFormSet
from QualityAssurance.forms import DisposalMethodFormset, FactMKFormset
import re
from time import time
from django.core.cache import cache
from datetime import datetime
import pytz


def record_time(func):
    def _warpper(*args, **kwargs):
        begin_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print("函數名稱:", func)
        print("使用時間:", end_time-begin_time)
        return result

    return _warpper


def Get_Taiwan_Time():
    """由於windows 系統和linux 時區不一致,所以特寫入此函數

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    taiwan_tz = pytz.timezone('Asia/Taipei')
    local_time = datetime.now(taiwan_tz)
    local_time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
    return local_time_str


def Get_Taiwan_Date():
    """由於windows 系統和linux 時區不一致,所以特寫入此函數

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    taiwan_tz = pytz.timezone('Asia/Taipei')
    local_date = datetime.now(taiwan_tz)
    local_date_str = local_date.strftime("%Y%m%d")
    # 這樣會打印台灣的當地日期，格式為 YYYYMMDD

    return local_date_str


def Get_station_choice(level_id: str, last_site_record: str, approval_status: str, endorsement_allow: Optional[bool]) -> list:
    """
        level_id 用來取得歷史紀錄的最後一個關卡的當下的站點選擇

        Return :
        next_station :下一站
        previous_station :上一站
    """
    station_choice = []
    levels = Level.objects.filter(level_id__startswith=level_id)
    approval_status = json.loads(approval_status.replace("'", '"'))
    target_id = ''

    for _level in levels:
        if _level.station_name == last_site_record:
            if '駁回' in approval_status:
                target_id = (f"{level_id}_" +
                             "{:03}".format(int(_level.level_id[-3:]) - 2))
                break

    for _level in levels:
        if _level.level_id == target_id:
            last_site_record = _level.station_name

    for _level in levels:
        if _level.station_name == last_site_record:
            next_station = _level.next_station
            previous_station = _level.previous_station

        # 加簽過程跑完
        if endorsement_allow is not None:
            if _level.station_name == last_site_record:
                station_choice = _level.station_choice
                station_choice = station_choice.replace("'", '"')
                station_choice = json.loads(station_choice)
        else:
            # 尚未跑完
            if _level.previous_station == last_site_record:
                # 取得當下關卡的站點選擇
                if '加簽' in approval_status or "同意加簽" in approval_status or "不同意加簽" in approval_status:
                    station_choice = ["同意加簽", '不同意加簽']
                else:
                    station_choice = _level.station_choice
                    station_choice = station_choice.replace("'", '"')
                    station_choice = json.loads(station_choice)

            # 如果沒有下一關了 但是加簽之後 又要繼續審核 有可能會有問題

    return station_choice, next_station, previous_station


def querydict_to_dict(querydict):
    """
        由於request post 的型態是dict的子類,轉換為正統的python dict
    """
    result = {}
    for key, value in querydict.lists():
        if len(value) == 1:
            result[key] = value[0]
        else:
            result[key] = value
    return result


def GetFormID(FormType):
    """
        將表單類型傳入
        表單ID(表單類型和日期編碼和張數)
        PAA
        PAA2023062600001
    """
    forms_with_FormType = Form.objects.filter(form_id__startswith=FormType)
    Today_str = Get_Taiwan_Date()
    last_count = '00001'

    for form in forms_with_FormType:
        if form.form_id[3:11] == Today_str:
            last_count = int(form.form_id[-5:]) + 1
            # 使用 `format()` 方法轉為 5 位數字字符串，不足的位數以 0 填充
            last_count = "{:05d}".format(last_count)
    return FormType + Today_str + last_count


def GetFormApplicationDate(application_date: str):
    """

    """
    return Get_Taiwan_Date()


def get_level_id(level_name: str, versionNumber: str):
    """
        會通用form_name
        level_name:(str):
            人員增補申請表

        versionNumber(str):A
            用來判斷版本
    """
    hashkey = GetHashKey(level_name + versionNumber)

    forms_filter = Level.objects.filter(level_id__startswith=hashkey)

    last_count = 0
    for form in forms_filter:
        last_count = max(last_count, int(form.level_id[-3:]))

    last_count += 1
    last_count = "{:03d}".format(last_count)
    out_str = hashkey + "_" + last_count

    return out_str


def get_level_id_not_num(level_name: str, versionNumber: str):
    return GetHashKey(level_name + versionNumber)


def get_process_id(form_id: str, versionNumber: str):
    return GetHashKey(form_id + versionNumber)


def GetHashKey(text: str):
    """ 
    forget why to encrypt user phone information
    將用戶的資料加密

    """
    hash_object = hashlib.sha256()
    hash_object.update(text.encode())
    return hash_object.hexdigest()


def get_previous_station(level_name: str, versionNumber: str, this_station_name):
    """
        level_name:(str):
            人員增補申請表

        versionNumber(str):A
            用來判斷版本

        用來取得上一個站點
    """
    out_str = ''
    hashkey = GetHashKey(level_name + versionNumber)

    forms_filter = Level.objects.filter(level_id__startswith=hashkey)
    for form in forms_filter:
        if this_station_name == form.next_station:
            out_str = form.station_name

    return out_str


def Get_otherworkid(target_workid: list, data: list, applicant, process_id):
    if 'applicant' in data:
        target_workid.append(applicant)

    # 出圖依賴書裡面有那種臨時取得上一關的狀況,只需要通知上一關的人
    if "previous_level_per" in data:
        ProcessHistory = Process_history.objects.filter(process_id=process_id)
        if ProcessHistory.last().approval_status == "['駁回']":
            second_last_history = ProcessHistory.order_by('-id')[1]
            # 當駁回 和上一關卡人時 會有邏輯上之衝突 # 取倒數第二個記錄
            target_workid.append(CustomUser.objects.get(
                id=second_last_history.approver_id).username)  # type: ignore
        else:
            target_workid.append(CustomUser.objects.get(
                id=ProcessHistory.last().approver_id).username)  # type: ignore


def GetWorkid(data: list, all_user):
    """

        data : 要判斷的Group列表
        將Group列表轉換為對應的工號
    Args:
        data (list): _description_
        all_user (CustomUser): all_user = CustomUser.objects.all()
    """
    user_group_map = cache.get('user_group_map')
    if user_group_map is None:
        user_group_map = {}
        for _user in all_user:
            user_group_name = _user.groups.values_list('name', flat=True)
            user_group_map.update({_user.username: user_group_name})

        cache.set('user_group_map', user_group_map, 300)  # 緩存300秒

    target_workid = []
    for work_id, user_group_names in user_group_map.items():
        for group_name in user_group_names:
            if group_name in data:
                target_workid.append(work_id)

    return target_workid


def get_combin_list(_each_process, endorsement: Optional[bool] = None):
    """ 取得所有需要判斷的團體

    Args:
        _each_process (_type_): _description_
        endorsement (_type_): _description_

    Returns:
        _type_: _description_
    """
    combin_list = []
    levels = Level.objects.filter(
        level_id__startswith=_each_process.process_id.level_id)

    for _level in levels:
        if (
            (endorsement == True and _level.station_name == _each_process.site_record) or
            (endorsement == False and _level.station_name == _each_process.site_record) or
           (endorsement is None and _level.previous_station == _each_process.site_record)):
            station_manager = _level.station_manager
            station_group = _level.station_group

            # 排除申請人自己
            if station_manager:
                combin_list.append(station_manager)

            if isinstance(station_group, list):
                combin_list.extend(station_group)
            else:
                if station_group:
                    combin_list.extend(json.loads(
                        station_group.replace("'", '"')))

    return combin_list


def Get_listType(data_str: str):
    """
        將字串轉換成list
    """
    return json.loads(data_str.replace("'", '"'))


def Clean_date(data: Union[dict, list], form_name: str, version_number: str):

    key_map = {}
    if form_name == '招募面試評核表' and version_number == 'A':
        key_map = {
            'user_name': "應徵者姓名",
            'interviewjobvacancies': "面試職缺",
            'interview_date': "面試日期",
            'character_behavior': "性格/人格偏好與價值觀,行為事例:(面試者所述之紀錄)",
            'character_control': "性格/人格偏好與價值觀,評語(面試官討論評估結論)",
            'character_option': "性格/人格偏好與價值觀,小結",
            'intent_behavior': "Intent意圖(獲取報酬、被滿足的方向),行為事例:(面試者所述之紀錄)",
            'intent_control': "Intent意圖(獲取報酬、被滿足的方向),評語(面試官討論評估結論)",
            'intent_option': "Intent意圖(獲取報酬、被滿足的方向),小結",
            'educational_backgroud_behavior': "學歷背景與天賦(教育學習歷程),行為事例:(面試者所述之紀錄)",
            'educational_backgroud_control': "學歷背景與天賦(教育學習歷程),評語(面試官討論評估結論)",
            'educational_backgroud_option': "學歷背景與天賦(教育學習歷程),小結",
            'Industry_knowledge_behavior': "業界知識、經驗與技能,行為事例:(面試者所述之紀錄)",
            'Industry_knowledge_control': "業界知識、經驗與技能,評語(面試官討論評估結論)",
            'Industry_knowledge_option': "業界知識、經驗與技能,小結",
            'person_self_behavior': "自我概念(一個人對自己的看法),行為事例:(面試者所述之紀錄)",
            'person_self_control': "自我概念(一個人對自己的看法),評語(面試官討論評估結論)",
            'person_self_option': "自我概念(一個人對自己的看法),小結",
            'learning_behavior': "對知識的追求與學習能力,行為事例:(面試者所述之紀錄)",
            'learning_control': "對知識的追求與學習能力,評語(面試官討論評估結論)",
            'learning_option': "對知識的追求與學習能力,小結",
            'contacts_behavior': "業界人脈,行為事例:(面試者所述之紀錄)",
            'contacts_control': "業界人脈,評語(面試官討論評估結論)",
            'contacts_option': "業界人脈,小結",
            'behavior_behavior': "行為觀察備註(如眼神,行為,服裝,姿態),行為事例:(面試者所述之紀錄)",
            'behavior_control': "行為觀察備註(如眼神,行為,服裝,姿態),評語(面試官討論評估結論)",
            'behavior_option': "行為觀察備註(如眼神,行為,服裝,姿態),小結",
            'interview_result': "面試結果",
            'hr_interviewer': "人資面試官",
            'corporate_sector': "所屬單位",
            'unit_interviewer': "單位面試官"
        }
    elif form_name == '人員增補申請表' and version_number == 'A':
        key_map = {
            'gender': '性別',
            'age': '年齡',
            'age_input': '年齡輸入',
            'licenses': '持有駕照',
            'department_school': '科系',
            'custom_department': '自訂系所',
            'work_experience': '經歷職務年資',
            'job_title': '職位名稱',
            'work_years': '工作年資',
            'school_knowledge': '學校知識',
            'work_knowledge': '業界知識/經驗',
            'certificates': '執照/證照',
            'additional_notes': '其他/備註',
            'apply_date': '申請日期',
            'add_job_title': '增補職稱',
            'add_people': '增補人數',
            'expand_structure_reason': '擴大組織結構原因',
            'reserve_force_reason': '儲備人力原因',
            'short_term_reason': '短期用工原因',
            'short_term_duration': '短期時長',
            'resignation_replacement_reason': '離職替代原因',
            'other_reason': '其他原因',
            'job_description': '職位描述',
            'interview_questions': '面試問題',
            'other_documents': '其他文件',
            'work_content': '對外刊登之工作內容與職務說明',
            'minimum_salary': '最低薪資',
            'maximum_salary': '最高薪資',
            'management_responsibility': '管理責任',
            'work_outside': '是否需要出差',
            'work_ability': '工作能力',
            'industry_experience': '業界經驗',
            'industry_connections': '業界人脈',
            'industry_knowledge': '業界知識',
            'school_knowledge_select': '學校知識',
            'business_knowledge': '企業知識',
            'csrfmiddlewaretoken': 'CSRF令牌',
            'action': '操作',
            'corporate_sector': '申請單位',
            'add_people_reason_choice': '增加人員原因',
            'add_people_reason': '增補原因',
            'custom_education_level': "學歷",
            'outside_add_job_title':"對外增補職稱"
        }
        formlanguage = [
            ("language", "語言"),
            ("listen", "聽"),
            ("speak", "說"),
            ("read", "讀"),
            ("write", "寫"),
        ]

        formTool = [
            ("first_level", "類別1"),
            ("second_level", "類別2"),
            ("third_level", "類別3"),
        ]
        formwork_skill = [
            ("skill_first_level", "類別1"),
            ("skill_second_level", "類別2"),
            ("skill_third_level", "類別3"),
        ]

        for i in range(5):
            for resp_symbol, resp_str in formlanguage:
                key_map[f"language_abilities{i}-0-{resp_symbol}"] = f"語言能力{i}-{resp_str}"

        for i in range(10):
            for resp_symbol, resp_str in formTool:
                key_map[f"Tool_expert{i}-0-{resp_symbol}"] = f"擅長工具{i}-{resp_str}"

        for i in range(10):
            for resp_symbol, resp_str in formwork_skill:
                key_map[f"work_skill{i}-0-{resp_symbol}"] = f"工作技能{i}-{resp_str}"

    elif form_name == '職務說明書' and version_number == 'A':
        key_map = {
            "form_id_Per": "表格ID_人員",
            "unit": "單位",
            "department": "部門",
            "group": "組別",
            "job_title_select": "職務名稱",
            "main_duty": "主要職責",
            "Occupation_category": "職系",
            "career_level": "職等",
            "licenses": "持有駕照",
            "education_level": "教育程度",
            "department_school": "科系要求",
            "custom_department": "自訂系所",
            "certificates": "專業證照/執照",
            "work_experience": "工作經驗",
            "job_title": "職稱",
            "work_years": "工作年數",
            "work_skill": "工作技能",
            "has_management": "是否有管理責任",
            "management_responsibility": "管理責任",
            "communication_internal_external_up": "對上",
            "communication_internal_external_down": "對下",
            "communication_internal_external_inner": "對內",
            "communication_internal_external_outer": "對外",
            "csrfmiddlewaretoken": "CSRF中介軟體權證",
            "action": "動作",
            'custom_certificates': '其他證照',
            'corporate_sector': "所屬單位",
            'custom_education_level': "自訂義教育程度"
        }

        form_responsibilities = [
            ("job_function_and_responsibilities_time_estimation", "工作職能和責任時間估計"),
            ("work_hours_percentage", "工作時間百分比"),
            ("time_frequency", "時間頻率"),
        ]

        formlanguage = [
            ("language", "語言"),
            ("listen", "聽"),
            ("speak", "說"),
            ("read", "讀"),
            ("write", "寫"),
        ]

        formTool = [
            ("first_level", "類別1"),
            ("second_level", "類別2"),
            ("third_level", "類別3"),
        ]
        formwork_skill = [
            ("skill_first_level", "類別1"),
            ("skill_second_level", "類別2"),
            ("skill_third_level", "類別3"),
        ]
        for i in range(20):
            for resp_eng, resp_chi in form_responsibilities:
                key_map[f"job_responsibilities{i}-0-{resp_eng}"] = f"工作責任{i}-{resp_chi}"

        for i in range(5):
            for resp_symbol, resp_str in formlanguage:
                key_map[f"language_abilities{i}-0-{resp_symbol}"] = f"語言能力{i}-{resp_str}"

        for i in range(10):
            for resp_symbol, resp_str in formTool:
                key_map[f"Tool_expert{i}-0-{resp_symbol}"] = f"擅長工具{i}-{resp_str}"

        for i in range(10):
            for resp_symbol, resp_str in formwork_skill:
                key_map[f"work_skill{i}-0-{resp_symbol}"] = f"工作技能{i}-{resp_str}"

    elif form_name == '出圖依賴書' and (version_number == 'A' or version_number == 'B'):
        key_map = {
            "form_id": "表單ID",
            "ApplicationDate": "申請日期",
            "QuotationScheduledDate": "預計報價日期",
            "newProductNumber": "新產品編號",
            "newProductName": "新產品名稱",
            "EstimatedAmount": "預計數量",
            "MOQ": "最小訂購量",
            "client": "客戶",
            "drawing": "圖紙",
            "sample": "樣品",
            "design_procedure": "設計流程",
            "usage": "用途",
            "description": "描述",
            "specification": "規格",
            "engineer_in_charge": "負責工程師",
        }
    elif form_name == '會議記錄' and version_number == 'A':
        key_map = {
            "iso_file_no": "ISO表單編號",
            "newProductName": "產品料號",
            "conferenceName": "會議名稱",
            "conference_start_datetime": "會議起始時間",
            "conference_end_datetime": "會議結束時間",
            "attendees": "與會人員",
            "meeting_place": "會議場所",
            "meeting_moderator": "會議主持人",
            "meeting_address": '會議地址',
            'content': "內容概要"
        }
    elif form_name == '客訴紀錄單' and (version_number == 'A' or version_number == 'B'):
        key_map = {
            "customer_number": '客戶編號',
            "country": '國家',
            "prod_no": "料號",
            "Complaintcontent": "客訴內容",
            "internalprocessing": "內部處理",
            "externalprocessing": "外部處理",
            "Attachment_path_one": "附件路徑1",
            "Attachment_path_two": "附件路徑2",
            "Attachment_path_three": "附件路徑3",
            "Attachment_path_four": "附件路徑4",
            "Attachment_path_five": "附件路徑5",
            "Attachment_path_six": "附件路徑6",
            "followupafterthreemonths": "三個月後追蹤",
            "Complaint_type": "客訴類別",
            'prod_type': "產品類別",
        }
    elif form_name == '矯正預防措施處理單' and version_number == 'A':
        key_map = {
            "complaint_reason": "不良原因",
            "temporary_plan": "臨時對策",
            "permanent_countermeasures": "永久對策",
            "happen_again": "防止再發生(後續追蹤)"
        }
    elif form_name == '品質異常單' and version_number == 'A':
        key_map = {
            "model_number": "型號代碼",
            "model_name": "型號名稱",
            "part_name_and_number": "料號品名",
            "source_category": "來源類別",
            "complaint_number": "客訴單號",
            "customer_number": "客戶編號",
            "batch_number": "批號",
            "purchase_number": "採購單號",
            "fact_number": "廠商編號",
            "batch_sizes": "批量",
            "manufacturing_order": "製令單號",
            "assemble": "組裝單位",
            "material_status": "料件狀態",
            "Exception_description": "異常說明",
            "exception_category": "異常類別",
            "disposal_method": "處置方式",
            "number_retries": "再發次數",
            "cause_analysis": "原因分析",
            "temporary_measures": "暫時處置對策",
            "permanent_disposal_countermeasures": "永久處置對策",
            "rework_order": "重工單",
            "other_disposition_documents": "其他處置單據",
            "remark_area": "備註",

        }
        form_disposal_methods = [
            ("part_name_and_number", "料號品名"),
            ("exception_category", "異常類別"),
            ("disposal_way", "處置方式"),
            ("responsible_unit", "責任單位"),
        ]

        for i in range(12):
            for resp_eng, resp_chi in form_disposal_methods:
                key_map[f"disposal_method{i}-0-{resp_eng}"] = f"異常相關{i}-{resp_chi}"
    elif form_name == '樣品確認單' and version_number == 'A':
        key_map = {
            "iso_file_no": "文件編號(ISO)",
            "marchine_model": "機種",
            "sample_order_number": "樣品訂單號碼",
            "customer_number": "客戶名稱",
            "sample_type": "樣品型態",
            "othersample_type": "其他樣品型態",
            "version": "樣品圖面及版本",
            "Function_is_qualified": "功能<使用規格確認書>開發",
            "design_is_qualified": "設計尺寸比對-開發",
            "smoothness_is_qualified": "順暢度",
            "noise_is_qualified": "異音",
            "gap_check_is_qualified": "間隙檢查",
            "strength_is_qualified": "強度",
            "assembly_method_is_qualified": "組裝方式",
            "adjustment_method_is_qualified": "調整方式",
            "processing_manufacturability_is_qualified": "加工可製造性",
            "plastic_material_is_qualified": "塑膠材質",
            "exterior_is_qualified": "外觀",
            "carry_is_qualified": "搬運",
            "durability_test_discussion_is_qualified": "耐久測試討論",
            "cost_review_is_qualified": "成本再檢討",
            "easy_replacement_items_is_qualified": "易更換物品之便利性",
            "oil_glue_is_qualified": "上油上膠",
            "content": "測試內容與結果",
        }
    elif form_name == '重工單' and (version_number == 'A' or version_number == 'B'):
        key_map = {
            'quantity': '數量',
            'responsible_unit': '責任單位',
            'paying_unit': '付費單位',
            'heavy_industry_information': '重工訊息來源',
            'estimated_completion_date': '預計完工日',
            'Heavy_industry_projects': '重工項目',
            'rebuild_reason': '重工原因',
            'source_notes': '來源備註',
            'remark': '備註',
            'prod_no_before': '產品編號(重工前)',
            'prod_name_before': '品名規格(重工前)',
            'prod_name_after': '品名規格(重工後)',
            'prod_no_after': '產品編號(重工後)',
            'pay_after_heavy_work': '重工後處置',
            'io_number': 'IO單號',
            "Withdraw_TYPE":"來源類別"
        }
        factmk_names = [
            ("Factname", "廠商名稱"),
            ("ROUTname", "製程名稱"),
        ]

        for i in range(10):
            for resp_symbol, resp_str in factmk_names:
                key_map[f"factmk_name{i}-0-{resp_symbol}"] = f"製程廠商{i}-{resp_str}"
    elif form_name == '實驗測試申請單' and version_number == 'A':
        key_map = {
            'test_reason': '測試原因',
            'test_type': '測試類別',
            'prod_type': '產品類別',
            'prod_number': '產品型號',
            'remark': '備註',
            'sample_provider': '樣品提供',
            'sample_provider_remark': '樣品備註',
            'estimated_completion_date': '預計完成日期',
            'Compet_prod_number': '競品型號',
            "tags":"標籤選擇",
            "Compet_corporation":"競品公司名稱",
            "sample_num":"樣品數量",
            "if_destroy_remark":"破壞原因",
            "if_back_remark":"歸還提供者原因",
            "Exception_date":"期望繳交日期",
            "if_destroy":"是否可破壞",
            "if_back":"是否歸還提供者",
            "if_ER_remark":"實驗室備註"

        }
    elif form_name == '門禁權限申請單' and version_number == 'A':
        key_map = {
            'ApplicationCategory': '申請類別',
            'secret_card_number': '門禁卡片號碼',
            'requestforaccess': '申請權限',
            'application_reason': '申請原因',



        }
    elif form_name == '名片申請單' and version_number == 'A':
        key_map = {
            'english_name': '英文名字',
            'Internalprofessionaltitle': '對內職稱',
            'Externalprofessionaltitle': '對外職稱',
            'Englishprofessionaltitle': '英文職稱',
            'ExtensionNumber': '分機號碼',
            'Fax': '傳真號碼',
            'email': '電子郵件地址',
            "Reasonforapplication": "申請原因",
            "boxes": '申請名片盒數',
            "Releasedate": "發放日期",
            "ifRecycle": "是否回收舊卡片",
            "ifremainingamount": "名片是否有剩餘",
            "Skype_number": "Skype"
        }
    if isinstance(data, dict):
        parser_data = {}
        hidden_key = []

        for key, value in data.items():
            if key in ['form_id_Per', 'csrfmiddlewaretoken', 'action', 'unit_configuration', 'job_description', 'interview_questions', 'other_documents', 'parents_form_id']:
                continue

            elif ('language_abilities' in key or 'job_responsibilities' in key or 'Tool_expert' in key or "disposal_method" in key or 'work_skill' in key or 'factmk_name' in key) and 'TOTAL_FORMS' in key:
                continue
            elif ('language_abilities' in key or 'job_responsibilities' in key or 'Tool_expert' in key or "disposal_method" in key or 'work_skill' in key or 'factmk_name' in key) and 'INITIAL_FORMS' in key:
                continue
            elif ('language_abilities' in key or 'job_responsibilities' in key or 'Tool_expert' in key or "disposal_method" in key or 'work_skill' in key or 'factmk_name' in key) and 'MIN_NUM_FORMS' in key:
                continue
            elif ('language_abilities' in key or 'job_responsibilities' in key or 'Tool_expert' in key or "disposal_method" in key or 'work_skill' in key or 'factmk_name' in key) and 'MAX_NUM_FORMS' in key:
                continue

            # 跳過沒有使用到的工作能力欄位
            elif 'job_responsibilities' in key and not value:
                hidden_key.extend(re.findall(r'job_responsibilities\d+', key))
                continue

            elif 'Tool_expert' in key and not value:
                hidden_key.extend(re.findall(r'Tool_expert\d+', key))
                continue

            elif 'work_skill' in key and not value:
                hidden_key.extend(re.findall(r'work_skill\d+', key))
                continue

            elif 'disposal_method' in key and not value:
                hidden_key.extend(re.findall(r'disposal_method\d+', key))
                continue

            elif 'language_abilities' in key and not value:
                hidden_key.extend(re.findall(r'disposal_method\d+', key))
                continue

            elif 'factmk_name' in key and not value:
                hidden_key.extend(re.findall(r'factmk_name\d+', key))
                continue

            elif 'job_responsibilities' in key and re.findall(r'job_responsibilities\d+', key)[0] in hidden_key:
                continue

            elif key in key_map:
                new_key = key_map[key]
                parser_data.update({new_key: value})
            else:
                print("剩下沒有判斷到的", key)

        return parser_data
    elif isinstance(data, list):
        parser_data = []
        if data:
            for key in data:
                if key in key_map:
                    parser_data.append(key_map[key])

        return parser_data
    else:
        raise ValueError("Data should be of type dict or list.")


def get_formsets(form_name, form_version, data=None, form_number: int = 0):
    "TOOL 不是表單喔 只是一個包裝後的FormSet"
    all_form_set = {
        "人員增補申請表": {
            "A": LanguageAbilityFormset
        },
        "人員補增申請表測試": {
            "A": LanguageAbilityFormset
        },
        "職務說明書": {
            "A": JobResponsibilityFormSet
        },
        "TOOL": {
            "A": ToolFormSet},
        "品質異常單": {
            "A": DisposalMethodFormset},
        "SKILL": {
            "A": SkillFormSet
        },
        "重工單": {
            "A": FactMKFormset,
            "B": FactMKFormset
        },
    }

    form_setprefix = {
        "人員增補申請表": {
            "A": 'language_abilities'
        },
        "人員補增申請表測試": {
            "A": 'language_abilities'
        },
        "職務說明書": {
            "A": 'job_responsibilities'
        },
        "TOOL": {
            "A": 'Tool_expert'},

        "品質異常單": {
            "A": 'disposal_method'},
        "SKILL": {
            "A": 'work_skill'},
        "重工單": {
            "A": 'factmk_name',
            "B": 'factmk_name'
        },
    }

    formsets = [
        all_form_set[form_name][form_version](
            data, prefix=form_setprefix[form_name][form_version] + f'{i}') for i in range(form_number)

    ]

    if len(formsets) < form_number:
        formsets.extend([all_form_set[form_name][form_version](
            None, prefix=form_setprefix[form_name][form_version] + f'{i}') for i in range(form_number - len(formsets))])

    return formsets


def parser_object_error(object):
    """
        to print error by html

    Args:
        object (_type_): like this check_form.errors
    """
    # 获取表单验证错误
    form_errors = object.as_data()

    # 可选：转换错误为字符串，以便在模板中显示
    error_messages = {}
    for field, errors in form_errors.items():
        error_messages[field] = [str(e) for e in errors]

    print(error_messages)
