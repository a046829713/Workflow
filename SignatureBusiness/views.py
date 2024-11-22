from django.shortcuts import render, redirect
from Company.models import Form
from workFlow.DataTransformer import querydict_to_dict, GetFormID
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file, filter_forms_condition
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from workFlow import Appsettings
from .forms import DrawingDependencyBookForm, CustomerComplaintRecordForm
from workFlow.Custom import GroupRequiredMixin
from workFlow.Appsettings import FORMURLS_ONLYCHANGEDATA,ATTACHMENT
from workFlow.FormAppsettings import PROD_TYPE_CHOICES
from typing import Optional
from Company.models import CustomUser
from Company.action_deal_with import Send_Email_CustomerComplaintRecord
from django.contrib.auth.models import Group
# Create your views here.


class CustomerComplaintRecord(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ["業務部","生產部經理"]

    def get(self, request):
        form = CustomerComplaintRecordForm()
        form_sys_info = Appsettings.FormCodes['客訴紀錄單']
        return render(request, "SignatureBusiness/CustomerComplaintRecord.html", {'form': form, "form_sys_info": form_sys_info, 'form_id_Per': ""})

    def post(self, request, form_id_Per=None, finish=None, Reset=False, OnlyChangeData=False):
        form_sys_info = Appsettings.FormCodes['客訴紀錄單']
        check_form = CustomerComplaintRecordForm(request.POST)

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

                # 從B版中間出現了加簽(但是因為不影響現有流程就沒有更改C版本)
                handle_process(form, applicant,[user.username for user in CustomUser.objects.filter(groups__in=[Group.objects.get(name='研發部副理')])])

                # 寄信給所有的業務
                Send_Email_CustomerComplaintRecord(form)

                return redirect("index")
            else:
                error_title = '資料驗證失敗請重新檢查資料'
                # 如果验证失败，将表单重新渲染并显示错误信息
                return render(request, 'SignatureBusiness/CustomerComplaintRecord.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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

                    # 寄信給所有的業務
                    Send_Email_CustomerComplaintRecord(form)
                    return redirect("index")
                else:
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果验证失败，将表单重新渲染并显示错误信息
                    return render(request, 'SignatureBusiness/CustomerComplaintRecord.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = CustomerComplaintRecordForm(form.data)
                return render(request, "SignatureBusiness/CustomerComplaintRecord.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id, "OnlyChangeData": OnlyChangeData})


class CustomerComplaintRecordsummary(LoginRequiredMixin, View):
    def _filter_forms_condition(self,
                                filter_forms: list,
                                customer_number: Optional[str] = '',
                                Complaint_type: Optional[str] = '',
                                prod_type: Optional[str] = '',

                                ):
        if customer_number:
            filter_forms = [
                each_form for each_form in filter_forms if customer_number in each_form.data['customer_number']]

        if Complaint_type:
            filter_forms = [
                each_form for each_form in filter_forms if Complaint_type == each_form.data['Complaint_type']]
        if prod_type:
            filter_forms = [
                each_form for each_form in filter_forms if prod_type == each_form.data['prod_type']]

        return filter_forms

    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='客訴紀錄單').exclude(result='').exclude(result='取回')

        context = {
            "form_name": '客訴紀錄單',
            'filter_forms': filter_forms,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'COMPLAINT_TYPE_CHOICES': [''] + [i[0] for i in CustomerComplaintRecordForm().COMPLAINT_TYPE_CHOICES],
            'PROD_TYPE_CHOICES': [i[0] for i in PROD_TYPE_CHOICES],
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "SignatureBusiness/CustomerComplaintRecordsummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        customer_number = data.get('customer_number')
        Complaint_type = data.get('Complaint_type')
        prod_type = data.get('prod_type')

        queryset = Form.objects.filter(form_name='客訴紀錄單').exclude(
            result='').exclude(result='取回')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, queryset=queryset, check_if_result=True)

        # 個別過濾
        filter_forms = self._filter_forms_condition(
            filter_forms, customer_number, Complaint_type, prod_type)

        context = {
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            'form_number': form_number if form_number else '',
            "filter_forms": filter_forms,
            "form_name": '客訴紀錄單',
            "customer_number": customer_number if customer_number else '',
            "Complaint_type": Complaint_type if Complaint_type else '',
            "prod_type": prod_type if prod_type else '',
            'COMPLAINT_TYPE_CHOICES': [''] + [i[0] for i in CustomerComplaintRecordForm().COMPLAINT_TYPE_CHOICES],
            'PROD_TYPE_CHOICES': [i[0] for i in PROD_TYPE_CHOICES],
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "SignatureBusiness/CustomerComplaintRecordsummary.html", context)


class DrawingDependencyBook(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['業務部']

    def get(self, request):
        form = DrawingDependencyBookForm()
        form_sys_info = Appsettings.FormCodes['出圖依賴書']
        
        

        attachment_map = {f'attachment{i}': f'附件{i}'for i in range(1, len(ATTACHMENT[form_sys_info[0]][form_sys_info[2]]) + 1 ) }  # 创建一个范围列表
        
        context = {"form": form,
                   "form_sys_info": form_sys_info,
                   "form_id_Per": "",
                   "attachment_map":attachment_map}
        
        return render(request, "SignatureBusiness/DrawingDependencyBook.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=False, OnlyChangeData=False):
        form_sys_info = Appsettings.FormCodes['出圖依賴書']
        check_form = DrawingDependencyBookForm(request.POST)

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
                return render(request, 'SignatureBusiness/DrawingDependencyBook.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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
                    return render(request, 'SignatureBusiness/DrawingDependencyBook.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = DrawingDependencyBookForm(form.data)
                
                attachment_map = {f'attachment{i}': f'附件{i}'for i in range(1, 11)}  # 创建一个范围列表
                
                context = {'form': form,
                           'form_id_Per': form_id_Per,
                           "attachments": attachments,
                           "form_sys_info": form_sys_info,
                           "Reset": Reset,
                           'parents_form_id': parents_form_id,
                           "OnlyChangeData": OnlyChangeData,
                           "attachment_map":attachment_map}                
                
                return render(request, "SignatureBusiness/DrawingDependencyBook.html", context)


class DrawingDependencyBooksummary(LoginRequiredMixin, View):
    def get(self, request):
        filter_forms = Form.objects.filter(
            form_name='出圖依賴書').exclude(result='').exclude(result='取回')

        context = {
            'filter_forms': filter_forms,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "SignatureBusiness/DrawingDependencyBooksummary.html", context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        queryset = Form.objects.filter(form_name='出圖依賴書').exclude(
            result='').exclude(result='取回')

        # 共通過濾
        filter_forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, queryset=queryset, check_if_result=True)

        context = {
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            "filter_forms": filter_forms,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, "SignatureBusiness/DrawingDependencyBooksummary.html", context)
