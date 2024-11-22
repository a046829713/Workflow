from django.shortcuts import render, redirect
from workFlow.Custom import group_required
from django.urls import reverse
from .forms import RecruitmentInterviewEvaluationForm, PersonnelAdditionApplicationForm, jobDescriptionForm, LanguageAbilityFormset
from .forms import AccessControlPermissionForm
from django.http import HttpResponseRedirect
from Company.models import Form, Process, Level, Process_real, Process_history, CustomUser
from workFlow.DataTransformer import querydict_to_dict, GetFormID, get_formsets
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from workFlow import Appsettings
from django.http import JsonResponse, HttpResponseNotFound
import os
from workFlow.settings import BASE_DIR
from django.http import FileResponse
# Create your views here.
from typing import Optional
from workFlow.Appsettings import FORMURLS_ONLYCHANGEDATA
from workFlow.Custom import GroupRequiredMixin
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file, filter_forms_condition, is_valid_and_to_send_process
from workFlow.Appsettings import FORM_INFOMATION
import re
from Company.models import Employee
import re


def ApprovalFrom(request):
    ALL_forms = [
        ['RecruitmentInterviewEvaluationFormWithoutArg', "招募面試評核表", "1"],
        ['PersonnelAdditionApplicationFormWithoutArg', '人員增補申請表', "1"],
        ['jobDescriptionFormWithoutArg', '職務說明書', "1"],
        ['AccessControlPermissionFormWithoutArg', '門禁權限申請單', "1"]
    ]

    # Preprocess the URLs
    for form in ALL_forms:
        form[0] = reverse(form[0])  # Replace the URL name with actual URL

    # "0是私有" ,"1是公有"
    return render(request, "HumanResource/HR_index.html", {
        "ALL_forms": ALL_forms,
    })


class RecruitmentInterviewEvaluation(LoginRequiredMixin, View):
    def get(self, request):
        form = RecruitmentInterviewEvaluationForm()
        form_sys_info = Appsettings.FormCodes['招募面試評核表']
        return render(request, "HumanResource/RecruitmentInterviewEvaluation.html", {'form': form, "form_sys_info": form_sys_info, 'form_id_Per': ""})

    def post(self, request, form_id_Per=None, finish=None, Reset=False):
        form_sys_info = Appsettings.FormCodes['招募面試評核表']
        check_form = RecruitmentInterviewEvaluationForm(request.POST)

        # 第一次直接提交表單簽核
        if form_id_Per is None:
            if check_form.is_valid():
                # 获取表单数据
                post_data = querydict_to_dict(request.POST)
                # 變數紀錄
                applicant = post_data.pop('applicant', '')
                form_id = GetFormID(post_data.pop('form_id', None))
                # 创建一个新的Form对象(就算資料庫裏面有也會因為再次保存而覆蓋掉)
                form = create_form_and_save(post_data, form_id, applicant)
                check_and_save_file(form, request)
                handle_process(form, applicant)
                return redirect("index")
            else:
                error_title = '資料驗證失敗請重新檢查資料'
                # 如果验证失败，将表单重新渲染并显示错误信息
                return render(request, 'HumanResource/RecruitmentInterviewEvaluation.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
        else:
            if finish:
                # 获取表单数据
                if check_form.is_valid():
                    post_data = querydict_to_dict(request.POST)
                    # 變數紀錄
                    applicant = post_data.pop('applicant', '')
                    # 创建一个新的Form对象(就算資料庫裏面有也會因為再次保存而覆蓋掉)
                    form = create_form_and_save(
                        post_data, form_id_Per, applicant)
                    check_and_save_file(form, request, check_repeat=True)
                    handle_process(form, applicant)
                    return redirect("index")
                else:
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果验证失败，将表单重新渲染并显示错误信息
                    return render(request, 'HumanResource/RecruitmentInterviewEvaluation.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = RecruitmentInterviewEvaluationForm(form.data)
                return render(request, "HumanResource/RecruitmentInterviewEvaluation.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id})


class PersonnelAdditionApplication(LoginRequiredMixin, View):
    """ LoginRequiredMixin 判斷是否已經登入 """

    def get(self, request):
        # 在這裡處理GET請求
        form = PersonnelAdditionApplicationForm()
        form_sys_info = Appsettings.FormCodes['人員增補申請表']

        formsets = get_formsets('人員增補申請表', 'A', data=None, form_number=5)

        SkillFormSets = get_formsets(
            'SKILL', "A", data=None, form_number=10)
        Toolformsets = get_formsets(
            'TOOL', "A", data=None, form_number=10)
        context = {'form': form,
                   'formsets': formsets,
                   'form_id_Per': '',
                   "Toolformsets": Toolformsets,
                   "form_sys_info": form_sys_info,
                   "SkillFormSets": SkillFormSets}

        return render(request, "HumanResource/PersonnelAdditionApplication.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=None, OnlyChangeData=False):
        form_sys_info = Appsettings.FormCodes['人員增補申請表']
        # 如果表單有附件的也要同時檢查
        check_form = PersonnelAdditionApplicationForm(
            request.POST, request.FILES)

        if form_id_Per is None:
            if check_form.is_valid():
                # 获取表单数据
                post_data = querydict_to_dict(request.POST)
                # 變數紀錄
                applicant = post_data.pop('applicant', '')
                form_id = GetFormID(post_data.pop('form_id', None))
                # 创建一个新的Form对象(就算資料庫裏面有也會因為再次保存而覆蓋掉)
                form = create_form_and_save(post_data, form_id, applicant)
                check_and_save_file(form, request)
                handle_process(form, applicant)
                return redirect("index")
            else:
                # 由於人員增補申請表不太可能會驗證不過,所以沒有針對驗證失敗後的附件保存
                formsets = get_formsets(
                    '人員增補申請表', 'A', data=check_form.data, form_number=5)
                Toolformsets = get_formsets(
                    'TOOL', "A", data=check_form.data, form_number=10)
                SkillFormSets = get_formsets(
                    'SKILL', "A", data=check_form.data, form_number=10)

                error_title = check_form.errors
                # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                return render(request, 'HumanResource/PersonnelAdditionApplication.html', {'form': check_form, 'formsets': formsets, "Toolformsets": Toolformsets, "form_sys_info": form_sys_info, 'form_id_Per': "", "SkillFormSets": SkillFormSets, "error_title": error_title})
        else:
            if finish:
                if check_form.is_valid():
                    # 获取表单数据
                    post_data = querydict_to_dict(request.POST)
                    # 變數紀錄
                    applicant = post_data.pop('applicant', '')
                    # 创建一个新的Form对象(就算資料庫裏面有也會因為再次保存而覆蓋掉)
                    form = create_form_and_save(
                        post_data, form_id_Per, applicant)
                    check_and_save_file(form, request, check_repeat=True)
                    handle_process(form, applicant)
                    return redirect("index")
                else:
                    # 由於人員增補申請表不太可能會驗證不過,所以沒有針對驗證失敗後的附件保存
                    formsets = get_formsets(
                        '人員增補申請表', 'A', data=check_form.data, form_number=5)
                    Toolformsets = get_formsets(
                        'TOOL', "A", data=check_form.data, form_number=10)
                    SkillFormSets = get_formsets(
                        'SKILL', "A", data=check_form.data, form_number=10)
                    # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                    return render(request, 'HumanResource/PersonnelAdditionApplication.html', {'form': check_form, 'formsets': formsets, "Toolformsets": Toolformsets, "form_sys_info": form_sys_info, 'form_id_Per': "", "SkillFormSets": SkillFormSets})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                if form.resourcenumber:
                    form.data.update({"resource_no": form.resourcenumber})
                form = PersonnelAdditionApplicationForm(form.data)
                formsets = get_formsets(
                    '人員增補申請表', 'A', data=form.data, form_number=5)
                Toolformsets = get_formsets(
                    'TOOL', "A", data=form.data, form_number=10)
                SkillFormSets = get_formsets(
                    'SKILL', "A", data=form.data, form_number=10)
                return render(request, "HumanResource/PersonnelAdditionApplication.html", {'form': form, 'formsets': formsets, "Toolformsets": Toolformsets, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, 'Reset': Reset, 'parents_form_id': parents_form_id, "SkillFormSets": SkillFormSets, "OnlyChangeData": OnlyChangeData})


class jobDescription(LoginRequiredMixin, View):
    def get_accurate_sector(self, check_unit):  
        """
            只要丟入使用者的部門，或是相關資訊，應該要返回轄下部門。
        """   
        # 定义正则表达式模式
        patterns = {
            '室': r'.*室$',# 匹配以 "室" 结尾的字符串
            '部': r'.*部$',# 匹配以 "部" 结尾的字符串
            '組': r'.*組$',# 匹配以 "組" 结尾的字符串
            '課': r'.*課$',# 匹配以 "課" 结尾的字符串
        }

        # 获取所有的单位名称
        units = set(Employee.objects.values_list('unit', flat=True))

        # 用于存储分类结果
        classified_units = {'室': [], '部': [], '組': [], '課': []}
            
        # 判斷哪個分類
        for unit in units:
            for category, pattern in patterns.items():
                if re.match(pattern, unit):
                    classified_units[category].append(unit)
                    break
        
        classified_units['部'] =  classified_units['部'] + ['資材部']
        target_category = ''

        # 输出分类结果
        for category, unit_list in classified_units.items():
            for unit in unit_list:
                if check_unit == unit:
                    target_category = category            
                    break

        corporate_sector = FORM_INFOMATION['CORPORATE_SECTOR_CHOICES']

        if target_category == '室':
            return corporate_sector
        
        elif target_category in  ['部','課','組']:
            return [ _sector for _sector in corporate_sector if check_unit in _sector[0]]

        else:
            return []
        
    def get(self, request):
        form = jobDescriptionForm()
        form_sys_info = Appsettings.FormCodes['職務說明書']

        job_formsets = get_formsets(
            form_sys_info[0], form_sys_info[2], data=None, form_number=20)

        formsets = get_formsets(
            '人員增補申請表', 'A', data=None, form_number=5)

        Toolformsets = get_formsets(
            'TOOL', "A", data=None, form_number=10)

        SkillFormSets = get_formsets(
            'SKILL', "A", data=None, form_number=10)

        context = {'form': form,
                   'formsets': formsets,
                   "job_formsets": job_formsets,
                   "Toolformsets": Toolformsets,
                   "SkillFormSets": SkillFormSets,
                   "form_sys_info": form_sys_info,
                   'form_id_Per': ""}

        # 申請人就只能自己下面的人下去選擇        
        # 生產部經理又兼任資材部經理
        if request.user.username == '1000295':
            unit_production = self.get_accurate_sector(Employee.objects.get(worker_id = request.user).unit)
            form.fields['corporate_sector'].choices = unit_production + self.get_accurate_sector("資材部")
        else:
            form.fields['corporate_sector'].choices = self.get_accurate_sector(Employee.objects.get(worker_id = request.user).unit)
        
        return render(request, "HumanResource/jobDescription.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=None, OnlyChangeData=False):
        form_sys_info = Appsettings.FormCodes['職務說明書']
        check_form = jobDescriptionForm(request.POST)

        if form_id_Per is None:
            if check_form.is_valid():
                is_valid_and_to_send_process(request, form_id_Per)
                return redirect("index")
            else:
                job_formsets = get_formsets(
                    form_sys_info[0], form_sys_info[2], data=check_form.data, form_number=20)

                formsets = get_formsets(
                    '人員增補申請表', 'A', data=check_form.data, form_number=5)
                Toolformsets = get_formsets(
                    'TOOL', "A", data=check_form.data, form_number=10)

                SkillFormSets = get_formsets(
                    'SKILL', "A", data=check_form.data, form_number=10)

                error_title = f'資料驗證失敗請重新檢查資料,錯誤訊息如下:{check_form.errors}'
                # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                return render(request, 'HumanResource/jobDescription.html', {'form': check_form, 'formsets': formsets, "job_formsets": job_formsets, "Toolformsets": Toolformsets, "SkillFormSets": SkillFormSets, "form_sys_info": form_sys_info, 'form_id_Per': "", 'error_title': error_title})
        else:
            if finish:
                if check_form.is_valid():
                    is_valid_and_to_send_process(request, form_id_Per)
                    return redirect("index")
                else:
                    job_formsets = get_formsets(
                        form_sys_info[0], form_sys_info[2], data=check_form.data, form_number=20)

                    formsets = get_formsets(
                        '人員增補申請表', 'A', data=check_form.data, form_number=5)

                    Toolformsets = get_formsets(
                        'TOOL', "A", data=check_form.data, form_number=10)

                    SkillFormSets = get_formsets(
                        'SKILL', "A", data=check_form.data, form_number=10)
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                    return render(request, 'HumanResource/jobDescription.html', {'form': check_form, 'formsets': formsets, "job_formsets": job_formsets, "Toolformsets": Toolformsets, "SkillFormSets": SkillFormSets, "form_sys_info": form_sys_info, 'form_id_Per': "", 'error_title': error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                form = jobDescriptionForm(form.data)
                job_formsets = get_formsets(
                    form_sys_info[0], form_sys_info[2], data=form.data, form_number=20)
                formsets = get_formsets(
                    '人員增補申請表', 'A', data=form.data, form_number=5)

                Toolformsets = get_formsets(
                    'TOOL', "A", data=form.data, form_number=10)
                SkillFormSets = get_formsets(
                    'SKILL', "A", data=form.data, form_number=10)
                return render(request, "HumanResource/jobDescription.html", {'form': form, 'formsets': formsets, "job_formsets": job_formsets, "Toolformsets": Toolformsets, "SkillFormSets": SkillFormSets, 'form_id_Per': form_id_Per, "form_sys_info": form_sys_info, 'Reset': Reset, 'parents_form_id': parents_form_id, "OnlyChangeData": OnlyChangeData})


def get_level_ajax(request, form_id_Per=None):
    """用來動態回傳用戶所選擇的值

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """

    first_level = request.GET.get('first_level')
    second_level = request.GET.get('second_level')

    if first_level and not second_level:
        filter_data = Appsettings.GOOD_AT_TOOL[first_level]
        second_filter_symbol = ['--']
        for i in list(filter_data.keys()):
            second_filter_symbol.extend(list(filter_data.keys()))

        return JsonResponse({'second_level': {'' if key == '--' else key: key for key in second_filter_symbol}})

    if first_level and second_level:
        third_filter_symbol = ['--']
        third_filter_symbol.extend(
            Appsettings.GOOD_AT_TOOL[first_level][second_level])

        return JsonResponse({'third_level': {'' if key == '--' else key: key for key in third_filter_symbol}})

    symbol = ['--']
    symbol.extend(list(Appsettings.GOOD_AT_TOOL.keys()))  # type: ignore

    return JsonResponse({'first_level': {'' if key == '--' else key: key for key in symbol}})


def get_skill_level_ajax(request, form_id_Per=None):
    first_level = request.GET.get('first_level')
    second_level = request.GET.get('second_level')

    if first_level and not second_level:
        filter_data = Appsettings.WORK_SKLL[first_level]
        second_filter_symbol = ['--']
        for i in list(filter_data.keys()):
            second_filter_symbol.extend(list(filter_data.keys()))

        return JsonResponse({'second_level': {'' if key == '--' else key: key for key in second_filter_symbol}})

    if first_level and second_level:
        third_filter_symbol = ['--']
        third_filter_symbol.extend(
            Appsettings.WORK_SKLL[first_level][second_level])
        return JsonResponse({'third_level': {'' if key == '--' else key: key for key in third_filter_symbol}})

    symbol = ['--']
    symbol.extend(list(Appsettings.WORK_SKLL.keys()))  # type: ignore

    return JsonResponse({'first_level': {'' if key == '--' else key: key for key in symbol}})


def download_pdf(request, pdf_filename):
    # 确定PDF文件的路径
    pdf_path = os.path.join(BASE_DIR, 'PDF_folder', pdf_filename)

    if os.path.exists(pdf_path):
        # 创建FileResponse对象，传递文件路径而不是文件对象
        response = FileResponse(open(pdf_path, 'rb'),
                                content_type='application/pdf')

        # 设置响应的头部信息，提示浏览器以附件形式处理
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

        # 返回响应对象
        return response
    else:
        # 如果文件不存在，返回404响应
        return HttpResponseNotFound("File not found.")


class AccessControlPermission(LoginRequiredMixin, View):
    def get(self, request):
        form = AccessControlPermissionForm()
        form_sys_info = Appsettings.FormCodes['門禁權限申請單']

        context = {'form': form,
                   "form_sys_info": form_sys_info,
                   'form_id_Per': ""
                   }

        return render(request, "HumanResource/AccessControlPermission.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=None):
        form_sys_info = Appsettings.FormCodes['門禁權限申請單']
        check_form = AccessControlPermissionForm(request.POST)

        if form_id_Per is None:
            if check_form.is_valid():
                is_valid_and_to_send_process(request, form_id_Per)
                return redirect("index")
            else:
                error_title = f'資料驗證失敗請重新檢查資料,錯誤訊息如下:{check_form.errors}'
                # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                context = {'form': check_form,
                           "form_sys_info": form_sys_info,
                           'form_id_Per': "",
                           'error_title': error_title}

                print(error_title)
                return render(request, 'HumanResource/AccessControlPermission.html', context)
        else:
            if finish:
                if check_form.is_valid():
                    is_valid_and_to_send_process(request, form_id_Per)
                    return redirect("index")
                else:
                    job_formsets = get_formsets(
                        form_sys_info[0], form_sys_info[2], data=check_form.data, form_number=20)

                    formsets = get_formsets(
                        '人員增補申請表', 'A', data=check_form.data, form_number=5)

                    Toolformsets = get_formsets(
                        'TOOL', "A", data=check_form.data, form_number=10)

                    SkillFormSets = get_formsets(
                        'SKILL', "A", data=check_form.data, form_number=10)
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                    return render(request, 'HumanResource/AccessControlPermission.html', {'form': check_form, 'formsets': formsets, "job_formsets": job_formsets, "Toolformsets": Toolformsets, "SkillFormSets": SkillFormSets, "form_sys_info": form_sys_info, 'form_id_Per': "", 'error_title': error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                form = AccessControlPermissionForm(form.data)
                job_formsets = get_formsets(
                    form_sys_info[0], form_sys_info[2], data=form.data, form_number=20)
                formsets = get_formsets(
                    '人員增補申請表', 'A', data=form.data, form_number=5)

                Toolformsets = get_formsets(
                    'TOOL', "A", data=form.data, form_number=10)
                SkillFormSets = get_formsets(
                    'SKILL', "A", data=form.data, form_number=10)
                return render(request, "HumanResource/AccessControlPermission.html", {'form': form, 'formsets': formsets, "job_formsets": job_formsets, "Toolformsets": Toolformsets, "SkillFormSets": SkillFormSets, 'form_id_Per': form_id_Per, "form_sys_info": form_sys_info, 'Reset': Reset, 'parents_form_id': parents_form_id})


class jobDescriptionFormsummary(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['人資課']

    def _filter(self, job_title, filter_forms: list):
        if job_title:
            return [_form for _form in filter_forms if job_title in _form.data.get("job_title_select")]
        else:
            return filter_forms

    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='職務說明書').exclude(result='').exclude(result='取回')

        context = {
            "form_name": '職務說明書',
            'filter_forms': filter_forms,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms},
            "JOB_TITLE_CHOICES": list(set([''] + [_form.data.get('job_title_select') for _form in filter_forms]))
        }

        return render(request, "HumanResource/jobDescriptionFormsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        status = data.get('status')
        form_number = data.get('form_number')
        job_title = data.get('job_title')

        queryset = Form.objects.filter(form_name='職務說明書').exclude(
            result='').exclude(result='取回')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, '職務說明書', status, form_number, queryset=queryset, check_if_result=True)

        filter_forms = self._filter(job_title, filter_forms)

        context = {
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'status': status if status else '',
            'form_number': form_number if form_number else '',
            "filter_forms": filter_forms,
            "form_name": '職務說明書',
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms},
            "JOB_TITLE_CHOICES": list(set([''] + [_form.data.get('job_title_select') for _form in Form.objects.filter(form_name='職務說明書')]))
        }

        return render(request, "HumanResource/jobDescriptionFormsummary.html", context)


class PersonnelAdditionApplicationFormsummary(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['人資課']

    def _filter(self, add_job_title, filter_forms: list):
        if add_job_title:
            return [_form for _form in filter_forms if add_job_title in _form.data.get("add_job_title")]
        else:
            return filter_forms

    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='人員增補申請表').exclude(result='').exclude(result='取回')

        context = {
            "form_name": '人員增補申請表',
            'filter_forms': filter_forms,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms},
            "ADD_JOB_TITLE_CHOICES": list(set([''] + [_form.data.get('add_job_title') for _form in filter_forms]))
        }

        return render(request, "HumanResource/PersonnelAdditionApplicationFormsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        status = data.get('status')
        form_number = data.get('form_number')

        add_job_title = data.get('add_job_title')

        queryset = Form.objects.filter(form_name='人員增補申請表').exclude(
            result='').exclude(result='取回')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, '人員增補申請表', status, form_number, queryset=queryset, check_if_result=True)

        filter_forms = self._filter(add_job_title, filter_forms)

        context = {
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'status': status if status else '',
            'form_number': form_number if form_number else '',
            "filter_forms": filter_forms,
            "form_name": '人員增補申請表',
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms},
            "ADD_JOB_TITLE_CHOICES": list(set([''] + [_form.data.get('add_job_title') for _form in Form.objects.filter(form_name='人員增補申請表')]))
        }

        return render(request, "HumanResource/PersonnelAdditionApplicationFormsummary.html", context)
