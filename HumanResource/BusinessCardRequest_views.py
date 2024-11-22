from typing import Any
from django.views.generic import FormView,View
from .forms import BusinessCardRequestForm
from workFlow import Appsettings
from Company.models import Employee, Form
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from Company.DataTransformer import is_valid_and_to_send_process
from django.shortcuts import render,redirect 


class BusinessCardRequestView(LoginRequiredMixin, View):
    def get(self, request):        
        form_sys_info = Appsettings.FormCodes['名片申請單']
        
        employee = Employee.objects.get(worker_id=self.request.user.username)  # type:ignore
        # 創建表單實例時傳遞預設值
        form = BusinessCardRequestForm(initial={
            'Internalprofessionaltitle': employee.position_name,
            'Externalprofessionaltitle': employee.position_name,
            "Internalprofessionaltitle_display": employee.position_name,
        })


        context = {'form': form,
                   "form_sys_info": form_sys_info,
                   'form_id_Per': ""                   
                   }
        return render(request, "HumanResource/BusinessCardRequest.html", context)

    def post(self, request, form_id_Per=None, finish=None, Reset=None):
        form_sys_info = Appsettings.FormCodes['名片申請單']
        check_form = BusinessCardRequestForm(request.POST)

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
                return render(request, 'HumanResource/BusinessCardRequest.html', context)
        else:
            if finish:
                if check_form.is_valid():
                    is_valid_and_to_send_process(request, form_id_Per)
                    return redirect("index")
                else:                    
                    error_title = '資料驗證失敗請重新檢查資料'
                    # 如果驗證失敗，將表單重新渲染並顯示錯誤信息
                    return render(request, 'HumanResource/BusinessCardRequest.html', {'form': check_form, "form_sys_info": form_sys_info, 'form_id_Per': "", 'error_title': error_title})
            else:
                # 這邊可以將上一次所保存的資料取出來
                form = Form.objects.get(form_id=form_id_Per)
                parents_form_id = form.parents_form_id
                form = BusinessCardRequestForm(form.data)
                print(form)
                return render(request, "HumanResource/BusinessCardRequest.html", {'form': form, 'form_id_Per': form_id_Per, "form_sys_info": form_sys_info, 'Reset': Reset, 'parents_form_id': parents_form_id})
    


    # def dispatch(self, request, *args, **kwargs):
    #     print("優先順序1")
    #     # 从URL路径捕获额外的参数
    #     self.form_id_Per = kwargs.get('form_id_Per', None)
    #     self.Reset = kwargs.get('Reset', None)
    #     self.finish = kwargs.get('finish', None)
    #     return super().dispatch(request, *args, **kwargs)

    # def get_form_kwargs(self):
    #     print("優先順序2")
    #     kwargs = super().get_form_kwargs()
    #     if self.form_id_Per and not self.finish:
    #         # 如果是重新编辑，加载之前保存的数据
    #         try:
    #             form = Form.objects.get(form_id=self.form_id_Per)
    #             print("資料測試")

    #             parents_form_id = form.parents_form_id
    #             form = BusinessCardRequestForm(form.data)

    #             context = {'form': form,
    #                        'form_id_Per': self.form_id_Per,
    #                        "form_sys_info": Appsettings.FormCodes['名片申請單'],
    #                        'Reset': self.Reset,
    #                        'parents_form_id': parents_form_id}
    #             return render(self.request, "HumanResource/BusinessCardRequest.html", context)

    #         except Form.DoesNotExist:
    #             # 处理表单不存在的情况
    #             print("表單不存在")
    #             pass


    #     return kwargs

    # def form_valid(self, form):
    #     print("優先順序3")
    #     # 在这里处理验证成功的逻辑
    #     is_valid_and_to_send_process(self.request, self.form_id_Per)
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     print("優先順序4")
    #     # 处理验证失败的逻辑
    #     print("Validation failed. Errors:", form.errors)
    #     return super().form_invalid(form)

    # def get_context_data(self, **kwargs: Any):
    #     context = super().get_context_data(**kwargs)
    #     context['form_sys_info'] = Appsettings.FormCodes['名片申請單']
    #     return context
