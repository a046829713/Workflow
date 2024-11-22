from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from workFlow.Custom import GroupRequiredMixin
from django.views.generic import View
from .forms import MeetingMinutesForm, SampleConfirmationForm, ExperimentalTestForm, PartApprovalNotificationForm
from workFlow import Appsettings
from workFlow.DataTransformer import querydict_to_dict, GetFormID, parser_object_error
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file, filter_forms_condition
from django.shortcuts import render, redirect
from Company.models import Form, CustomUser
from typing import Optional
from workFlow.Appsettings import FORMURLS_ONLYCHANGEDATA
import time
from django.contrib.auth.models import Group
import copy
import random



class MeetingMinutesFormsummary(LoginRequiredMixin, GroupRequiredMixin, View):
    def _filter_forms_condition(self, filter_forms: list, conferenceName: Optional[str] = '', newProductName: Optional[str] = ''):

        if conferenceName:
            filter_forms = [
                each_form for each_form in filter_forms if each_form.data['conferenceName'] == conferenceName]
        if newProductName:
            filter_forms = [
                each_form for each_form in filter_forms if each_form.data['newProductName'] == newProductName]

        return filter_forms

    group_required = ['研發部']

    def get(self, request):
        filter_forms = Form.objects.filter(form_name='會議記錄').exclude(result='').exclude(result='取回')

        context = {
            "form_name": '會議記錄',
            "filter_forms": filter_forms,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "R_D_Department/MeetingMinutesFormsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        status = data.get('status')
        form_number = data.get('form_number')
        conferenceName = data.get('conferenceName')
        newProductName = data.get('newProductName')

        queryset = Form.objects.filter(form_name='會議記錄')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, '會議記錄', status, form_number, queryset=queryset, check_if_result=True)

        # 個別過濾
        filter_forms = self._filter_forms_condition(
            filter_forms, conferenceName, newProductName)

        context = {
            "form_name": '會議記錄',
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',            
            'status': status if status else '',
            'conferenceName': conferenceName if conferenceName else '',
            'newProductName': newProductName if newProductName else '',
            "filter_forms": filter_forms,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "R_D_Department/MeetingMinutesFormsummary.html", context)


class MeetingMinutes(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['研發部']

    def get(self, request):
        form = MeetingMinutesForm()
        form_sys_info = Appsettings.FormCodes['會議記錄']
        return render(request, "R_D_Department/MeetingMinutes.html", {'form': form, "form_sys_info": form_sys_info, 'form_id_Per': ""})

    def post(self, request, form_id_Per=None, finish=None, Reset=False):
        form_sys_info = Appsettings.FormCodes['會議記錄']
        check_form = MeetingMinutesForm(request.POST)

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

                # MeetingMinutes 會有特殊的加簽與會人員

                handle_process(form, applicant, list(map(lambda x: x.split()[0], post_data['attendees'] if isinstance(
                    post_data['attendees'], list) else [post_data['attendees']])))

                return redirect("index")
            else:
                error_title = '資料驗證失敗請重新檢查資料'
                # 如果验证失败，将表单重新渲染并显示错误信息
                return render(request, 'R_D_Department/MeetingMinutes.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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
                    print(post_data['attendees'])
                    handle_process(form, applicant,  list(map(lambda x: x.split()[0], post_data['attendees'] if isinstance(
                        post_data['attendees'], list) else [post_data['attendees']])))
                    return redirect("index")
                else:
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果验证失败，将表单重新渲染并显示错误信息
                    return render(request, 'R_D_Department/MeetingMinutes.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = MeetingMinutesForm(form.data)
                return render(request, "R_D_Department/MeetingMinutes.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id})


class SampleConfirmation(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['研發部']

    def get(self, request):
        form = SampleConfirmationForm()
        form_sys_info = Appsettings.FormCodes['樣品確認單']

        context = {'form': form,
                   "form_sys_info": form_sys_info, 'form_id_Per': ""}
        return render(request, "R_D_Department/SampleConfirmation.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=False):
        form_sys_info = Appsettings.FormCodes['樣品確認單']
        check_form = SampleConfirmationForm(request.POST)

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
                return render(request, 'R_D_Department/SampleConfirmation.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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
                    return render(request, 'R_D_Department/SampleConfirmation.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = SampleConfirmationForm(form.data)
                return render(request, "R_D_Department/SampleConfirmation.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id})


class SampleConfirmationFormsummary(LoginRequiredMixin, GroupRequiredMixin, View):
    def _filter_forms_condition(self, filter_forms: list, marchine_model: Optional[str] = '', version: Optional[str] = ''):

        if marchine_model:
            filter_forms = [
                each_form for each_form in filter_forms if marchine_model in each_form.data['marchine_model']]
        if version:
            filter_forms = [
                each_form for each_form in filter_forms if version in each_form.data['version']]

        return filter_forms

    group_required = ['研發部']

    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='樣品確認單').exclude(result='')

        context = {
            "form_name": '樣品確認單',
            "filter_forms": filter_forms,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "R_D_Department/SampleConfirmationFormsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        status = data.get('status')
        form_number = data.get('form_number')

        marchine_model = data.get('marchine_model')
        version = data.get('version')

        queryset = Form.objects.filter(form_name='樣品確認單')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, queryset=queryset, check_if_result=True)

        # 個別過濾
        filter_forms = self._filter_forms_condition(
            filter_forms, marchine_model, version)

        context = {
            "form_name": '樣品確認單',
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            'marchine_model': marchine_model if marchine_model else '',
            'version': version if version else '',
            "filter_forms": filter_forms,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "R_D_Department/SampleConfirmationFormsummary.html", context)


class ExperimentalTest(LoginRequiredMixin, View):
    def _get_compet_coprorations(self, filter_forms) -> list:
        """
            用來回傳競品公司名稱，讓未來的人有機會可以重複選擇

        Args:
            filter_forms (_type_): _description_

        Returns:
            list: _description_
        """
        coprorations = [each_from.data.get(
            'Compet_corporation') for each_from in filter_forms if each_from.data.get('Compet_corporation')]

        newcoprorations = []
        for _each in coprorations:
            if isinstance(_each, str):
                newcoprorations.append(_each)

            if isinstance(_each, list):
                newcoprorations.extend(_each)

        CORPORATION_CHOICES = [(_, _) for _ in list(set(newcoprorations))]
        return CORPORATION_CHOICES

    def _get_alltags(self, filter_forms) -> list:
        """ 返回所有標籤可能 """
        all_tags = [each_from.data.get(
            'tags') for each_from in filter_forms if each_from.data.get('tags')]

        newtags = []
        for _eachtag in all_tags:
            if isinstance(_eachtag, str):
                newtags.append(_eachtag)

            if isinstance(_eachtag, list):
                newtags.extend(_eachtag)

        TAGS_CHOICES = [(tag, tag) for tag in list(set(newtags))]  
        return TAGS_CHOICES

    def get(self, request):
        form_sys_info = Appsettings.FormCodes['實驗測試申請單']
        attachment_map = {f'attachment{i}': f'附件{i}'for i in range(1, 11)}  # 创建一个范围列表

        filter_forms = Form.objects.filter(form_name='實驗測試申請單')        
        TAGS_CHOICES = self._get_alltags(filter_forms)
        CORPORATION_CHOICES = self._get_compet_coprorations(filter_forms)

        form = ExperimentalTestForm(
            tags_choices=TAGS_CHOICES, coprorataion_choices=CORPORATION_CHOICES)  # 传递 TAGS_CHOICES

        context = {
            'form': form,
            "form_sys_info": form_sys_info,
            'form_id_Per': "",
            'attachment_map': attachment_map,
            # 預計完成日期在申請時不需要給使用者看到
            'if_hide': True
        }

        return render(request, "R_D_Department/ExperimentalTest.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=False, OnlyChangeData=False):
        form_sys_info = Appsettings.FormCodes['實驗測試申請單']
        check_form = ExperimentalTestForm(request.POST)

        # 如果是草稿的不會近來這裡
        if check_form.data.getlist('tags'):
            TAGS_CHOICES = [(tag, tag) for tag in check_form.data.getlist('tags')]  # 根据 all_tags 准备 TAGS_CHOICES
            CORPORATION_CHOICES = [(tag, tag) for tag in check_form.data.getlist('Compet_corporation')]  # 根据 Compet_corporation 准备 CORPORATION_CHOICES
            check_form.fields['tags'].choices = TAGS_CHOICES
            check_form.fields['Compet_corporation'].choices = CORPORATION_CHOICES

        # 第一次直接提交表單簽核
        if form_id_Per is None:
            if check_form.is_valid():
                # 获取表单数据
                post_data = querydict_to_dict(request.POST)
                # 變數紀錄
                applicant = post_data.pop('applicant', '')
                form_id = GetFormID(post_data.pop('form_id', None))
                # 创建一个新的Form对象(就算資料庫裏面有也會因為再次保存而覆蓋掉)
                
                if isinstance(post_data['tags'], str):
                    post_data['tags'] = [post_data['tags']]
                    
                form = create_form_and_save(post_data, form_id, applicant)
                check_and_save_file(form, request)
                handle_process(form, applicant)
                return redirect("index")
            else:
                error_title = '資料驗證失敗請重新檢查資料'
                parser_object_error(check_form.errors)
                return render(request, 'R_D_Department/ExperimentalTest.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
        else:
            if finish:
                # 获取表单数据
                if check_form.is_valid():
                    post_data = querydict_to_dict(request.POST)
                    # 變數紀錄
                    applicant = post_data.pop('applicant', '')
                    # 创建一个新的Form对象(就算資料庫裏面有也會因為再次保存而覆蓋掉)
                    if isinstance(post_data['tags'], str):
                        post_data['tags'] = [post_data['tags']]
                    form = create_form_and_save(
                        post_data, form_id_Per, applicant)
                    check_and_save_file(form, request, check_repeat=True)
                    handle_process(form, applicant)
                    return redirect("index")
                else:
                    error_title = '資料驗證失敗請重新檢查資料'
                    parser_object_error(check_form.errors)
                    return render(request, 'R_D_Department/ExperimentalTest.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()

                filter_forms = Form.objects.filter(form_name='實驗測試申請單')
                TAGS_CHOICES = self._get_alltags(filter_forms)
                CORPORATION_CHOICES = self._get_compet_coprorations(filter_forms)

                form = ExperimentalTestForm(form.data)
                form.fields['tags'].choices = TAGS_CHOICES
                form.fields['Compet_corporation'].choices = CORPORATION_CHOICES

                attachment_map = {f'attachment{i}': f'附件{i}'for i in range(1, 11)}

                context = {'form': form,
                           'form_id_Per': form_id_Per,
                           "attachments": attachments,
                           "form_sys_info": form_sys_info,
                           "Reset": Reset,
                           'parents_form_id': parents_form_id,
                           "OnlyChangeData": OnlyChangeData,
                           'attachment_map': attachment_map
                           }
                
                # 草稿的時候
                if not OnlyChangeData:
                    context.update({"if_hide": True})

                return render(request, "R_D_Department/ExperimentalTest.html", context)

class ExperimentalTestsummary(ExperimentalTest):
    def _filter_forms_condition(self,
                                filter_forms: list,
                                test_type: Optional[str] = '',
                                prod_type: Optional[str] = '',
                                prod_number: Optional[str] = '',
                                estimated_completion_date: Optional[str] = '',
                                Compet_prod_number: Optional[str] = '',
                                keyword: Optional[str] = '',
                                ):
        if test_type:
            filter_forms = [
                each_form for each_form in filter_forms if each_form.data['test_type'] == test_type]
        if prod_type:
            filter_forms = [
                each_form for each_form in filter_forms if each_form.data['prod_type'] == prod_type]
        if prod_number:
            filter_forms = [
                each_form for each_form in filter_forms if prod_number in each_form.data['prod_number']]
        if estimated_completion_date:
            filter_forms = [
                each_form for each_form in filter_forms if estimated_completion_date in each_form.data['estimated_completion_date']]

        if Compet_prod_number:
            filter_forms = [each_form for each_form in filter_forms if each_form.data.get(
                'Compet_prod_number')]
            filter_forms = [
                each_form for each_form in filter_forms if Compet_prod_number in each_form.data['Compet_prod_number']]
        
        if keyword:
            filter_forms = [
                each_form for each_form in filter_forms
                if any(keyword in _str for _str in (each_form.data.get('tags') if isinstance(each_form.data.get('tags'), list) else [each_form.data.get('tags')]))
            ]

        return filter_forms

    def _random_color(self):
        """生成随机颜色的函数"""
        return "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
    
    def _add_Compet_prod_number(self,filter_forms):
        """
            有時候沒有競品型號，為了讓版面一致所以會回填資料
        """
        # add Compet_prod_number
        for each_form in filter_forms:
            if 'Compet_prod_number' not in each_form.data:
                each_form.data.update({'Compet_prod_number': ''})
                each_form.data = {k: each_form.data[k] for k in sorted(each_form.data)}
    
    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='實驗測試申請單').exclude(result='').exclude(result='取回')

        self._add_Compet_prod_number(filter_forms)               
               
        TAGS_CHOICES = self._get_alltags(filter_forms)
        tagged_tags_colors = {tag[0]:self._random_color() for tag in TAGS_CHOICES}
        

        context = {
            "form_name": '實驗測試申請單',
            "filter_forms": filter_forms,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'TEST_TYPE_CHOICES': [i[0] for i in ExperimentalTestForm().TEST_TYPE_CHOICES],
            'PROD_TYPE_CHOICES': [i[0] for i in ExperimentalTestForm().PROD_TYPE_CHOICES],
            "button_show": str(request.user) in [_each_user.username for _each_user in CustomUser.objects.filter(groups=Group.objects.filter(name__in=['生技課']).first())],
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms},
            "tagged_tags_colors":tagged_tags_colors
        }

        return render(request, "R_D_Department/ExperimentalTestsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        status = data.get('status')
        form_number = data.get('form_number')
        test_type = data.get('test_type')
        prod_type = data.get('prod_type')
        prod_number = data.get('prod_number')
        estimated_completion_date = data.get('estimated_completion_date')
        Compet_prod_number = data.get('Compet_prod_number')
        keyword = data.get('keyword')


        queryset = Form.objects.filter(form_name='實驗測試申請單').exclude(
            result='').exclude(result='取回')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, '實驗測試申請單', status, form_number, queryset=queryset, check_if_result=True)

        # 個別過濾
        filter_forms = self._filter_forms_condition(
            filter_forms, test_type, prod_type, prod_number, estimated_completion_date, Compet_prod_number,keyword)

        self._add_Compet_prod_number(filter_forms)
                
        TAGS_CHOICES = self._get_alltags(filter_forms)
        tagged_tags_colors = {tag[0]:self._random_color() for tag in TAGS_CHOICES}
        
        context = {
            "form_name": '實驗測試申請單',
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'status': status if status else '',
            'keyword': keyword if keyword else '',
            "filter_forms": filter_forms,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'TEST_TYPE_CHOICES': [i[0] for i in ExperimentalTestForm().TEST_TYPE_CHOICES],
            'test_type': test_type if test_type else '',
            'PROD_TYPE_CHOICES': [i[0] for i in ExperimentalTestForm().PROD_TYPE_CHOICES],
            'prod_type': prod_type if prod_type else '',
            'prod_number': prod_number if prod_number else '',
            'estimated_completion_date': estimated_completion_date if estimated_completion_date else '',
            'Compet_prod_number': Compet_prod_number if Compet_prod_number else '',
            "button_show": str(request.user) in [_each_user.username for _each_user in CustomUser.objects.filter(groups=Group.objects.filter(name__in=['生技課']).first())],
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms},
            "tagged_tags_colors":tagged_tags_colors
        }

        return render(request, "R_D_Department/ExperimentalTestsummary.html", context)


class PartApprovalNotification(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['研發部']

    def get(self, request):
        form = PartApprovalNotificationForm()
        form_sys_info = Appsettings.FormCodes['部品承認通知單']

        tasks = [
            "檢驗圖",
            "檢驗紀錄表",
            "樣品開發檢驗紀錄表",
            "進料檢驗單",
            "可靠度測試報告",
            "特性測試紀錄",
            "樣品(比對、試驗用)",
            "部品品質檢驗規範表",
            "工程圖"

        ]

        context = {'form': form,
                   "tasks": tasks,
                   "form_sys_info": form_sys_info,
                   # 创建一个范围列表
                   "attachment_range": [f'附件{i}' for i in range(1, 13)],
                   'form_id_Per': ""}

        return render(request, "R_D_Department/PartApprovalNotification.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=False):
        form_sys_info = Appsettings.FormCodes['部品承認通知單']
        check_form = PartApprovalNotificationForm(request.POST)

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
                return render(request, 'R_D_Department/PartApprovalNotification.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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
                    return render(request, 'R_D_Department/PartApprovalNotification.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = PartApprovalNotificationForm(form.data)
                return render(request, "R_D_Department/PartApprovalNotification.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id})
