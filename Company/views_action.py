from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from workFlow.Custom import group_required
from django.contrib.auth.models import Group
from .models import CustomUser, Level, Form, Process, Process_real, Process_history
from Company.GetData import get_employee_map
from workFlow.DataTransformer import querydict_to_dict, get_level_id, get_previous_station, GetWorkid, Get_station_choice, Get_listType, GetFormID, Clean_date, Get_Taiwan_Time
from .DataTransformer import check_different_dict, check_and_save_file, approved_transfor, filter_forms_condition, get_QAR_employee_data, get_history_level_count_map, Allform_get_station_chioce, vaild_job, count_language, count_tool, count_work_skill, count_factmk_name, get_resourcenumber_forms
from .DataTransformer import workid_to_name, save_process_history
import json
from django.views.generic import View
from workFlow.Appsettings import FORMURLS, ATTACHMENT_TRANSLATE, FORMURLS_RESET, FROM_AUTHORITY, FORMURLS_ONLYCHANGEDATA, RECRUITMENTINTERVIEWEVALUATION_TO_CHECK, RECRUITMENTINTERVIEWEVALUATION_TO_PARSER, JOBDESCRIPTION_TO_CHECK, PERSONNELADDITIONAPPLICATION_TO_CHECK
from workFlow.Appsettings import HEAVYWORKORDER_TO_CHECK, JOBDESCRIPTION_OTHER_TO_CHECK, PERSONNELADDITIONAPPLICATION_TO_CHECK2
from django.contrib.auth.mixins import LoginRequiredMixin
from HumanResource.views import RecruitmentInterviewEvaluation, PersonnelAdditionApplication, jobDescription, AccessControlPermission
from HumanResource.BusinessCardRequest_views import BusinessCardRequestView
from .models import Form, CustomUser
from .Email_Send import short_term_QAR_send_email, send_email
from . action_deal_with import form_action_deal_with
import re
from QualityAssurance.models import AbnormalFactna
from QualityAssurance.DataTransformer import generate, get_item_dict, create_abnormal
from Database import SQL_operate
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import CreateView
from workFlow.Custom import GroupRequiredMixin
from django.contrib import messages

def update_site_record(station_choice, process_real: Process_real, next_station, This_site_record, previous_station):
    if station_choice in ['核准', '確認']:
        # 回到一般狀況
        if process_real.endorsement_allow is None:
            process_real.site_record = next_station  # 站點記錄
        else:
            process_real.site_record = This_site_record

    elif station_choice in ['退簽', '結案', '加簽', '取回']:
        process_real.site_record = next_station   # 站點記錄 還是會有下一站當最後一站

    elif station_choice in ['同意加簽', '不同意加簽']:
        process_real.site_record = This_site_record  # 加簽保持原站
    
    elif station_choice in ['駁回']:
        # 這邊用來更新 及時運行的站點無誤
        process_real.site_record = previous_station



def update_next_action(request,form_id):
    # 這邊要新增一段 判斷下一個使用者自己有沒有在裡面
    forms = approved_transfor(request)
    return any([True for each_form in forms if each_form.form_id == form_id])

    



@login_required
def action(request, form_id):
    """
        使用者用來提交的處理POST的邏輯

    Args:
        request (_type_): _description_
        form_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    post_data = querydict_to_dict(request.POST)
    station_choice = post_data.pop('station_choice', '')
    _process_id = post_data.pop('process_id', '')
    This_site_record = post_data.pop('This_site_record', '')
    next_station = post_data.pop('next_station', '')
    previous_station = post_data.pop('previous_station', '')
    process_real = Process_real.objects.get(
        process_id=_process_id)
    process = Process.objects.get(
        process_id=_process_id)  # 這邊必須要傳入物件

    # 各表單特殊處理區域
    _form_obj = Form.objects.get(form_id=form_id)
    _form_name = _form_obj.form_name

    update_site_record(station_choice, process_real,
                       next_station, This_site_record, previous_station)

    if station_choice in ['核准', '確認']:
        process_real.endorsement_allow = None
        process_real.endorsement_approvers = None
        process_real.endorsement_count = 0
        process_real.temporaryapproval = None
        
        # 客訴紀錄單 # 回覆客訴處理的內容
        if next_station == '客訴處理員' and 'complaintResolutionStatus' in post_data:
            if post_data.get('complaintResolutionStatus'):
                form = Form.objects.get(form_id=form_id)
                form.data['internalprocessing'] = post_data.get(
                    'complaintResolutionStatus')
                form.save()
                
                # 客訴處理員完成之後, 業務人員希望快速得到通知
                send_email(CustomUser.objects.get(
                    username=form.applicant).email, Assign_email_str='everyday')

        # owner_form_name='客訴紀錄單', doc='當業務填寫了對於外部處理的東西之後保存起來'
        # owner_form_name='實驗測試申請單', doc='當實驗室要回覆使用者日期時'
        # owner_form_name='重工單', doc='預計完成日期,由生產管理員回覆'
        # owner_form_name='重工單', doc='經理核准之後，統一寄信給每個需要知道的人'
        form_action_deal_with(choice=station_choice).run(
            Form_objects=_form_obj, post_data=post_data)

        # 品異單 資料核實
        if "cause_analysis" in post_data and "temporary_measures" in post_data and 'permanent_disposal_countermeasures' in post_data:
            # 更新form表單裡面的狀態
            form = Form.objects.get(form_id=form_id)
            form.data['cause_analysis'] = post_data['cause_analysis']
            form.data['temporary_measures'] = post_data['temporary_measures']
            form.data['permanent_disposal_countermeasures'] = post_data['permanent_disposal_countermeasures']
            form.save()


        # 出圖依賴書 #當特助選擇了臨時加簽的人員之後,就要將臨時增加的人員加到實例裡面,讓系統可以通知臨時加簽的人
        if _form_name == '出圖依賴書' and (next_station == '研發主管發案確認' or next_station == '研發負責組別'):
            if "rdgroupSelect" in post_data:
                team_leader_selection = post_data['rdgroupSelect']
                # 確保 team_leader_selection 是一個列表
                if not isinstance(team_leader_selection, list):
                    team_leader_selection = [team_leader_selection]
                process_real.temporaryapproval = json.dumps(
                    team_leader_selection)
    
    elif station_choice in ['退簽', '結案', '加簽', '取回']:
        if station_choice == '加簽' and "endorsement_asigns" in post_data:
            process_real.endorsement_asign = json.dumps(
                post_data['endorsement_asigns'])

        # 更新矯正預防措施處理單
        if station_choice == '結案' and "complaint_reason" in post_data and "temporary_plan" in post_data:
            # 更新form表單裡面的狀態
            form = Form.objects.get(form_id=form_id)
            form.data['complaint_reason'] = post_data['complaint_reason']
            form.data['temporary_plan'] = post_data['temporary_plan']
            form.save()

        form_action_deal_with(choice=station_choice).run(
            Form_objects=_form_obj, post_data=post_data)

    elif station_choice in ['同意加簽', '不同意加簽']:
        endorsement_mode = ''
        # 1. 要判斷是否進入下一站
        # 2. 要判斷會簽搶簽的關係
        levels = Level.objects.filter(level_id__startswith=process.level_id)

        endorsement_manager = ''
        endorsement_group = []
        for _level in levels:
            if _level.station_name == This_site_record:
                endorsement_mode = _level.endorsement_mode
                endorsement_manager = _level.endorsement_manager
                endorsement_group = json.loads(
                    _level.endorsement_group)  # type: ignore

        # 搶簽
        if endorsement_mode == 'grab':
            if station_choice == '同意加簽':
                process_real.endorsement_allow = True
            elif station_choice == '不同意加簽':
                process_real.endorsement_allow = False
        # 會簽
        elif endorsement_mode == 'counter_sign':
            filter_user = []
            if endorsement_manager:
                filterUser = CustomUser.objects.filter(
                    username=endorsement_manager, is_active=True)
                if filterUser.exists():
                    filter_user = [user.username for user in filterUser]

            if endorsement_group:
                filter_user = list(
                    set(filter_user + GetWorkid(endorsement_group, CustomUser.objects.filter(is_active=True))))

            # 這邊還要判斷臨時加簽的
            if process_real.endorsement_asign:
                filter_user = list(
                    set(filter_user + json.loads(process_real.endorsement_asign)))

            filter_user_number = len(filter_user)
            process_real.endorsement_count += 1

        if process_real.endorsement_approvers is None:
            process_real.endorsement_approvers = [  # type: ignore
                [request.user.username, station_choice]]
        else:
            original_approvers = Get_listType(
                process_real.endorsement_approvers)
            original_approvers.append([request.user.username, station_choice])
            process_real.endorsement_approvers = original_approvers

        if endorsement_mode == 'counter_sign':
            if filter_user_number == process_real.endorsement_count:  # type: ignore
                target_num = True
                for workid, chioce in process_real.endorsement_approvers:
                    if chioce == '不同意加簽':
                        target_num = False
                process_real.endorsement_allow = target_num

    elif station_choice in ['駁回']:
        process_real.temporaryapproval = None

        form_action_deal_with( choice=station_choice).run(
            Form_objects=_form_obj, post_data=post_data)

    process_real.approval_status = [
        station_choice]   # 簽核狀態(站點選擇)

    process_real.approver = CustomUser.objects.get(
        username=request.user.username)  # 簽核者

    process_real.approval_opinion = post_data.pop(
        'approval_opinion', '')  # 簽核意見


    if station_choice in ['退簽', '結案', '取回']:
        process_real.process_status = "結束"  # 流程狀態
        process_real.approval_time = Get_Taiwan_Time()
        # 更新form表單裡面的狀態
        form = Form.objects.get(form_id=form_id)
        form.result = station_choice
        form.closing_date = process_real.approval_time
        form.save()

        if Form.objects.get(form_id=form_id).form_name == '名片申請單' and next_station == '名片製作':
            form = Form.objects.get(form_id=form_id)
            form.data['Releasedate'] = post_data.get('releasedate', '')
            form.data['ifRecycle'] = post_data.get('ifRecycle', '')
            form.save()
    else:
        process_real.process_status = "運行中"  # 流程狀態
        process_real.approval_time = Get_Taiwan_Time()
        process_real.save()  # 保存即時運行任務

    save_process_history(request, _process_id,
                         station_choice, next_station, process_real)

    if station_choice in ['取回']:
        return redirect("form_application")
    if station_choice in ['結案']:
        process_real.delete()  # 結案後就不需要再保留了 刪掉即可
        return redirect("approved")
    else:
        result = update_next_action(request=request,form_id = form_id)
        if result:
            url = reverse("form_information",args=[form_id])
            messages.success(request, '系統提示:由於系統偵測到下一關審核人員依然是您，請繼續完成審核動作!!')
            return redirect(reverse("form_information",args=[form_id]))
        return redirect("approved")





