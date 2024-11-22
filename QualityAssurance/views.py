from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from workFlow.Custom import GroupRequiredMixin
from django.views.generic import View
from .forms import QualityAbnormalityReportForm, HeavyworkorderForm
from workFlow import Appsettings
from workFlow.DataTransformer import querydict_to_dict, GetFormID, GetWorkid, get_formsets, GetFormApplicationDate
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file, filter_forms_condition, is_valid_and_to_send_process
from django.shortcuts import render, redirect
from Company.models import CustomUser, Form, Employee, Process, Process_history
from QualityAssurance.models import AbnormalFactna, AbnormalMK
from QualityAssurance.DataTransformer import create_abnormalfactna, count_diff_map, getMK_Data
from typing import Optional
import re
from workFlow.Appsettings import FORMURLS_ONLYCHANGEDATA
import time
from django.core.cache import cache
from Database import SQL_operate
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from workFlow.Debug_tool import Check_input_output
# Create your views here.
from Database import SQL_operate

import datetime
from datetime import timedelta
class QualityAbnormalityReportFormsummary(LoginRequiredMixin, View):
    def parser_formset(self, data):
        """_summary_

        Args:
            data (_type_): _description_


            return:data = [
                {
                    "part_name_and_number": "S29000-00 黑打包机(台/手柄/花轮NO YBICO/NO MIT)",
                    "exception_category": "...",
                    "disposal_method": "...",
                    "responsible_unit": "..."
                },
                {
                    "part_name_and_number": "11-416 *(锭11-M04-16Z)六角螺纹M4*16*P0.7(B)",
                    "exception_category": "...",
                    "disposal_method": "...",
                    "responsible_unit": "..."
                },
                ...
            ]
        """
        out_dict = {}
        for key, value in data.items():
            if not value:
                continue
            match = re.search(r"disposal_method(\d+)", key)
            if match:
                target_parent = match.group(1)  # 這會輸出 "0"

                if target_parent not in out_dict:
                    out_dict[target_parent] = {}

                if 'part_name_and_number' in key:
                    out_dict[target_parent]['part_name_and_number'] = value
                if 'exception_category' in key:
                    out_dict[target_parent]['exception_category'] = value
                if 'disposal_way' in key:
                    out_dict[target_parent]['disposal_way'] = value
                if 'responsible_unit' in key:
                    out_dict[target_parent]['responsible_unit'] = value

        return [i for i in list(out_dict.values()) if i]

    def _filter_forms_condition(self, filter_forms: list,
                                part_name_and_number: Optional[str] = '',
                                exception_category: Optional[str] = '',
                                disposal_way: Optional[str] = '',
                                responsible_unit: Optional[str] = ''
                                ):

        def match_condition(data, key, value, contains=False):
            if contains:
                return value in data.get(key, '')
            return data.get(key, '') == value

        out_list = []

        conditions = {
            'part_name_and_number': (part_name_and_number, True),
            'exception_category': (exception_category, False),
            'disposal_way': (disposal_way, False),
            'responsible_unit': (responsible_unit, True),
        }

        for check_data, form_object in filter_forms:
            for key, (value, contains) in conditions.items():
                if value:
                    for each_data in check_data:
                        if match_condition(each_data, key, value, contains):
                            out_list.append(form_object)
                            break
                    break
        # 代表沒有過濾掉任何東西
        if out_list:
            return out_list
        else:
            return [form_object for check_data, form_object in filter_forms]

    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='品質異常單').exclude(result='')

        context = {
            "form_name": '品質異常單',
            "filter_forms": filter_forms,
            "method_datas": [(each_form.form_id, self.parser_formset(each_form.data)) for each_form in filter_forms],
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "QualityAssurance/QualityAbnormalityReportFormsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        form_number = data.get('form_number')

        status = data.get('status')
        part_name_and_number = data.get('part_name_and_number')  # 料號品名
        exception_category = data.get('exception_category')  # 異常類別
        disposal_method = data.get('disposal_method')  # 處置方式
        responsible_unit = data.get('responsible_unit')  # 責任單位
        QAR_form_number = data.get('QAR_form_number')  # 品質異常單單號

        if QAR_form_number:
            queryset = Form.objects.filter(
                form_name='品質異常單', form_id__icontains=QAR_form_number)
        else:
            queryset = Form.objects.filter(
                form_name='品質異常單').exclude(result='')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, queryset=queryset, check_if_result=True)

        filter_symbols = list(zip([self.parser_formset(
            each_form.data) for each_form in filter_forms], filter_forms))

        # 個別過濾
        filter_forms = self._filter_forms_condition(
            filter_symbols, part_name_and_number, exception_category, disposal_method, responsible_unit)

        context = {
            "form_name": '品質異常單',
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            'form_number': form_number if form_number else '',
            'part_name_and_number': part_name_and_number if part_name_and_number else '',
            'exception_category': exception_category if exception_category else '',
            'disposal_method': disposal_method if disposal_method else '',
            'responsible_unit': responsible_unit if responsible_unit else '',
            'QAR_form_number': QAR_form_number if QAR_form_number else '',
            "filter_forms": filter_forms,
            "method_datas": [(each_form.form_id, self.parser_formset(each_form.data)) for each_form in filter_forms],
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "QualityAssurance/QualityAbnormalityReportFormsummary.html", context)


class QualityAbnormalityReport(LoginRequiredMixin, View):
    def is_form_empty(self, form):
        # 检查form中的所有字段是否都是空的
        return all(not bool(field.value()) for field in form)

    def get(self, request):
        begin_time = time.time()
        form = QualityAbnormalityReportForm()
        form_sys_info = Appsettings.FormCodes['品質異常單']

        formsets = get_formsets(
            form_sys_info[0], form_sys_info[2], data=None, form_number=12)

        context = {'form': form,
                   "form_sys_info": form_sys_info,
                   'form_id_Per': "",
                   "formsets": formsets
                   }

        return render(request, "QualityAssurance/QualityAbnormalityReport.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=False, OnlyChangeData=False, complaint_reason=None, parents_form_id=None):
        form_sys_info = Appsettings.FormCodes['品質異常單']
        check_form = QualityAbnormalityReportForm(request.POST)

        # 如果特殊狀況就不需要進入一般判斷
        if complaint_reason:
            applicant = request.user.username
            form_id = GetFormID("QAR")
            form = Form()
            form.form_id = form_id
            form.form_name = "品質異常單"
            form.applicant = applicant
            form.result = '審核中'  # 替换为实际的result
            form.application_date = GetFormApplicationDate('')  # 假设申请日期为今天
            form.closing_date = ''
            form.version_number = "A"
            form.parents_form_id = ''
            form.resourcenumber = parents_form_id if parents_form_id else ''
            form.data = {
                "source_category": "\u5ba2\u6236\u5831\u6028\u53ca\u8981\u6c42",
                "Exception_description": complaint_reason,
                "resource_no": form.resourcenumber
            }
            form.save()
            check_and_save_file(form, request)
            handle_process(form, applicant)

            return redirect("index")

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
                formsets = get_formsets(
                    form_sys_info[0], form_sys_info[2], check_form.data, form_number=12)
                # 如果验证失败，将表单重新渲染并显示错误信息
                context = {'form': check_form,
                           "form_sys_info": form_sys_info,
                           'form_id_Per': "",
                           "error_title": error_title,
                           "formsets": formsets}
                return render(request, 'QualityAssurance/QualityAbnormalityReport.html', context)
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
                    formsets = get_formsets(
                        form_sys_info[0], form_sys_info[2], check_form.data, form_number=12)
                    # 如果验证失败，将表单重新渲染并显示错误信息
                    context = {'form': check_form,
                               "form_sys_info": form_sys_info,
                               'form_id_Per': form_id_Per,
                               "error_title": error_title,
                               "formsets": formsets}

                    # 如果验证失败，将表单重新渲染并显示错误信息
                    return render(request, 'QualityAssurance/QualityAbnormalityReport.html', context)
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = QualityAbnormalityReportForm(form.data)
                formsets = get_formsets(
                    form_sys_info[0], form_sys_info[2], data=form.data, form_number=12)

                empty_forms_flags = [self.is_form_empty(
                    form) for formset in formsets for form in formset]

                context = {'form': form,
                           'form_id_Per': form_id_Per,
                           "attachments": attachments,
                           "form_sys_info": form_sys_info,
                           "Reset": Reset,
                           'parents_form_id': parents_form_id,
                           "OnlyChangeData": OnlyChangeData,
                           "combin_formsets": list(zip(formsets, empty_forms_flags))
                           }
                return render(request, "QualityAssurance/QualityAbnormalityReport.html", context)


class HeavyworkorderFormsummary(LoginRequiredMixin, View):
    def special_filter(self, filter_forms, fact_re_no):
        """
            將原本所過濾出來的表單,根據加工廠商在一次過濾
        """
        out_list = []
        if fact_re_no:
            new_filter_forms = AbnormalFactna.objects.filter(
                factoryname=fact_re_no.split(' ')[1])  # 只用廠商的中文名稱過濾
            new_filter_forms_ids = [
                _form.form_id for _form in new_filter_forms]

            # 判斷加工廠商是否在前面過濾出來的表單裡面
            for each_form in filter_forms:
                if each_form.form_id in new_filter_forms_ids:
                    out_list.append(each_form)

            return out_list
        else:
            return filter_forms

    def parser_formset(self, data):
        """_summary_

        Args:
            data (_type_): _description_


            return:data = [
                {
                    "part_name_and_number": "S29000-00 黑打包机(台/手柄/花轮NO YBICO/NO MIT)",
                    "exception_category": "...",
                    "disposal_method": "...",
                    "responsible_unit": "..."
                },
                {
                    "part_name_and_number": "11-416 *(锭11-M04-16Z)六角螺纹M4*16*P0.7(B)",
                    "exception_category": "...",
                    "disposal_method": "...",
                    "responsible_unit": "..."
                },
                ...
            ]
        """
        out_dict = {}
        for key, value in data.items():
            if 'prod_no_before' in key:
                out_dict['prod_no_before'] = value
            if 'prod_no_after' in key:
                out_dict['prod_no_after'] = value
            if 'Heavy_industry_projects' in key:
                out_dict['Heavy_industry_projects'] = value
            if 'rebuild_reason' in key:
                out_dict['rebuild_reason'] = value
            if 'prod_name_after' in key:
                out_dict['prod_name_after'] = value
            if 'prod_name_before' in key:
                out_dict['prod_name_before'] = value
            if 'quantity' in key:
                out_dict['quantity'] = value
            if 'estimated_completion_date' in key:
                out_dict['estimated_completion_date'] = value

        return out_dict

    def _filter_forms_condition(self, filter_forms: list,
                                prod_no_before: Optional[str] = '',
                                prod_no_after: Optional[str] = '',
                                ):

        def match_condition(data, key, value, contains=False):
            if contains:
                return value in data.get(key, '')
            return data.get(key, '') == value

        out_list = []
        conditions = {
            'prod_no_before': (prod_no_before, True),
            'prod_no_after': (prod_no_after, True),
        }

        for check_data, form_object in filter_forms:
            for key, (value, contains) in conditions.items():
                if value:
                    if match_condition(check_data, key, value, contains):
                        out_list.append(form_object)
                        break

        #  如果真的沒東西，有可能使用者沒有查詢任何東西，所以回傳全部
        if out_list:
            return out_list
        else:
            # 代表沒有過濾掉任何東西
            return [form_object for check_data, form_object in filter_forms]

    def _filter_forms_condition2(self, filter_forms: list,
                                 start_estimated_completion_date: Optional[str] = '',
                                 end_estimated_completion_date: Optional[str] = '',
                                 ):

        out_list = []
        for check_data, form_object in filter_forms:
            # 過濾符合時間範圍的表單
            estimated_completion_date = check_data.get(
                'estimated_completion_date')

            if estimated_completion_date >= start_estimated_completion_date \
                    and estimated_completion_date <= end_estimated_completion_date:
                out_list.append(form_object)

        return out_list

    def _get_factno_na(self):
        FACT_df = SQL_operate.DB_operate(sqltype='YBIT').get_pd_data(
            'select FACT_NO,FACT_NA from FACT')
        FACT_df['FACT_NO'] = FACT_df['FACT_NO'] + ' '
        vendors = (FACT_df['FACT_NO'] + FACT_df['FACT_NA']).to_list()
        return vendors

    def _filter_mk(self, mkfilters, mk_map, filter_forms):
        """
        Args:
            mkfilters (_type_): 
                <QuerySet [<AbnormalMK: MK202403110008 - RWF2024031800001 - 01>,
                <AbnormalMK: MK202403150011 - RWF2024031500001 - 01>,]>

            用來確認真的有這個
            mk_map (list): [('RWF2024031300001', '01'), ('RWF2024031300001', '02'), ('RWF2024031300001', '03'), ('RWF2024031300001', '04')]

            filter_forms (_type_): <QuerySet [<Form: Form object (RWF2024031300001)>,
              <Form: Form object (RWF2024031300002)>, <Form: Form object (RWF2024031300003)>]

        Returns:
            _type_: _description_
        """
        # 過濾出真正有使用的mk
        allmk = []
        mk_number = []
        mk_matchs = []
        for each_mk in mkfilters:
            for checkdata in mk_map:
                if each_mk.form_id == checkdata[0] and each_mk.item == checkdata[1]:
                    allmk.append(each_mk)
                    mk_number.append(each_mk.mk_number)
                    for form in filter_forms:
                        if each_mk.form_id == form.form_id:
                            mk_matchs.append(
                                (each_mk.mk_number, each_mk.form_id + '-' + each_mk.item, form.data['quantity']))

        return allmk, mk_number, mk_matchs

    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='重工單', result='審核中').exclude(result='').exclude(result='取回')

        
        start_date_obj = datetime.date.today() - timedelta(days=7)
        end_date_obj = datetime.date.today()

        # 過濾出需要的表單即可，因為重工單需要的數量龐大
        filter_forms = filter_forms.filter(application_date__range=[
            start_date_obj, end_date_obj])

        form_ids = [form.form_id for form in filter_forms]

        abnormalfactnas = AbnormalFactna.objects.filter(form_id__in=form_ids)

        mk_map = [(abnormalfactna.form_id, abnormalfactna.item)
                  for abnormalfactna in abnormalfactnas]

        mkfilters = AbnormalMK.objects.filter(form_id__in=form_ids)

        allmk, mk_number, mk_matchs = self._filter_mk(
            mkfilters, mk_map, filter_forms)

        MKQTY_map, MKYN_map = getMK_Data(mk_number)

        # 需要中文名字
        context = {
            "form_name": '重工單',
            "filter_forms": filter_forms,
            "method_datas": [(each_form.form_id, self.parser_formset(each_form.data)) for each_form in filter_forms],
            'abnormalfactnas': abnormalfactnas,
            'allmk': allmk,
            'MKQTY_map': MKQTY_map,
            'MKYN_map': MKYN_map,
            # 計算製令尚未開單
            'diff_map': count_diff_map(MKQTY_map, mk_matchs),
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'vendors': self._get_factno_na(),
            "fullname_map": {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "QualityAssurance/HeavyworkorderFormsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)

        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        RWF_form_number = data.get('RWF_form_number')  # 品質異常單單號
        prod_no_before = data.get('prod_no_before')  # 產品編號(重工前)
        prod_no_after = data.get('prod_no_after')  # 產品編號(重工後)
        fact_re_no = data.get('fact_re_no')  # 加工廠商
        start_estimated_completion_date = data.get(
            'start_estimated_completion_date')  # 預計完工日開始
        end_estimated_completion_date = data.get(
            'end_estimated_completion_date')  # 預計完工日結束

        sort_direction = data.get('sort_direction')  # 用來排序 #產品編號(重工前)

        if RWF_form_number:            
            queryset = Form.objects.filter(
                form_name='重工單', form_id__icontains=RWF_form_number).exclude(result='取回')
        else:
            queryset = Form.objects.filter(form_name='重工單').exclude(
                result='').exclude(result='取回')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, queryset=queryset, check_if_result=True)

        filter_symbols = list(zip([self.parser_formset(
            each_form.data) for each_form in filter_forms], filter_forms))

        # 個別過濾(條件一)
        filter_forms = self._filter_forms_condition(
            filter_symbols, prod_no_before, prod_no_after)

        # 如果有選擇預計完工日的篩選條件，在進入判斷
        if start_estimated_completion_date and end_estimated_completion_date:
            filter_symbols = list(zip([self.parser_formset(
                each_form.data) for each_form in filter_forms], filter_forms))

            filter_forms = self._filter_forms_condition2(
                filter_symbols, start_estimated_completion_date, end_estimated_completion_date)

        # 特殊過濾,針對重工單加工廠商過濾 這邊已經變成list了
        filter_forms = self.special_filter(filter_forms, fact_re_no)

        if sort_direction:
            # 在 Python 中根据 'prod_no_before' 键进行排序
            filter_forms.sort(key=lambda x: x.data.get(
                'prod_no_before', ''), reverse=(sort_direction == 'DESC'))

        form_ids = [form.form_id for form in filter_forms]

        abnormalfactnas = AbnormalFactna.objects.filter(form_id__in=form_ids)
        mk_map = [(abnormalfactna.form_id, abnormalfactna.item)
                  for abnormalfactna in abnormalfactnas]
        mkfilters = AbnormalMK.objects.filter(form_id__in=form_ids)

        allmk, mk_number, mk_matchs = self._filter_mk(
            mkfilters, mk_map, filter_forms)

        MKQTY_map, MKYN_map = getMK_Data(mk_number)

        context = {
            "form_name": '重工單',
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'start_estimated_completion_date': start_estimated_completion_date if start_estimated_completion_date else '',
            'end_estimated_completion_date': end_estimated_completion_date if end_estimated_completion_date else '',
            'applicant': applicant if applicant else '',
            'status': status if status else '',
            'form_number': form_number if form_number else '',
            "filter_forms": filter_forms,
            'RWF_form_number': RWF_form_number if RWF_form_number else '',
            'prod_no_before': prod_no_before if prod_no_before else '',
            'prod_no_after': prod_no_after if prod_no_after else '',
            'fact_re_no': fact_re_no if fact_re_no else '',
            "sort_direction": sort_direction if sort_direction else '',
            "method_datas": [(each_form.form_id, self.parser_formset(each_form.data)) for each_form in filter_forms],
            'abnormalfactnas': abnormalfactnas,
            'allmk': allmk,
            'MKQTY_map': MKQTY_map,
            'MKYN_map': MKYN_map,
            # 計算製令尚未開單
            'diff_map': count_diff_map(MKQTY_map, mk_matchs),
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'vendors': self._get_factno_na(),
            "fullname_map": {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }
        return render(request, "QualityAssurance/HeavyworkorderFormsummary.html", context)


class Heavyworkorder(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['研發部', '品保課', '品檢組', '生管課長']
    def get(self, request):
        form = HeavyworkorderForm()
        form_sys_info = Appsettings.FormCodes['重工單']
        form_CN_name = form_sys_info[0]
        form_version = form_sys_info[2]

        formsets = get_formsets(
            form_CN_name, form_version, data=None, form_number=10)

        context = {'form': form,
                   "form_sys_info": form_sys_info,
                   "formsets": formsets,
                   'form_id_Per': "",
                   "show_area": False}
        
        return render(request, "QualityAssurance/Heavyworkorder.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=None, OnlyChangeData=False):
        # 如果已經完整了表單的話，系統資訊要跟者表單走(版本控制)
        if form_id_Per is None:
            form_sys_info = Appsettings.FormCodes['重工單']
        else:
            _form = Form.objects.get(form_id=form_id_Per)
            form_sys_info = [_form.form_name,
                             form_id_Per[:3], _form.version_number]

        form_CN_name = form_sys_info[0]
        form_version = form_sys_info[2]
        
        check_form = HeavyworkorderForm(request.POST)

        # 因為前端頁面已經更新為動態加載，為了讓驗證的時候通過，需要讓表單驗證的知道所有的資料訊息
        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")
        PROD_df = ERP_sql.get_pd_data("select PROD_NO,PROD_NAME from PROD")

        _product = [
            ('', '--')] + [(prod_no, f'{prod_no}--{prod_name}') for prod_no, prod_name in PROD_df.values]
        # 处理数据并设置表单的选项
        check_form.fields['prod_no_before'].choices = _product
        check_form.fields['prod_no_after'].choices = _product

        IVIO_df = ERP_sql.get_pd_data(f"SELECT IVIO_NO FROM IVIO")
        check_form.fields['io_number'].choices = [
            (i, i) for i in IVIO_df['IVIO_NO'].to_list()]


        if form_id_Per is None:
            if check_form.is_valid():
                form_id = is_valid_and_to_send_process(request, form_id_Per)
                post_data = querydict_to_dict(request.POST)
                create_abnormalfactna(post_data, form_id)
                # 品檢組的填寫完之後想要送到這裡
                return redirect("form_application")
            else:
                formsets = get_formsets(
                    form_CN_name, form_version, data=check_form.data, form_number=10)

                error_title = f'資料驗證失敗請重新檢查資料,錯誤訊息如下:{check_form.errors}'

                context = {'form': check_form,
                           'formsets': formsets,
                           "form_sys_info": form_sys_info,
                           'form_id_Per': "",
                           'error_title': error_title}
                # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                return render(request, 'QualityAssurance/Heavyworkorder.html', context)
        else:
            if finish:                
                if check_form.is_valid():
                    is_valid_and_to_send_process(request, form_id_Per)
                    post_data = querydict_to_dict(request.POST)
                    create_abnormalfactna(post_data, form_id_Per)
                    # 品檢組的填寫完之後想要送到這裡
                    return redirect("form_application")
                else:
                    formsets = get_formsets(
                        form_CN_name, form_version, data=check_form.data, form_number=10)

                    error_title = '資料驗證失敗請重新檢查資料'

                    context = {'form': check_form,
                               'formsets': formsets,
                               "form_sys_info": form_sys_info,
                               'form_id_Per': "",
                               'error_title': error_title}

                    # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                    return render(request, 'QualityAssurance/Heavyworkorder.html', context)
            else:                
                # 這邊可以將上一次所保存的資料取出來
                _form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = _form.parents_form_id
                form = HeavyworkorderForm(_form.data)

                # 因為如果不知道資料數量的話 會造成編輯功能失效
                ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")
                PROD_df = ERP_sql.get_pd_data(
                    "select PROD_NO,PROD_NAME from PROD")

                # 处理数据并设置表单的选项
                if _form.data['prod_no_before']:
                    form.fields['prod_no_before'].choices = [
                        (prod_no, f'{prod_no}--{prod_name}') for prod_no, prod_name in PROD_df.values if prod_no == _form.data['prod_no_before']]

                if _form.data['prod_no_after']:
                    form.fields['prod_no_after'].choices = [(prod_no, f'{prod_no}--{prod_name}') for prod_no, prod_name in PROD_df.values if prod_no == _form.data['prod_no_after']]

                if _form.data['io_number']:
                    IVIO_df = ERP_sql.get_pd_data(f"SELECT IVIO_NO FROM IVIO")
                    form.fields['io_number'].choices = [
                        (i, i) for i in IVIO_df['IVIO_NO'].to_list()]
                

                formsets = get_formsets(
                    form_CN_name, form_version, data=form.data, form_number=10)

                context = {'form': form,
                           'formsets': formsets,
                           'form_id_Per': form_id_Per,
                           "form_sys_info": form_sys_info,
                           'Reset': Reset,
                           'parents_form_id': parents_form_id,
                           "OnlyChangeData": OnlyChangeData,
                           "show_area": False}
                return render(request, "QualityAssurance/Heavyworkorder.html", context)


class HeayworkorderPrint(LoginRequiredMixin, View):
    def _get_factname(self, fact_no):
        """用來組合工廠名稱給重工單列印

        Args:
            fact_no (_type_): _description_

        Returns:
            _type_: _description_
        """
        sql = SQL_operate.DB_operate(sqltype='YBIT')
        FACT_df = sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
        for each_fact_no, each_fact_na in FACT_df.values:
            if fact_no == each_fact_no:
                return each_fact_na

        return ''

    def post(self, request, form_id=None):

        assert isinstance(form_id, str), 'form_id must be str type'
        form = Form.objects.get(form_id=form_id)
        factnamestr = ''
        for key, value in form.data.items():
            if 'factmk_name' in key and 'Factname' in key and value:
                if factnamestr:
                    factnamestr = factnamestr + '/' + self._get_factname(value)
                else:
                    factnamestr += self._get_factname(value)

        checkasignname = False

        Process_historys = Process_history.objects.filter(
            process_id=Process.objects.get(form_id=form_id).process_id)

        for eachhistory in Process_historys:
            if '核准' in eachhistory.approval_status:
                checkasignname = True

        # 要將某些地方轉換成中文            
        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")
        FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
        
        if form.data.get('paying_unit'):
            form.data['paying_unit'] = FACT_df[FACT_df['FACT_NO'] == form.data.get('paying_unit')]['FACT_NA'].iloc[0]
        
        if form.data.get('responsible_unit'):    
            form.data['responsible_unit'] = FACT_df[FACT_df['FACT_NO'] == form.data.get('responsible_unit')]['FACT_NA'].iloc[0]
        
        
        
        context = {'form': form,
                   'factnamestr': factnamestr,
                   'checkasignname': checkasignname,
                   'applicantname': CustomUser.objects.get(username=form.applicant).FullName
                   }
        return render(request, "QualityAssurance/HeayworkorderPrint.html", context)


class pricemodal(LoginRequiredMixin, View):
    def post(self, request):

        data = querydict_to_dict(request.POST)

        # 比較取得MK
        abnormalmks = AbnormalMK.objects.filter(
            form_id=data['form_id'], item=data['item'])

        if len(abnormalmks) == 0:
            return JsonResponse({'error': '請注意填寫單價之前請先填入MK在補單價'}, status=404)

        # 取得生產數量
        form = Form.objects.get(form_id=data['form_id'])

        ERPsql = SQL_operate.DB_operate(sqltype='YBIT')
        # 只需要一個就好
        result = ERPsql.get_db_data(
            f"select RBOM_BQTY from MAKEP where MAKE_NO= '{abnormalmks[0].mk_number}' ")
        abnormalfactna = AbnormalFactna.objects.get(
            form_id=data['form_id'], item=data['item'])
        abnormalfactna.unit_price = data['price']
        abnormalfactna.total_price = int(
            float(form.data['quantity']) / float(result[0][0]) * float(data['price']))
        abnormalfactna.save()
        # {'form_id': 'RWF2023111500005', 'item': '01', 'csrfmiddlewaretoken': 'kaJvsBQ1ZulAdPMllgUYJTqza1CCyRLsVarDOLTVPOLGlaBqDguMbkkE0LUCnBiL'}
        return HttpResponse(status=200)  # 只返回状态码 200


class mknumberModal(LoginRequiredMixin, View):
    def post(self, request):
        data = querydict_to_dict(request.POST)
        abnormalmk = AbnormalMK()
        abnormalmk.mk_number = data['mknumber']
        abnormalmk.form_id = data['form_id']
        abnormalmk.item = data['item']
        abnormalmk.remarks = data['remarks']
        abnormalmk.save()

        # 要將資料準備好回傳前台
        form = Form.objects.get(form_id=data['form_id'])
        abnormalmks = AbnormalMK.objects.filter(form_id=data['form_id'])
        abnormalfactnas = AbnormalFactna.objects.filter(
            form_id=data['form_id'])

        # 過濾出真正有使用的mk
        mk_matchs = []
        for each_mk in abnormalmks:
            mk_matchs.append((each_mk.mk_number, each_mk.form_id +
                             '-' + each_mk.item, form.data['quantity']))

        mk_number = [abnormalmk.mk_number for abnormalmk in abnormalmks]

        MKQTY_map, MKYN_map = getMK_Data(mk_number)
        # 需要中文名字
        context = {
            "form": form,
            "form_name": '重工單',
            "abnormalfactnas": abnormalfactnas,
            'abnormalmks': abnormalmks,
            'MKQTY_map': MKQTY_map,
            'MKYN_map': MKYN_map,
            'diff_map': count_diff_map(MKQTY_map, mk_matchs),
        }

        # 渲染HTML模板
        html = render_to_string(
            "QualityAssurance/mk_template.html", context, request=request)

        return HttpResponse(html)


class delAbnormalMK(LoginRequiredMixin, View):
    def post(self, request):
        data = querydict_to_dict(request.POST)
        obejct = AbnormalMK.objects.get(id=data['id'])
        obejct.delete()
        return redirect('HeavyworkorderFormsummary')


def get_prod_choices_ajax(request):
    # 定义一个函数来获取（或设置）缓存的数据
    def get_prod_choices():
        # 尝试从缓存中获取数据
        PROD_CHOICES = cache.get('Heavywork_PROD_CHOICES')

        # 如果缓存中没有数据，那么查询数据库并设置缓存
        if PROD_CHOICES is None:
            sql = SQL_operate.DB_operate(sqltype="YBIT")
            PROD_df = sql.get_pd_data("select PROD_NO,PROD_NAME from PROD")
            PROD_CHOICES = [(prod_no, f'{prod_no}--{prod_name}')
                            for prod_no, prod_name in PROD_df.values]

            # 将数据存储在缓存中，这里设置为600秒（10分钟）的过期时间。
            # 您可以根据需要调整此过期时间。
            cache.set('Heavywork_PROD_CHOICES', PROD_CHOICES, 600)

        return PROD_CHOICES
    query = request.GET.get('q', '')

    if query:
        filtered_choices = [i for i in get_prod_choices() if query in i[0]]
        # 將元組列表轉換為Select2期望的格式
        select2_data = [{"id": i[0], "text": i[1]} for i in filtered_choices]
    else:
        select2_data = []

    return JsonResponse({'results': select2_data})


def get_io_number(request):
    query = request.GET.get('q', '')
    if query:
        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")
        IVIO_df = ERP_sql.get_pd_data(
            f"SELECT TOP 1000 IVIO_NO FROM IVIO WHERE IVIO_NO LIKE '%{query}%'")
        
        
        # 將元組列表轉換為Select2期望的格式
        select2_data = [{"id": i, "text": i}
                        for i in IVIO_df['IVIO_NO'].to_list()]
    else:
        select2_data = []

    return JsonResponse({'results': select2_data})
