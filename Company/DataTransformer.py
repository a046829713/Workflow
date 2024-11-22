from .models import Employee, Process, Process_real, CustomUser, Process_history, Form, Level, Attachment, get_upload_to
from workFlow.DataTransformer import get_level_id_not_num, get_process_id, GetFormApplicationDate, querydict_to_dict, GetFormID, get_combin_list
from workFlow.DataTransformer import GetWorkid, Get_listType, Get_otherworkid, Get_Taiwan_Time, Get_station_choice
from datetime import datetime
from workFlow.Appsettings import ATTACHMENT
import json
from typing import List, Optional, Union
# 用來緩存使用者資料
from django.core.cache import cache
from time import time
from django.db.models import Q
from .Database import SQL_operate
import re
# 所有關於流程的資料都會盡量集中在這裡處理,和全域的Dataframe的邏輯不同


def save_process_history(request, _process_id, station_choice, next_station, process_real: Process_real):
    process_history = Process_history()
    process_history.process_id = _process_id
    
    if station_choice in ['駁回']:
        process_history.site_record = next_station
    else:
        process_history.site_record = process_real.site_record

    process_history.approval_status = process_real.approval_status
    process_history.approver = CustomUser.objects.get(
        username=request.user.username)  # 簽核者
    process_history.approval_opinion = process_real.approval_opinion
    process_history.approval_time = process_real.approval_time
    process_history.save()


def change_department_head(data: list, applicant):
    """
    轉換department_head到各部門主管

    Args:
        data (_type_): _description_
        applicant (_type_): _description_

    Returns:
        _type_: _description_
    """
    new_combin = []
    # 取得所有需要簽核的關係圖 ['department_head', 'HR', '總經理室']
    for each_relationship in data:
        # 部門主管
        if each_relationship == 'department_head':
            # applicant :工號 1000530
            new_combin.append(Employee.objects.get(
                worker_id=applicant).department_level)
        else:
            # 取得團體權限
            new_combin.append(each_relationship)

    return new_combin


def save_process(form) -> Process:
    """
        命名為SAVE的原因是因為使用Create mothod
    """
    # 現在我們可以創建一個新的Process，並關聯到上述的Form和Level
    process = Process.objects.create(
        # 其實表單form_id好似永遠不會重複,但為了獨特性暫時用兩個一起加密
        process_id=get_process_id(form.form_id, form.version_number),
        form_id=form,  # 直接賦值Form實例,但我認為這個有點雞肋沒什麼用
        level_id=get_level_id_not_num(form.form_name, form.version_number),
    )

    return process


def create_process_real_and_save(level, process, applicant, endorsement_asign: Optional[List[str]] = None):
    """_summary_

    Args:
        level (_type_): _description_
        process (_type_): _description_
        applicant (_type_): _description_
        endorsement_asign (Optional[List[str]], optional): ['1000114', '1000035', '1000055']. Defaults to None.

    Returns:
        _type_: _description_
    """
    process_real = Process_real()
    process_real.process_id = process
    process_real.site_record = level.station_name   # 站點記錄
    process_real.approval_status = level.station_choice   # 簽核狀態(站點選擇)
    process_real.approver = CustomUser.objects.get(username=applicant)  # 簽核者
    process_real.approval_opinion = ''  # 簽核意見
    process_real.process_status = "運行中"  # 流程狀態
    process_real.approval_time = Get_Taiwan_Time()  # 簽核時間
    if endorsement_asign:
        if not isinstance(endorsement_asign, list):
            endorsement_asign = [endorsement_asign]
        process_real.endorsement_asign = json.dumps(endorsement_asign)
    process_real.save()
    return process_real


def create_process_history_and_save(level, process, applicant):
    process_history = Process_history()
    process_history.process_id = process.process_id
    process_history.site_record = level.station_name   # 站點記錄
    process_history.approval_status = level.station_choice
    process_history.approver = CustomUser.objects.get(
        username=applicant)  # 簽核者
    process_history.approval_opinion = ''  # 簽核意見

    process_history.approval_time = Get_Taiwan_Time()  # 簽核時間

    process_history.save()
    return process_history


def create_form_and_save(post_data, form_id, applicant):
    form = Form()
    form.form_id = form_id
    form.form_name = post_data.pop('form_name', '')
    form.applicant = applicant
    form.result = post_data.pop('result', '')  # 替换为实际的result
    form.application_date = GetFormApplicationDate(
        post_data.pop('application_date', ''))  # 假设申请日期为今天
    form.closing_date = post_data.pop('closing_date', '')  # 假设结案日期也为今天
    form.version_number = post_data.pop('version_number', '')
    form.parents_form_id = post_data.pop('parents_form_id', '')

    # 通常如果有來源單號都把它紀錄起來
    form.resourcenumber = post_data.pop('resource_no', '')
    form.data = post_data
    form.save()
    return form


def handle_process(form, applicant, endorsement_asign: Optional[List[str]] = None):
    """_summary_

    Args:
        form (_type_): _description_
        applicant (_type_): _description_
        endorsement_asign (list): 臨時需要加簽的人員
    """

    # 同時發起流程
    # 創造Process
    form = Form.objects.get(form_id=form.form_id)
    process = save_process(form)
    level = Level.objects.get(level_id=process.level_id + "_" + "001")
    create_process_real_and_save(level, process, applicant, endorsement_asign)
    create_process_history_and_save(level, process, applicant)


def check_and_save_file(form, request, check_repeat=False):
    """檢查並保存文件

    Args:
        form (_type_): _description_
        request (_type_): _description_
    """
    file_fields = ATTACHMENT[form.form_name][form.version_number]
    for field in file_fields:
        if field in request.FILES:
            if check_repeat:
                # 如果有同名的附件，删除它
                existing_attachments = Attachment.objects.filter(
                    name=field, form_id=form.form_id)
                for attachment in existing_attachments:
                    attachment.file.delete()
                    attachment.delete()
            attachment = Attachment(
                name=field, form_name=form.form_name, form_id=form.form_id, file=request.FILES[field])
            attachment.save()
            form.attachments.add(attachment)
    form.save()


def is_valid_and_to_send_process(request, form_id_Per=None):
    """
        保存form表單,並且送出簽核
    """
    post_data = querydict_to_dict(request.POST)

    if form_id_Per is None:
        form_id = GetFormID(post_data.pop('form_id', None))
    else:
        form_id = form_id_Per

    applicant = post_data.pop('applicant', '')
    form = create_form_and_save(post_data, form_id, applicant)
    check_and_save_file(form, request)
    handle_process(form, applicant)
    return form_id


def _filter_combin(_each_process, combin_list: list):
    """
        filter no use groups and remove its in combin list

        ['品檢組品異小組', '產研課品異小組']
    """
    # 過濾區塊
    # 將不需要顯示的過濾掉

    if _each_process.process_id.form_id.form_name == '品質異常單':
        if '產研課品異小組' in combin_list and '品檢組品異小組' in combin_list:
            if _each_process.process_id.form_id.data['source_category'] == '廠商進料不良':
                combin_list.remove('產研課品異小組')
            else:
                combin_list.remove('品檢組品異小組')

    return combin_list


def approved_transfor(request):
    """ 
    用來處理代辦審核
    在 Django 中，即使你沒有在 settings.py 中明確地配置緩存，你仍然可以使用緩存API。原因是Django提供了一個默認的緩存後端：django.core.cache.backends.locmem.LocMemCache，它是一個簡單的基於內存的緩存。

    LocMemCache 是一個進程級別的緩存，意味著它只在單一進程中存在。如果你的Django應用運行在多進程模式下（例如，多個uWSGI或Gunicorn工作進程），每個進程將有自己的緩存實例，這些實例之間是隔離的。

    默認情況下，這個緩存後端的配置是：
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    """
    begin_time = time()
    forms = []
    # 將每一個流程取出來 #並且取得
    all_process = Process_real.objects.select_related('process_id__form_id').all()
    all_user = cache.get('all_user')
    if all_user is None:
        all_user = CustomUser.objects.all()
        cache.set('all_user', all_user, 300)  # 緩存300秒

    all_employee = cache.get('all_employee')
    if all_employee is None:
        all_employee = Employee.objects.all()
        cache.set('all_employee', all_employee, 300)  # 緩存300秒

    for _each_process in all_process:
        approval_status = json.loads(
            _each_process.approval_status.replace("'", '"'))

        endorsement_allow = _each_process.endorsement_allow

        # 雖然之前都在加簽,但是一但endorsement_allow被允許之後或拒絕之後就不需要再走加簽的判斷了
        if ('加簽' not in approval_status and "同意加簽" not in approval_status and "不同意加簽" not in approval_status) or endorsement_allow is not None:
            combin_list = get_combin_list(_each_process, endorsement_allow)
            _filter_combin(_each_process, combin_list)

            # 申請人變數
            applicant = _each_process.process_id.form_id.applicant

            # 原本部級主管定義是一個人 這邊已經轉換為Group了(在workflow的系統當中,簽核者的身份都是以活字格的角色,或是團體下去思考)
            new_combin = change_department_head(combin_list, applicant)

            target_workid = GetWorkid(new_combin, all_user)

            Get_otherworkid(target_workid, new_combin, applicant,
                            _each_process.process_id.process_id)

            # 添加直屬主管的workid
            if 'direct_supervisor' in combin_list:
                for each_data in all_employee:
                    if each_data.worker_id == applicant:
                        target_workid.append(each_data.supervisor_id)

            # 不論如何這關都要簽(臨時會放入的這種),如果是加簽,還沒有考慮這種臨時指派的
            if _each_process.temporaryapproval:
                target_workid.extend(json.loads(
                    _each_process.temporaryapproval))


            # 當這個流程裡面沒有任何需要自己簽核的時候跳過
            if request.user.username in target_workid:
                forms.append(_each_process.process_id.form_id)

        else:
            # 取得所有流程裡面的事件,並且判斷目前執行到的最後一關的下一關是否有自己
            combin_list = []
            # 透過事件ID取得關卡狀態,並且判斷該站點是否需要自己否則跳過
            levels = Level.objects.filter(level_id__startswith=_each_process.process_id.level_id)

            for _level in levels:
                if _level.station_name == _each_process.site_record:
                    # 取得當下關卡的負責人員
                    station_manager = _level.endorsement_manager
                    station_group = _level.endorsement_group
                    station_group = station_group.replace("'", '"')
                    station_group = json.loads(station_group)

                    if isinstance(station_group, list):
                        combin_list = combin_list + station_group
                    else:
                        if station_group:
                            combin_list.append(station_group)

            target_workid = GetWorkid(combin_list, all_user)


            if station_manager:
                target_workid.append(station_manager)

            # 臨時需要加簽的人員
            if _each_process.endorsement_asign:
                target_workid.extend(json.loads(
                    _each_process.endorsement_asign.replace("'", '"')))

            # 當這個流程裡面沒有任何需要自己簽核的時候跳過,並且從未簽核過
            if request.user.username in target_workid:
                if _each_process.endorsement_approvers:

                    if request.user.username not in [workid for workid, chioce in Get_listType(_each_process.endorsement_approvers)]:
                        forms.append(_each_process.process_id.form_id)
                else:
                    forms.append(_each_process.process_id.form_id)

    print("消耗時間:",time() - begin_time)
    return forms


def check_different_dict(dict1: dict, dict2: dict):
    """
        找出键相同但值不同的项
    """
    return [key for key in dict1 if dict1.get(key) != dict2.get(key)]


def filter_forms_condition(start_date, end_date, applicant, form_name, status, form_number, check_if_result=False, result_in=False, queryset=None) -> list:
    """用來過濾想看的表單

    Args:
        start_date (): 起始日期
        end_date (_type_): 結束日期
        applicant (_type_): 申請人
        form_name (_type_): 表單名稱
        status (_type_): 狀態

    Returns:
        list: _description_
    """
    if queryset is None:
        queryset = Form.objects.all()
        

    # 如果設置了開始日期和結束日期，則過濾基於這個範圍
    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        queryset = queryset.filter(application_date__range=[
                                   start_date_obj, end_date_obj])

     # 如果設置了申請人，則過濾基於這個申請人
    if applicant:
        queryset = queryset.filter(applicant=applicant)

    # 如果設置了表單名稱，則過濾基於這個表單名稱
    if form_name:
        queryset = queryset.filter(form_name=form_name)

    # 如果設置了狀態，則過濾基於這個狀態
    if status:
        queryset = queryset.filter(result=status)

    # 如果設置了form_number，則只取得這個條件
    if form_number:
        queryset = queryset.filter(form_id=form_number)

    # 現在QuerySet篩選基於所有提供的條件
    if check_if_result:
        queryset = queryset.exclude(result='')

    if result_in:
        queryset = queryset.filter(result__in=['退簽', '結案'])

    return list(queryset)


def get_QAR_employee_data():
    employees = Employee.objects.all()

    a = {employee.worker_id: employee.department_level[:3] if employee.department_level !=
         'nan' else "總經理室" for employee in employees}  # type: ignore
    worktitle_map = {
        employee.worker_id: employee.position_name for employee in employees}

    all_data = {}
    for key, value in a.items():
        if value in all_data:
            all_data[value].append((key, key + " " + worktitle_map[key]))
        else:
            all_data[value] = [(key, key + " " + worktitle_map[key])]

    return all_data


def get_history_level_count_map(map_process, process_historys):
    """
        記錄歷史資料的次數來決定現在是第幾關
        map_process = [(each_process.form_id.form_id, each_process.process_id) for each_process in processes]
        process_historys = Process_history.objects.filter(process_id__in=processes_ids) 

    Args:
        process_historys (_type_): _description_
    """

    count_map = {}
    for each_process in process_historys:
        for row in map_process:
            if each_process.process_id == row[1]:
                if row[0] not in count_map:
                    count_map[row[0]] = 1
                else:
                    count_map[row[0]] += 1
    return count_map


def Allform_get_station_chioce(filtered_map):
    """
        為了要製作取回的功能,在設計的當下只有用在Allform
    """
    station_map = {}
    for each_form_id in filtered_map:
        process = Process.objects.get(form_id=each_form_id)
        process_real = Process_real.objects.get(process_id=process.process_id)

        approval_status = process_real.approval_status
        endorsement_allow = process_real.endorsement_allow

        # 用來將流程的歷史資料傳入
        ProcessHistory = Process_history.objects.filter(
            process_id=process.process_id)

        last_site_record = ProcessHistory.last().site_record

        station_choice, next_station, previous_station = Get_station_choice(
            process.level_id, last_site_record, approval_status, endorsement_allow)

        station_map.update({each_form_id: {'next_station': next_station,
                                           'previous_station': previous_station,
                                           'process_id': process.process_id,
                                           "This_site_record": last_site_record}
                            })
    return station_map


# def vaild_job(data: dict):


#     form_responsibilities = [
#         ("job_function_and_responsibilities_time_estimation", "工作職能和責任時間估計"),
#         ("work_hours_percentage", "工作時間百分比"),
#         ("time_frequency", "時間頻率"),
#     ]

#     vaildKeys = dict()
#     for key, value in data.items():
#         if 'job_function_and_responsibilities_time_estimation' in key or 'work_hours_percentage' in key or 'time_frequency' in key:
#             if value:
#                 for each_value in form_responsibilities:
#                     if each_value[0] in key:
#                         key = key.replace('-0-','-')
#                         key = key.replace('job_responsibilities','工作責任')
#                         key = key.replace(each_value[0],each_value[1])
#                         output = re.search(r'工作責任(\d+)-',key)
#                         output = output.group(1)
#                         if not(vaildKeys.get(output)):
#                             vaildKeys[output] = []
#                         vaildKeys[output].append(key)
#     return list(vaildKeys.values())

def vaild_job(data: dict):
    form_responsibilities = {
        "job_function_and_responsibilities_time_estimation": "工作職能和責任時間估計",
        "work_hours_percentage": "工作時間百分比",
        "time_frequency": "時間頻率",
    }

    vaildKeys = {}
    for key, value in data.items():
        if value and any(fr in key for fr in form_responsibilities):
            for fr_key, fr_value in form_responsibilities.items():
                if fr_key in key:
                    key = key.replace(
                        '-0-', '-').replace('job_responsibilities', '工作責任').replace(fr_key, fr_value)
                    match = re.search(r'工作責任(\d+)-', key)
                    if match:
                        idx = match.group(1)
                        vaildKeys.setdefault(idx, []).append(key)

    return list(vaildKeys.values())


def count_language(data: dict):
    count_ = 0
    for key, value in data.items():
        if 'language_abilities' in key:
            if '-language' in key or 'listen' in key or 'speak' in key or 'read' in key or 'write' in key:
                if value:
                    count_ += 1

    return count_


def count_tool(data: dict):
    count_ = 0
    for key, value in data.items():
        if 'Tool_expert' in key:
            if 'first_level' in key or 'second_level' in key or 'third_level' in key:
                if value:
                    count_ += 1

    return count_


def count_work_skill(data: dict):
    count_ = 0
    for key, value in data.items():
        if 'work_skill' in key:
            if 'skill_first_level' in key or 'skill_second_level' in key or 'skill_third_level' in key:
                if value:
                    count_ += 1

    return count_


def count_factmk_name(data: dict):
    count_ = 0
    for key, value in data.items():
        if 'factmk_name' in key:
            if 'Factname' in key or 'ROUTname' in key:
                if value:
                    count_ += 1

    return count_


def get_resourcenumber_forms(form_object, form_id):
    if form_object.resourcenumber:
        relationship_forms = Form.objects.filter(Q(resourcenumber=form_object.resourcenumber) | Q(
            resourcenumber=form_id) | Q(form_id=form_object.resourcenumber)).exclude(form_id=form_id)
    else:
        relationship_forms = Form.objects.filter(
            resourcenumber=form_id).exclude(form_id=form_id)

    return relationship_forms


def workid_to_name(work_ids: Optional[Union[List[str], str]]) -> str:
    """    
        統一用文字回傳好了
    Args:
        work_ids (Optional[Union[List[str], str]]): _description_

    Returns:
        str: _description_

    """
    out_str = ''
    if not isinstance(work_ids, list) and work_ids:
        work_ids = [work_ids]

    out_list = []

    if work_ids:
        all_user = CustomUser.objects.all()
        for work_id in work_ids:
            for user in all_user:
                if user.username == work_id:
                    out_list.append(user.FullName)

    out_str = ','.join(out_list)

    return out_str


def update_context_info(form_object, context: dict, request) -> None:
    """
        根據每一張表單,來更新相關的context
    """
    # 重工單廠商名稱
    # 製程名稱
    if form_object.form_name == '重工單':
        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")                
        
        FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
        FACT_map = {fact_no: fact_na for fact_no, fact_na in FACT_df.values}

        ROUT_df = ERP_sql.get_pd_data("select ROUT_NO,ROUT_NA from ROUT")
        ROUT_map = {rout_no: rout_na for rout_no, rout_na in ROUT_df.values}       
        
        
        context.update({"FACT_map": FACT_map, "ROUT_map": ROUT_map})

    if form_object.form_name == '招募面試評核表':
        unit_interviewer = context['form'].data['unit_interviewer']
        context['form_clean_data']['單位面試官'] = workid_to_name(unit_interviewer)
        hr_interviewer = context['form'].data['hr_interviewer']
        context['form_clean_data']['人資面試官'] = workid_to_name(hr_interviewer)

    if form_object.form_name == '客訴紀錄單':
        # 如果尚未擁有處理過的狀況(第一次回給業務採用公版)
        if 'internalprocessing' not in form_object.data:
            # 客服處理員的提示公版
            context.update({"CustomerServiceResponse": """初次回復:\n1.人物 who:\n\t相關員工/部門名稱：[涉及員工或部門名稱]\n2.事項 What:\n\t事件經過：[具體的事件描述]\n3.時間 When:\n\t事件發生時間:[具體的時間描述]\n4.地點 Where:\n\t發生問題的具體地點:[地點描述]\
                            \n5.物品Objects/Products involved:\n\t相關產品/服務：[涉及的產品或服務名稱]\n\t任何相關物品的詳細信息\n6.備註 Remarks:\n\t調查結果:[調查發現的主要內容]\n\t解決方案/補救措施：[提供的解決方案或採取的補救措施]\n\t預防措施:[為防止未來類似問題發生而製定的措施]\n\t其他資訊：[任何其他需要通知客戶的資訊]
            """})
        else:
            context.update(
                {"CustomerServiceResponse": form_object.data['internalprocessing']})

    # 當出圖依賴書需要確認的時候要把資料傳入
    if form_object.form_name == '出圖依賴書' and form_object.version_number == 'B':
        respone_groups = CustomUser.objects.filter(
            groups__name__in=['研發部副理', '產研課長'],
            is_active=True).distinct()

        context.update({'respone_groups': respone_groups})

        # 取得研發部的所有用戶，但排除研發部副理
        rd_groups = CustomUser.objects.filter(groups__name='研發部', is_active=True).exclude(
            groups__name='研發部副理').exclude(groups__name='產研課長').distinct()
        context.update({'rd_groups': rd_groups})

        # (角色為產研課長)
        product_reserchs = CustomUser.objects.filter(
            groups__name='產研課').distinct()
        context.update({'product_reserchs': product_reserchs})

        # 檢查當前用戶是否為產研課長
        current_user = CustomUser.objects.get(username=request.user.username)
        is_product_research_head = current_user.groups.filter(
            name='產研課長').exists()
        context.update({'is_product_research_head': is_product_research_head})
