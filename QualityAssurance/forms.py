from django import forms
from Company.models import CustomUser, Form, Employee
from django_select2.forms import Select2Widget
from Database import SQL_operate
from django.utils import timezone
from django.core.cache import cache
import time
from datetime import date, timedelta


def get_next_month_last_day():
    # 獲取今天的日期
    today = date.today()

    # 計算下個月的第一天
    # 首先計算當前月份的最後一天，然後加一天
    first_day_next_month = date(
        today.year, today.month, 1) + timedelta(days=64)
    first_day_next_month = first_day_next_month.replace(day=1)

    # 計算下個月的最後一天
    # 這可以通過從下下個月的第一天減去一天來實現
    last_day_next_month = first_day_next_month - timedelta(days=1)

    return last_day_next_month.strftime('%Y-%m-%d')


def get_fact_choices():
    # 尝试从缓存中获取数据
    FACT_CHOICES = cache.get('FACT_CHOICES')

    # 如果缓存中没有数据，那么查询数据库并设置缓存
    if FACT_CHOICES is None:
        sql = SQL_operate.DB_operate(sqltype="YBIT")
        FACT_df = sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
        FACT_CHOICES = [(i, i)for i in FACT_df['FACT_NO'] +
                        ' ' + FACT_df['FACT_NA'].to_list()]
        # 将数据存储在缓存中，这里设置为600秒（10分钟）的过期时间。
        # 您可以根据需要调整此过期时间。
        cache.set('FACT_CHOICES', FACT_CHOICES, 600)

    return FACT_CHOICES


class QualityAbnormalityReportForm(forms.Form):
    sql = SQL_operate.DB_operate(sqltype="YBIT")

    CUST_df = sql.get_pd_data("select CUST_NO,CUST_NA,CONT_NO from CUST")
    PURC_df = sql.get_pd_data("select PURC_NO from PURC")
    MAKE_df = sql.get_pd_data("select MAKE_NO from MAKE")

    filters_form = Form.objects.filter(form_name='客訴紀錄單')
    MOTHER_FORM_CHOICES = [(each_form.form_id, each_form.form_id + '/' +
                            each_form.data['customer_number']) for each_form in filters_form]

    abnormal_df = SQL_operate.DB_operate(
        sqltype="MIS").get_pd_data("select 編號 from abnormal")

    CUSTOMER_NUMBER_CHOICES = [
        (i, i)for i in CUST_df['CUST_NO'] + ' ' + CUST_df['CUST_NA'].to_list()]

    ABNORMAL_CHOICES = [
        (i, i)for i in abnormal_df['編號']
    ]

    PURC_NO_CHOICES = [(i, i) for i in PURC_df['PURC_NO'].to_list()]
    MAKE_NO_CHOICES = [(i, i) for i in MAKE_df['MAKE_NO'].to_list()]

    SOURCE_CHOICES = [
        ("", '--'),
        ('客戶報怨及要求', '客戶報怨及要求'),
        ('廠商進料不良', '廠商進料不良'),
        ('產線組裝不良', '產線組裝不良'),
    ]

    ASSEMBLE_CHOICES = [
        ("", '--'),
        ('裝配一組', '裝配一組'),
        ('裝配二組', '裝配二組'),
        ('裝配三組', '裝配三組'),
    ]

    STATUS_CHOICES = [
        ("", '--'),
        ('製程中', '製程中'),
        ('成品', '成品'),

    ]

    model_number = forms.CharField(
        label="型號代碼",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=500
    )

    model_name = forms.CharField(
        label="型號名稱",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=500,
    )

    source_category = forms.ChoiceField(
        label="來源類別",
        choices=SOURCE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'source_category'}),
    )

    # complaint_number 原本的命名,但是為了記錄母表要改成統一名稱resource_no
    resource_no = forms.ChoiceField(
        choices=MOTHER_FORM_CHOICES,
        label="客訴單號",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    purchase_number = forms.ChoiceField(
        choices=PURC_NO_CHOICES,
        label="採購單號",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    fact_number = forms.ChoiceField(
        choices=get_fact_choices(),
        label="廠商編號",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    batch_sizes = forms.CharField(
        label="批量",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'batch_sizes', 'placeholder': '請輸入批量(選填)'}))

    manufacturing_order = forms.ChoiceField(
        choices=MAKE_NO_CHOICES,
        label="製令單號",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    assemble = forms.ChoiceField(
        choices=ASSEMBLE_CHOICES,
        label="組裝單位",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    material_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="料件狀態",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    Exception_description = forms.CharField(
        label="異常說明",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'Exception_description'})
    )

    number_retries = forms.IntegerField(
        label="再發次數",
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'id': 'number_retries'})
    )

    cause_analysis = forms.CharField(
        label="原因分析",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'cause_analysis'})
    )

    temporary_measures = forms.CharField(
        label="暫時處置對策",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'temporary_measures'})
    )

    permanent_disposal_countermeasures = forms.CharField(
        label="永久處置對策",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'permanent_disposal_countermeasures'})
    )

    remark_area = forms.CharField(
        label="備註",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'remark_area'})
    )

    attachment1 = forms.FileField(
        label="附件1",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment1'})
    )

    attachment2 = forms.FileField(
        label="附件2",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment2'})
    )

    attachment3 = forms.FileField(
        label="附件3",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment3'})
    )

    attachment4 = forms.FileField(
        label="附件4",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment4'})
    )

    attachment5 = forms.FileField(
        label="附件5",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment5'})
    )

    attachment6 = forms.FileField(
        label="附件6",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment6'})
    )

    attachment7 = forms.FileField(
        label="附件7",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment7'})
    )
    attachment8 = forms.FileField(
        label="附件8",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment8'})
    )
    attachment9 = forms.FileField(
        label="附件9",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment9'})
    )
    attachment10 = forms.FileField(
        label="附件10",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment10'})
    )
    attachment11 = forms.FileField(
        label="附件11",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment11'})
    )
    attachment12 = forms.FileField(
        label="附件12",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment12'})
    )
    rework_order = forms.ChoiceField(
        choices=ABNORMAL_CHOICES,
        label="重工單(選填)",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    other_disposition_documents = forms.CharField(
        label="其他處置單據(選填)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'manufacturing_order', 'placeholder': '請輸入其他單據編號(選填)'}))


class DisposalMethodForm(forms.Form):
    EXCEPTION_CATEGORY_CHOICES = [
        ("", '--'),
        ('尺寸', '尺寸'),
        ('外觀', '外觀'),
        ('其他', '其他'),

    ]
    DISPOSAL_METHOD_CHOICES = [
        ("", '--'),
        ('退貨', '退貨'),
        ('特採', '特採'),
        ('修圖', '修圖'),
        ('重工', '重工'),
        ('其他', '其他'),

    ]
    # PROD_CHOICES = get_prod_choices()

    part_name_and_number = forms.ChoiceField(
        choices=[],
        label="料號品名",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control js-data-example-ajax'})
    )

    exception_category = forms.ChoiceField(
        choices=EXCEPTION_CATEGORY_CHOICES,
        label="異常類別",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )
    disposal_way = forms.ChoiceField(
        choices=DISPOSAL_METHOD_CHOICES,
        label="處置方式",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    responsible_unit = forms.ChoiceField(
        choices=get_fact_choices(),
        label="責任單位",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )


DisposalMethodFormset = forms.formset_factory(DisposalMethodForm, extra=1)


class HeavyworkorderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HeavyworkorderForm, self).__init__(*args, **kwargs) 
        # 静态选项，可根据需要调整
        self.fields['heavy_industry_information'].choices = [
            ('品質異常單', '品質異常單'),
            ('品保異常品處理', '品保異常品處理'),
            ('設計變更單', '設計變更單')
        ]
    
    ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")

    FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
    FACT_CHOICES = [('', '--')] + [(fact_no,f'{fact_no} {fact_na}') for fact_no, fact_na in FACT_df.values]
    
    
    
    quantity = forms.IntegerField(
        label="數量",
        widget=forms.NumberInput(
            attrs={'class': 'form-control'})
    )

    responsible_unit = forms.ChoiceField(
        choices=FACT_CHOICES,
        label="責任單位",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    paying_unit = forms.ChoiceField(
        choices=FACT_CHOICES,
        label="付費單位",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    heavy_industry_information = forms.ChoiceField(
        choices=[],
        label="重工訊息來源",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )
    source_notes = forms.CharField(
        label="來源備註",
        widget=forms.Textarea(
            attrs={'class': 'form-control'})
    )

    estimated_completion_date = forms.DateField(
        label="預計完工日",
        initial=get_next_month_last_day(),
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',  # 確保日期格式為 YYYY-MM-DD
            attrs={'type': 'date', 'class': 'form-control'}),

    )

    remark = forms.CharField(
        label="備註",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control'})
    )

    prod_no_before = forms.ChoiceField(
        choices=[],
        label="產品編號(重工前)",
        widget=Select2Widget(attrs={'class': 'form-control'}
        )
    )

    prod_name_before = forms.CharField(
        label="品名規格(重工前)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control ', 'readonly': 'readonly'}))

    prod_no_after = forms.ChoiceField(
        choices=[],
        label="產品編號(重工後)",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )
    prod_name_after = forms.CharField(
        label="品名規格(重工後)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control ', 'readonly': 'readonly'}))

    rebuild_reason = forms.CharField(
        label="重工原因",
        widget=forms.Textarea(
            attrs={'class': 'form-control'})
    )

    pay_after_heavy_work = forms.CharField(
        label="重工後處置",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control '}))

    io_number = forms.ChoiceField(
        choices=[],
        label="IO單號",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    Heavy_industry_projects = forms.CharField(
        label="重工項目",
        widget=forms.Textarea(
            attrs={'class': 'form-control'})
    )
    
    Withdraw_TYPE = forms.ChoiceField(
        choices=[
        ("", '--'),
        ('在製', '在製'),
        ('庫存', '庫存'),
    ],
        label="來源類別",
        widget=Select2Widget(attrs={'class': 'form-control'})
    ) 

class FactMKForm(forms.Form):
    ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")

    FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA from FACT")
    FACT_CHOICES = [('', '--')] + [(fact_no,
                                    f'{fact_no} {fact_na}') for fact_no, fact_na in FACT_df.values]

    ROUT_df = ERP_sql.get_pd_data("select ROUT_NO,ROUT_NA from ROUT")
    ROUT_CHOICES = [('', '--')] + [(rout_no,
                                    f'{rout_no} {rout_na}') for rout_no, rout_na in ROUT_df.values]

    Factname = forms.ChoiceField(
        choices=FACT_CHOICES,
        label="廠商名稱",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )
    ROUTname = forms.ChoiceField(
        choices=ROUT_CHOICES,
        label="製程名稱",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )


FactMKFormset = forms.formset_factory(FactMKForm, extra=1)
