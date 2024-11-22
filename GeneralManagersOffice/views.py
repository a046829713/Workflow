from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from workFlow.Custom import GroupRequiredMixin
from django.views.generic import View
from .forms import CorrectiveeActionReportForm
from workFlow import Appsettings
from workFlow.DataTransformer import querydict_to_dict, GetFormID, GetWorkid
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file, GetFormApplicationDate
from django.shortcuts import render, redirect
from Company.models import Form, CustomUser

# Create your views here.
# CorrectiveeActionReport , CAR


class CorrectiveeActionReport(LoginRequiredMixin, View):
    def get(self, request):
        form = CorrectiveeActionReportForm()
        form_sys_info = Appsettings.FormCodes['矯正預防措施處理單']
        return render(request, "GeneralManagersOffice/CorrectiveeActionReport.html", {'form': form, "form_sys_info": form_sys_info, 'form_id_Per': ""})

    def post(self, request, form_id_Per=None, finish=None, Reset=False, departments=None, parents_form_id=None, OnlyChangeData=False):
        form_sys_info = Appsettings.FormCodes['矯正預防措施處理單']
        check_form = CorrectiveeActionReportForm(request.POST)

        # 如果特殊狀況就不需要進入一般判斷
        if departments:
            all_user = CustomUser.objects.all()
            # map_data = {'研發部': "3000001", '品技部': "5000026",
            #             '生產部': "1000519", '資材部': "1000470"}
            map_data = {'品技部': "品技部經理", '研發部': '研發部經理',
                        '生產部': "生產部經理", '資材部': "資材部經理"}

            for each_department in departments:
                applicant = GetWorkid(
                    [map_data[each_department]], all_user=all_user)[0]
                form_id = GetFormID("CAR")
                form = Form()
                form.form_id = form_id
                form.form_name = "矯正預防措施處理單"
                form.applicant = applicant
                form.result = '審核中'  # 替换为实际的result
                form.application_date = GetFormApplicationDate('')  # 假设申请日期为今天
                form.closing_date = ''
                form.version_number = "A"
                form.parents_form_id = ''
                form.resourcenumber = parents_form_id if parents_form_id else ''
                form.data = {"form_id_Per": "", "complaint_reason": "",
                             "temporary_plan": "", "permanent_countermeasures": "", "happen_again": ""}
                form.save()
                check_and_save_file(form, request)
                handle_process(form, applicant)

            return redirect("index")

        # 第一次直接提交表單簽核
        if form_id_Per is None:
            if check_form.is_valid():
                # 获取表单数据
                post_data = querydict_to_dict(request.POST)
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
                return render(request, 'GeneralManagersOffice/CorrectiveeActionReport.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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
                    return render(request, 'GeneralManagersOffice/CorrectiveeActionReport.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                print(attachments)
                form = CorrectiveeActionReportForm(form.data)
                return render(request, "GeneralManagersOffice/CorrectiveeActionReport.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id, "OnlyChangeData": OnlyChangeData})