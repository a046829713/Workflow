from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from workFlow.Custom import GroupRequiredMixin
from .forms import AssetDataForm
from django.views.generic import View
from workFlow import Appsettings
from workFlow.DataTransformer import querydict_to_dict, GetFormID
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file
from django.shortcuts import render, redirect
from Company.models import Form
from typing import Optional


class AssetData(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['資訊課']

    def get(self, request):
        form = AssetDataForm()
        form_sys_info = Appsettings.FormCodes['資產報廢申請單']
        return render(request, "ITInformation/AssetData.html", {'form': form, "form_sys_info": form_sys_info, 'form_id_Per': ""})

    def post(self, request, form_id_Per=None, finish=None, Reset=False):
        form_sys_info = Appsettings.FormCodes['資產報廢申請單']
        check_form = AssetDataForm(request.POST)

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
                return render(request, 'ITInformation/AssetData.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", "error_title": error_title})
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
                    handle_process(form, applicant)
                    return redirect("index")
                else:
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果验证失败，将表单重新渲染并显示错误信息
                    return render(request, 'ITInformation/AssetData.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': form_id_Per, "error_title": error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                attachments = form.attachments.all()
                form = AssetDataForm(form.data)
                return render(request, "ITInformation/AssetData.html", {'form': form, 'form_id_Per': form_id_Per, "attachments": attachments, "form_sys_info": form_sys_info, "Reset": Reset, 'parents_form_id': parents_form_id})