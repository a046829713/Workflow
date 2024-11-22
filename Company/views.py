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
from .DataTransformer import update_context_info
import json
from django.views.generic import View, ListView
from workFlow.Appsettings import FORMURLS, ATTACHMENT_TRANSLATE, FORMURLS_RESET, FROM_AUTHORITY, FORMURLS_ONLYCHANGEDATA, RECRUITMENTINTERVIEWEVALUATION_TO_CHECK, RECRUITMENTINTERVIEWEVALUATION_TO_PARSER, JOBDESCRIPTION_TO_CHECK, PERSONNELADDITIONAPPLICATION_TO_CHECK
from workFlow.Appsettings import HEAVYWORKORDER_TO_CHECK, JOBDESCRIPTION_OTHER_TO_CHECK, PERSONNELADDITIONAPPLICATION_TO_CHECK2
from django.contrib.auth.mixins import LoginRequiredMixin
from HumanResource.views import RecruitmentInterviewEvaluation, PersonnelAdditionApplication, jobDescription, AccessControlPermission
from HumanResource.BusinessCardRequest_views import BusinessCardRequestView
from SignatureBusiness.views import DrawingDependencyBook, CustomerComplaintRecord
from R_D_Department.views import MeetingMinutes, SampleConfirmation, ExperimentalTest
from GeneralManagersOffice.views import CorrectiveeActionReport
from QualityAssurance.views import QualityAbnormalityReport, Heavyworkorder
from QualityAssurance.forms import QualityAbnormalityReportForm
from SignatureBusiness.forms import DrawingDependencyBookForm
from django.db.models import Q
from django.urls import reverse
from .models import Form, CustomUser
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib import messages
from .forms import ChangepasswordForm, LevelForm
from . action_deal_with import form_action_deal_with
from Company.New_Email_Send import Email_Sever
import re
from QualityAssurance.models import AbnormalFactna
from QualityAssurance.DataTransformer import generate, get_item_dict, create_abnormal, delete_abnormalna
from Database import SQL_operate
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from workFlow.Custom import GroupRequiredMixin


class SummaryForm(LoginRequiredMixin, View):
    """

        用來取得總表裡面的form
    Args:
        LoginRequiredMixin (): _description_
        View (_type_): _description_
    """

    def get(self, request):
        ALL_forms = [
            ['MeetingMinutesFormsummary', "會議記錄總表"],
            ['QualityAbnormalityReportFormsummary', "品質異常單總表"],
            ['SampleConfirmationFormsummary', "樣品確認單總表"],
            ['HeavyworkorderFormsummary', "重工單"],
            ['DrawingDependencyBooksummary', "出圖依賴書"],
            ['ExperimentalTestsummary', "實驗測試申請單"],
            ['CustomerComplaintRecordsummary', "客訴紀錄單"],
            ['jobDescriptionFormsummary', "職務說明書"],
            ['PersonnelAdditionApplicationFormsummary', "人員增補申請表"],
        ]

        # Preprocess the URLs
        for form in ALL_forms:
            form[0] = reverse(form[0])  # Replace the URL name with actual URL

        context = {
            "ALL_forms": ALL_forms,
        }

        return render(request, 'Company/summaryForm.html', context)


class reviewedForm(LoginRequiredMixin, View):
    """

        用來取得自己審核過的表單
    Args:
        LoginRequiredMixin (): _description_
        View (_type_): _description_
    """

    def get(self, request):
        catchid = CustomUser.objects.get(
            username=request.user.username).id  # type: ignore
        process_historys = Process_history.objects.all()

        filters_processids = [
            i.process_id for i in process_historys if i.approver_id == catchid]  # type: ignore

        # 透過process id 取得form id
        processes = Process.objects.all()
        filter_forms = [
            i.form_id for i in processes if i.process_id in filters_processids]

        # 排序表單的順序
        filter_forms = (
            sorted(filter_forms, key=lambda x: x.application_date, reverse=True))

        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(
            set([each_form.form_name for each_form in filter_forms]))

        context = {"forms": filter_forms,
                   "FORMURLS_RESET": FORMURLS_RESET,
                   "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
                   'Showreset_button': True,
                   'form_names': form_names,
                   'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
                   }

        # 當簽核者 和自己是同一個人的時候才能顯示該點的操作
        return render(request, 'Company/already_down.html', context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')
        # check_if_result 判定是否需要過濾空值
        forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number)

        catchid = CustomUser.objects.get(
            username=request.user.username).id  # type: ignore

        process_historys = Process_history.objects.all()

        filters_processids = [
            i.process_id for i in process_historys if i.approver_id == catchid]  # type: ignore

        # 透過process id 取得form id
        processes = Process.objects.all()
        filter_forms = [
            i.form_id for i in processes if i.process_id in filters_processids]
        filter_forms = [i for i in filter_forms if i in forms]

        # 排序表單的順序
        filter_forms = (
            sorted(filter_forms, key=lambda x: x.application_date, reverse=True))

        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(
            set([each_form.form_name for each_form in filter_forms]))
        context = {
            'forms': filter_forms,
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            "FORMURLS_RESET": FORMURLS_RESET,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'Showreset_button': True,
            'form_names': form_names,
        }

        return render(request, 'Company/already_down.html', context)


class InSideForm(LoginRequiredMixin, View):
    def get(self, request):
        # 查看人員所擁有的下屬
        subordinate_workid = get_employee_map(request.user.FullName)

        # 透過團體來過濾哪一些人可以看到
        forms = Form.objects.exclude(result='')

        filter_forms = []
        for form in forms:
            if form.applicant in subordinate_workid:
                filter_forms.append(form)
        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(
            set([each_form.form_name for each_form in filter_forms]))

        context = {
            "forms": filter_forms,
            'Showreset_button': False,
            'form_names': form_names,
        }

        # 當簽核者 和自己是同一個人的時候才能顯示該點的操作
        return render(request, 'Company/already_down.html', context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, check_if_result=True)

       # 查看人員所擁有的下屬
        subordinate_workid = get_employee_map(request.user.FullName)

        filter_forms = []
        for form in forms:
            if form.applicant in subordinate_workid:
                filter_forms.append(form)

        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(
            set([each_form.form_name for each_form in filter_forms]))

        context = {
            'forms': filter_forms,
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            "FORMURLS_RESET": FORMURLS_RESET,
            'Showreset_button': False,
            'form_names': form_names,
        }
        return render(request, 'Company/already_down.html', context)


class OutSideForm(LoginRequiredMixin, View):
    def get(self, request):
        # 取得這個人的部門
        user = request.user
        groups = user.groups.all()

        # 查看人員所擁有的團體
        all_group_name = [group.name for group in groups]

        # 透過團體來過濾哪一些人可以看到
        forms = Form.objects.exclude(result='').exclude(result='取回')

        filter_forms = []
        for form in forms:
            for each_group in FROM_AUTHORITY[form.form_name][form.version_number]:
                if each_group in all_group_name:
                    filter_forms.append(form)
                    break

        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(
            set([each_form.form_name for each_form in filter_forms]))

        context = {
            "forms": filter_forms,
            'Showreset_button': False,
            'form_names': form_names,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        # 當簽核者 和自己是同一個人的時候才能顯示該點的操作
        return render(request, 'Company/already_down.html', context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = data.get('applicant')
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, check_if_result=True)

        # 取得這個人的部門
        user = request.user
        groups = user.groups.all()

        # 查看人員所擁有的團體

        all_group_name = [group.name for group in groups]

        # 透過團體來過濾哪一些人可以看到
        filter_forms = []
        for form in forms:
            for each_group in FROM_AUTHORITY[form.form_name][form.version_number]:
                if each_group in all_group_name:
                    filter_forms.append(form)
                    break
        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(
            set([each_form.form_name for each_form in filter_forms]))

        context = {
            'forms': filter_forms,
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            "FORMURLS_RESET": FORMURLS_RESET,
            'Showreset_button': False,
            'form_names': form_names,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in filter_forms}
        }

        return render(request, 'Company/already_down.html', context)


class Allform(LoginRequiredMixin, View):
    def get(self, request):
        forms = Form.objects.filter(
            applicant=request.user.username).exclude(result='')

        form_ids = [each_form.form_id for each_form in forms]

        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(set([each_form.form_name for each_form in forms]))

        processes = Process.objects.filter(form_id_id__in=form_ids)
        processes_ids = [each_process.process_id for each_process in processes]

        map_process = [(each_process.form_id.form_id, each_process.process_id)
                       for each_process in processes]

        process_historys = Process_history.objects.filter(
            process_id__in=processes_ids)

        # 記錄歷史資料的次數來決定現在是第幾關
        count_map = get_history_level_count_map(map_process, process_historys)

        # 快速過濾符合條件的(尚未被簽核過的才能取回)
        filtered_map = [k for k, v in count_map.items() if v < 2]

        # 當取得可以退簽(取回)的表單之後開始進行資料整合
        station_map = Allform_get_station_chioce(filtered_map)

        context = {"forms": forms,
                   "FORMURLS_RESET": FORMURLS_RESET,
                   "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
                   'Showreset_button': True,
                   "filtered_map": filtered_map,
                   "station_map": station_map,
                   'form_names': form_names,
                   'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in forms}
                   }

        # 當簽核者 和自己是同一個人的時候才能顯示該點的操作
        return render(request, 'Company/already_down.html', context)

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = request.user.username
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, check_if_result=True)

        form_ids = [each_form.form_id for each_form in forms]

        # 取得每一個表單的名稱並且聚合在一起
        form_names = list(set([each_form.form_name for each_form in forms]))

        processes = Process.objects.filter(form_id_id__in=form_ids)
        processes_ids = [each_process.process_id for each_process in processes]

        map_process = [(each_process.form_id.form_id, each_process.process_id)
                       for each_process in processes]

        process_historys = Process_history.objects.filter(
            process_id__in=processes_ids)

        # 記錄歷史資料的次數來決定現在是第幾關
        count_map = get_history_level_count_map(map_process, process_historys)

        # 快速過濾符合條件的(尚未被簽核過的才能取回)
        filtered_map = [k for k, v in count_map.items() if v < 2]

        # 當取得可以退簽(取回)的表單之後開始進行資料整合
        station_map = Allform_get_station_chioce(filtered_map)
        context = {
            'forms': forms,
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            "FORMURLS_RESET": FORMURLS_RESET,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'Showreset_button': True,
            "filtered_map": filtered_map,
            "station_map": station_map,
            'form_names': form_names,
            'fullname_map': {_form.applicant: CustomUser.objects.get(username=_form.applicant).FullName for _form in forms}
        }

        return render(request, 'Company/already_down.html', context)


class Already_down(LoginRequiredMixin, View):
    def get(self, request):
        forms = Form.objects.filter(
            result__in=['退簽', '結案'], applicant=request.user.username)

        return render(request, "Company/already_down.html", {'forms': forms, "FORMURLS_RESET":
                                                             FORMURLS_RESET, "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA, 'Showreset_button': True})

    def post(self, request):
        data = querydict_to_dict(request.POST)
        start_date = data.get('start-date')
        end_date = data.get('end-date')
        applicant = request.user.username
        form_name = data.get('form_name')
        status = data.get('status')
        form_number = data.get('form_number')

        forms = filter_forms_condition(
            start_date, end_date, applicant, form_name, status, form_number, check_if_result=True, result_in=True)

        context = {
            'forms': forms,
            'start_date': start_date if start_date else '',
            'end_date': end_date if end_date else '',
            'applicant': applicant if applicant else '',
            'form_name': form_name if form_name else '',
            'status': status if status else '',
            "FORMURLS_RESET": FORMURLS_RESET,
            "FORMURLS_ONLYCHANGEDATA": FORMURLS_ONLYCHANGEDATA,
            'Showreset_button': True
        }

        return render(request, 'Company/already_down.html', context)


class FormDraft(LoginRequiredMixin, View):
    """

        表單草稿的製做
    """

    def get(self, request):        
        forms = Form.objects.filter(applicant=request.user.username, result='')
        return render(request, "Company/draft.html", {'forms': forms, "FORMURLS":
                                                      FORMURLS})

    def post(self, request):
        pass


class SaveFrom(LoginRequiredMixin, View):
    def save_check(self, form: Form, post_data: dict, form_id_Per):
        # 當有特殊的保存狀況要處理時，可以進來這裡
        if form.form_name == '重工單' and form.version_number == 'B':
            # 當保存資料的時候，檢查是否有變異
            # 當預計完工日改變時要通知採購
            if post_data.get('estimated_completion_date') != form.data.get('estimated_completion_date'):
                mailserver = Email_Sever(windows_path=r'C:\Users\user\Desktop\程式專區\Workflow\workflow\Company\templates\Email\DateChange_Email.html',
                                         linux_path=r'/home/user/桌面/program/Workflow/workflow/Company/templates/Email/DateChange_Email.html')
                mailserver.update_Recipient_list(User_data=list(
                    CustomUser.objects.filter(groups__in=[Group.objects.get(name='採購組')])))
                mailserver.change_context(form_id=form_id_Per)
                mailserver.Send('重工單異動通知')

            # {'01': {'factoryno': '110119', 'makeno': '01'}, '02': {'factoryno': '110172', 'makeno': '02'}}
            item_data = get_item_dict(generate(post_data))
            print(item_data)

            # 比對現有資料，如果不存在先新增
            abnormalfactnas = AbnormalFactna.objects.filter(
                form_id=form.form_id)
            items = list(abnormalfactnas.values_list('item', flat=True))
            print(items)
            print('*'*120)
            ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")
            FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
            FACT_map = {fact_no: fact_na for fact_no,
                        fact_na in FACT_df.values}
            ROUT_df = ERP_sql.get_pd_data("select ROUT_NO,ROUT_NA from ROUT")
            ROUT_map = {rout_no: rout_na for rout_no,
                        rout_na in ROUT_df.values}

            for key, value in item_data.items():
                if key in items:
                    # 不檢查全部覆寫
                    for abnormalfactna in abnormalfactnas:
                        if key == abnormalfactna.item:
                            abnormalfactna.factoryno = value['factoryno']
                            abnormalfactna.factoryname = FACT_map[value['factoryno']]
                            abnormalfactna.makeno = value['makeno']
                            abnormalfactna.makename = ROUT_map[value['makeno']]
                            abnormalfactna.save()
                else:
                    # 如果是新增的要幫他創建
                    create_abnormal(key, value, form.form_id,
                                    FACT_map, ROUT_map)
            # 如果使用者刪除了，畫面的部分也要改掉
            for item_key in items:
                if item_data.get(item_key) is None:
                    delete_abnormalna(key=item_key, form_id=form.form_id)

    def post(self, request, form_id_Per=None):
        # 获取表单数据
        post_data = querydict_to_dict(request.POST)
        applicant = post_data.pop('applicant', '')
        # 如果已經存在表單
        if form_id_Per:
            form = Form.objects.get(form_id=form_id_Per)
            self.save_check(form, post_data, form_id_Per)
            keys_to_remove = ['form_name', 'form_id', 'version_number',
                              'result', 'application_date', 'closing_date', 'parents_form_id']
            for key in keys_to_remove:
                post_data.pop(key, None)

            form.data = post_data
            form.save()

        # 尚未存在表單
        else:
            form = Form()
            form.form_id = form_id_Per if form_id_Per else GetFormID(
                post_data.pop('form_id', None))

            form.form_name = post_data.pop('form_name', '')
            form.applicant = applicant
            form.version_number = post_data.pop(
                'version_number', '')

            form.data = post_data
            form.parents_form_id = post_data.pop('parents_form_id', '')
            form.save()

        check_and_save_file(form, request, check_repeat=True)
        return redirect('form_application')


@login_required
def form_application(request):
    return render(request, "Company/form_application.html", {'approved_form_num': len(approved_transfor(request))})


def index(request):
    return render(request, "Company/index.html")


def register(request):
    if request.method == 'POST':  # 當使用者提交資料
        form = UserCreationForm(request.POST)  # 內建的form，model為User。
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/quiz')
        else:
            return render(request, 'Company/register.html', {'form': form})
    else:
        form = UserCreationForm()
        context = {'form': form}
        return render(request, 'Company/register.html', context)


def post_login(request):
    """

        if request.method == 'POST': 檢查請求的方法是否為 'POST'。在 HTTP 協議中，'POST' 通常用於提交數據。

        username = request.POST['username'] 和 password = request.POST['password'] 從請求的 POST 數據中獲取用戶名和密碼。

        user = auth.authenticate(username=username, password=password) 調用 Django 的 authenticate 函數嘗試驗證提供的用戶名和密碼。如果用戶名和密碼正確，它會返回一個 User 物件，否則返回 None。

        if user and user.is_staff is False: 如果驗證成功（即 user 不為 None），並且用戶不是員工（即 user.is_staff 為 False），那麼登入該用戶並重定向到 '/login/' 頁面。

        elif user and user.is_staff is True: 如果驗證成功，並且用戶是員工，那麼登入該用戶並重定向到 '/quiz/' 頁面。

        else: 如果驗證失敗，重定向到 '/login/' 頁面。

        else: 如果請求的方法不是 'POST'（比如是 'GET'），那麼渲染 'registration/login.html' 模板並返回給用戶。
    """
    # 表單提交之後
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active is True:
            auth.login(request, user)
            return HttpResponseRedirect('index')
        else:
            return HttpResponseRedirect('login')
    else:
        return render(request, 'Company/login.html', locals())


class AddModelView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Level
    form_class = LevelForm
    template_name = 'Company/add_model.html'
    success_url = reverse_lazy('add_model')
    group_required = ['admin']

    def form_valid(self, form):
        post_data = querydict_to_dict(self.request.POST)
        form.instance.level_id = get_level_id(
            post_data['level_name'], post_data['versionNumber'])
        form.instance.previous_station = get_previous_station(
            post_data['level_name'], post_data['versionNumber'], post_data['station_name'])
        form.instance.station_choice = post_data['station_choice'] if isinstance(
            post_data['station_choice'], list) else [post_data['station_choice']]
        form.instance.station_group = json.dumps(post_data.get('station_group', '') if isinstance(
            post_data.get('station_group', ''), list) else [post_data.get('station_group', '')])
        form.instance.endorsement_group = json.dumps(post_data.get('endorsement_group', '') if isinstance(
            post_data.get('endorsement_group', ''), list) else [post_data.get('endorsement_group', '')])
        form.instance.limited_time = ''

        response = super().form_valid(form)

        messages.success(self.request, '創建流程成功!')
        return response

    def form_invalid(self, form):
        errors = form.errors
        messages.error(self.request, '表單驗證失敗，請檢查輸入內容。')
        return render(self.request, self.template_name, {'form': form, 'errors': errors})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ShowFormListView(LoginRequiredMixin, ListView):
    model = Form
    template_name = "Company/approved.html"
    context_object_name = 'forms'
    paginate_by = 20  # 每页显示的对象数量

    def get_queryset(self):
        form_ids = []
        if self.request.method == 'GET':
            if self.request.GET.get('page') == '1' or not self.request.GET.get('page'):
                forms = approved_transfor(self.request)
                form_ids = [form.form_id for form in forms]
                self.request.session['approved_form_ids'] = form_ids
            else:
                form_ids = self.request.session.get('approved_form_ids', [])

        # 返回 QuerySet，并处理可能的异常
        if form_ids:
            # 返回排序后的 QuerySet，首先按 application_date 降序，然后按 form_name 升序
            return Form.objects.filter(form_id__in=form_ids).order_by('form_name','-application_date')
        else:
            return Form.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context


@login_required
def form_information_finish(request, form_id):
    """
        用來顯示已完成的表單的完整狀況
        1.申請人資訊
        2.表單內容
        3.表單復件
        4.表單流程
    Args:
        request (_type_): _description_
        form_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    # 取得表單的唯一資料來比對相關的資訊
    form_object = Form.objects.get(form_id=form_id)

    CustomUser_object = CustomUser.objects.get(
        username=form_object.applicant)

    Heavyworkorder_to_check = HEAVYWORKORDER_TO_CHECK
    Heavyworkorder_to_check_to_parser = [
        f'製程廠商{i}' for i in range(int(count_factmk_name(form_object.data) / 2))]

    # 如果是舊的重工單,額外處理
    if form_object.form_name == '重工單' and len(form_id) != 16:
        clean_data = Clean_date(
            form_object.data, form_object.form_name, form_object.version_number)
        context = {"form": form_object,
                   "form_clean_data": clean_data,
                   'customuser': CustomUser_object,
                   "form_finish": True,
                   'Heavyworkorder_to_check': Heavyworkorder_to_check,
                   "Heavyworkorder_to_check_to_parser": Heavyworkorder_to_check_to_parser
                   }

        update_context_info(form_object, context, request)
        
        return render(request, 'Company/form_information.html', context)

    # 要將某些地方轉換成中文
    if form_object.form_name == '重工單':
        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")

        FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
        
        if form_object.data.get('paying_unit'):
            form_object.data['paying_unit'] = FACT_df[FACT_df['FACT_NO'] == form_object.data.get('paying_unit')]['FACT_NA'].iloc[0]
        
        if form_object.data.get('responsible_unit'):    
            form_object.data['responsible_unit'] = FACT_df[FACT_df['FACT_NO'] == form_object.data.get('responsible_unit')]['FACT_NA'].iloc[0]



    process = Process.objects.get(form_id=form_id)

    # 取得所有關卡 用來渲染尚未完成的關卡
    all_level = Level.objects.filter(level_id__startswith=process.level_id)

    # 用來將流程的歷史資料傳入
    ProcessHistory = Process_history.objects.filter(
        process_id=process.process_id)

    allProcessHistory_name = [
        _process.site_record for _process in ProcessHistory]

    last_site_record = ProcessHistory.last().site_record  # type: ignore

    translate_data = ATTACHMENT_TRANSLATE[form_object.form_name][form_object.version_number]
    attachments = form_object.attachments.all()

    clean_data = Clean_date(form_object.data, form_object.form_name,
                            form_object.version_number)

    # 取得來源表單的關係表單
    relationship_forms = get_resourcenumber_forms(form_object, form_id)

    # 非強制關係表單
    if form_object.relationshipnumber:
        relationship_forms = relationship_forms | Form.objects.filter(
            form_id=form_object.relationshipnumber)

    RecruitmentInterviewEvaluation_to_check = RECRUITMENTINTERVIEWEVALUATION_TO_CHECK
    RecruitmentInterviewEvaluation_to_parser = RECRUITMENTINTERVIEWEVALUATION_TO_PARSER
    jobdescription_to_check = JOBDESCRIPTION_TO_CHECK
    jobdescription_other_to_check = JOBDESCRIPTION_OTHER_TO_CHECK

    jobdescription_to_check_to_parser = vaild_job(form_object.data)

    jobdescription_language_to_check_to_parser = [
        f'語言能力{i}' for i in range(int(count_language(form_object.data) / 4))]

    jobdescription_tool_to_check_to_parser = [
        f'擅長工具{i}' for i in range(int(count_tool(form_object.data) / 3))]

    jobdescription_work_skill_to_check_to_parser = [
        f'工作技能{i}' for i in range(int(count_work_skill(form_object.data) / 3))]

    personneladditionapplication_to_check = PERSONNELADDITIONAPPLICATION_TO_CHECK
    personneladditionapplication_to_check2 = PERSONNELADDITIONAPPLICATION_TO_CHECK2
    
    

         
    context = {"form": form_object,
               "form_clean_data": clean_data,
               'customuser': CustomUser_object,
               'ProcessHistory': ProcessHistory,
               "This_site_record": last_site_record,
               "attachments": attachments,
               "form_finish": True,
               "translate_data": translate_data,
               'all_level': all_level,
               'allProcessHistory_name': allProcessHistory_name,
               "relationship_forms": relationship_forms,
               "RecruitmentInterviewEvaluation_to_check": RecruitmentInterviewEvaluation_to_check,
               "RecruitmentInterviewEvaluation_to_parser": RecruitmentInterviewEvaluation_to_parser,
               "jobdescription_to_check": jobdescription_to_check,
               'jobdescription_to_check_to_parser': jobdescription_to_check_to_parser,
               "jobdescription_other_to_check": jobdescription_other_to_check,
               'jobdescription_language_to_check_to_parser': jobdescription_language_to_check_to_parser,
               'jobdescription_tool_to_check_to_parser': jobdescription_tool_to_check_to_parser,
               "jobdescription_work_skill_to_check_to_parser": jobdescription_work_skill_to_check_to_parser,
               'personneladditionapplication_to_check': personneladditionapplication_to_check,
               'Heavyworkorder_to_check': Heavyworkorder_to_check,
               "Heavyworkorder_to_check_to_parser": Heavyworkorder_to_check_to_parser,
               "personneladditionapplication_to_check2": personneladditionapplication_to_check2
               }

    update_context_info(form_object, context, request)
    return render(request, 'Company/form_information.html', context)


@login_required
def form_information(request, form_id):
    """
        用來顯示表單的完整狀況
        1.申請人資訊
        2.表單內容
        3.表單副件        
        4.表單關卡
        5.表單流程
        5.簽核
    Args:
        request (_type_): _description_
        form_id (_type_): _description_
        我讓Company_process_real 和Company_process_history 的站點名稱不同用以呈現駁回的方式
    Returns:
        _type_: _description_
    """
    # 取得表單的唯一資料來比對相關的資訊
    form_object = Form.objects.get(form_id=form_id)

    # 用來取得和母單所不同的區塊
    different_keys = []
    if form_object.parents_form_id:
        parents_form_object = Form.objects.get(
            form_id=form_object.parents_form_id)

        different_keys = check_different_dict(
            form_object.data, parents_form_object.data)

        different_keys = Clean_date(different_keys, form_object.form_name,
                                    form_object.version_number)

    CustomUser_object = CustomUser.objects.get(username=form_object.applicant)

    process = Process.objects.get(form_id=form_id)

    # 取得所有關卡 用來渲染尚未完成的關卡
    all_level = Level.objects.filter(level_id__startswith=process.level_id)
    
    process_id = process.process_id
    process_real = Process_real.objects.get(process_id=process_id)
    approval_status = process_real.approval_status

    
    endorsement_allow = process_real.endorsement_allow

    # 用來將流程的歷史資料傳入
    ProcessHistory = Process_history.objects.filter(process_id=process_id)
    last_site_record = ProcessHistory.last().site_record

    # 簽核區域
    # 這邊會有一個問題是
    station_choice, next_station, previous_station = Get_station_choice(
        process.level_id, last_site_record, approval_status, endorsement_allow)

    translate_data = ATTACHMENT_TRANSLATE[form_object.form_name][form_object.version_number]
    attachments = form_object.attachments.all().order_by('name')
    
    # 要將某些地方轉換成中文
    if form_object.form_name == '重工單':
        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")
        FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
        
        if form_object.data.get('paying_unit'):
            form_object.data['paying_unit'] = FACT_df[FACT_df['FACT_NO'] == form_object.data.get('paying_unit')]['FACT_NA'].iloc[0]
        
        if form_object.data.get('responsible_unit'):    
            form_object.data['responsible_unit'] = FACT_df[FACT_df['FACT_NO'] == form_object.data.get('responsible_unit')]['FACT_NA'].iloc[0]
    
    
    
    clean_data = Clean_date(form_object.data, form_object.form_name,
                            form_object.version_number)

    # 取得來源表單的關係表單
    relationship_forms = get_resourcenumber_forms(form_object, form_id)

    # 非強制關係表單
    if form_object.relationshipnumber:
        relationship_forms = relationship_forms | Form.objects.filter(
            form_id=form_object.relationshipnumber)

    RecruitmentInterviewEvaluation_to_check = RECRUITMENTINTERVIEWEVALUATION_TO_CHECK
    RecruitmentInterviewEvaluation_to_parser = RECRUITMENTINTERVIEWEVALUATION_TO_PARSER
    jobdescription_to_check = JOBDESCRIPTION_TO_CHECK
    jobdescription_other_to_check = JOBDESCRIPTION_OTHER_TO_CHECK
    Heavyworkorder_to_check = HEAVYWORKORDER_TO_CHECK

    jobdescription_to_check_to_parser = vaild_job(form_object.data)

    jobdescription_language_to_check_to_parser = [
        f'語言能力{i}' for i in range(int(count_language(form_object.data) / 4))]

    jobdescription_tool_to_check_to_parser = [
        f'擅長工具{i}' for i in range(int(count_tool(form_object.data) / 3))]

    jobdescription_work_skill_to_check_to_parser = [
        f'工作技能{i}' for i in range(int(count_work_skill(form_object.data) / 3))]
    Heavyworkorder_to_check_to_parser = [
        f'製程廠商{i}' for i in range(int(count_factmk_name(form_object.data) / 2))]

    personneladditionapplication_to_check = PERSONNELADDITIONAPPLICATION_TO_CHECK
    personneladditionapplication_to_check2 = PERSONNELADDITIONAPPLICATION_TO_CHECK2

    context = {"form": form_object,
               "form_clean_data": clean_data,
               'customuser': CustomUser_object,
               'ProcessHistory': ProcessHistory,
               'station_choice': station_choice,
               'next_station': next_station,
               'previous_station': previous_station,
               'process_id': process_id,
               "This_site_record": last_site_record,
               "attachments": attachments,
               "form_finish": False,
               "translate_data": translate_data,
               'all_level': all_level,
               "approval_status": json.loads(approval_status.replace("'",'"')), # 這邊可能有list  和 str 兩種狀態
               'different_keys': different_keys,
               "relationship_forms": relationship_forms,
               "RecruitmentInterviewEvaluation_to_check": RecruitmentInterviewEvaluation_to_check,
               'RecruitmentInterviewEvaluation_to_parser': RecruitmentInterviewEvaluation_to_parser,
               "jobdescription_to_check": jobdescription_to_check,
               'jobdescription_to_check_to_parser': jobdescription_to_check_to_parser,
               "jobdescription_other_to_check": jobdescription_other_to_check,
               'jobdescription_language_to_check_to_parser': jobdescription_language_to_check_to_parser,
               'jobdescription_tool_to_check_to_parser': jobdescription_tool_to_check_to_parser,
               "jobdescription_work_skill_to_check_to_parser": jobdescription_work_skill_to_check_to_parser,
               'personneladditionapplication_to_check': personneladditionapplication_to_check,
               'Heavyworkorder_to_check': Heavyworkorder_to_check,
               "Heavyworkorder_to_check_to_parser": Heavyworkorder_to_check_to_parser,
               "personneladditionapplication_to_check2": personneladditionapplication_to_check2}

    # 更新各表單需要的資料
    update_context_info(form_object, context, request)
    
    
    # 當品質異常單需要確認的時候要把資料傳入
    if form_object.form_name == '品質異常單':
        QAR_form = QualityAbnormalityReportForm(form_object.data)
        context.update({"QAR_form": QAR_form})
        # 當品質異常單需要加簽的時候要把資料傳入
        employee_data = get_QAR_employee_data()
        context.update({"employee_data": employee_data})

    # 當出圖依賴書需要上傳檔案的時候要把資料傳入
    if form_object.form_name == '出圖依賴書' and form_object.version_number == 'B':
        attachment_map = {f'attachment{i}': f'附件{i}'for i in range(1, 9)}  # 创建一个范围列表
        context.update({"attachment_map": attachment_map})


    return render(request, 'Company/form_information.html', context)


@login_required
def forbidden(request):
    return render(request, 'Company/Forbidden.html')


def remove_form(request, form_id):
    """

        將不要的form表單從資料裡面刪除
    Args:
        request (_type_): _description_
        form_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    post_data = querydict_to_dict(request.POST)
    Form.objects.get(form_id=form_id).delete()
    return redirect('FormDraft')


class ChangeURLSaveORSubmit(LoginRequiredMixin, View):
    def get(self, request):
        pass

    def post(self, request):
        data = querydict_to_dict(request.POST)
        form_id_Per = data.get('form_id_Per', None)
        action = data.get('action', None)
        form_name = data.get("form_name", None)
        version_number = data.get("version_number", None)
        parents_form_id = data.get("parents_form_id", None)

        map_object = {
            "人員增補申請表":
            {
                "A": PersonnelAdditionApplication
            },
            "招募面試評核表": {
                "A": RecruitmentInterviewEvaluation
            },
            "職務說明書": {
                "A": jobDescription
            },
            "出圖依賴書": {
                "A": DrawingDependencyBook,
                "B": DrawingDependencyBook,

            },
            "客訴紀錄單": {
                "A": CustomerComplaintRecord,
                "B": CustomerComplaintRecord,
            },
            "會議記錄": {
                "A": MeetingMinutes
            },
            "品質異常單": {
                "A": QualityAbnormalityReport
            },
            "矯正預防措施處理單": {
                "A": CorrectiveeActionReport
            },
            "樣品確認單": {
                "A": SampleConfirmation
            },
            "重工單": {
                "A": Heavyworkorder,
                "B": Heavyworkorder
            },
            "實驗測試申請單": {
                "A": ExperimentalTest
            },
            "門禁權限申請單": {
                "A": AccessControlPermission
            },
            "名片申請單": {
                "A": BusinessCardRequestView
            }
        }

        # 表單尚未擁有formid
        if form_id_Per is None or not form_id_Per:
            if action is not None:
                # type: ignore
                return map_object[form_name][version_number].as_view()(request)
            else:
                return SaveFrom.as_view()(request)  # 如果這個request 是一個POST方法,傳送過去也會是觸發POST
        else:
            # 如果表單已經有了formid
            if action is not None:
                return map_object[form_name][version_number].as_view()(request, form_id_Per=form_id_Per, finish=True)
            else:
                return SaveFrom.as_view()(request, form_id_Per=form_id_Per)


class Illustrate(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        return render(request, 'Company/illustrate.html', context)


class change_passward(LoginRequiredMixin, View):
    def get(self, request):

        form = ChangepasswordForm()
        context = {"form": form}
        return render(request, 'Company/change_password.html', context)

    def post(self, request):
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_new_password = request.POST.get('confirmNewPassword')
        form = ChangepasswordForm()
        context = {"form": form}
        user = request.user

        if not user.check_password(current_password):
            # Current password is not correct
            messages.error(request, '當前用戶密碼錯誤,請重新確認')
            return render(request, 'Company/change_password.html', context)

        if new_password != confirm_new_password:
            # New passwords do not match
            messages.error(request, '新密碼並不相同')
            return render(request, 'Company/change_password.html', context)

        # Update the password
        user.set_password(new_password)
        user.save()

        # Updating the session
        update_session_auth_hash(request, user)

        messages.success(request, '密碼更新完成')
        return render(request, 'Company/index.html')
