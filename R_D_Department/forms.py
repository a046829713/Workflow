from django import forms
from Company.models import CustomUser, Form
from django_select2.forms import Select2Widget,Select2MultipleWidget
from Database import SQL_operate
from django.utils import timezone
from workFlow.FormAppsettings import PROD_TYPE_CHOICES

class MeetingMinutesForm(forms.Form):
    all_customuser = CustomUser.objects.all()
    filters_form = Form.objects.filter(form_name='出圖依賴書')

    MOTHER_FORM_CHOICES = [(each_form.form_id, each_form.form_id + '  ' + each_form.data.get('newProductNumber','') + '  ' + each_form.applicant) for each_form in filters_form]

    CUSTOMUSER_CHOICES = [(user.username + '  ' + user.FullName,
                           user.username + '  ' + user.FullName) for user in all_customuser if user.username != 'Administrator']

    FILE_NO_CHOICES = [
        ("YB54-N35-REV03", "YB54-N35-REV03")
    ]

    CONFERENCE_NAME_CHOICES = [
        ("其他", "其他"),
        ("啟動會議", "啟動會議"),
        ("規劃審查會議", "規劃審查會議"),
        ("設計審查會議", "設計審查會議"),
        ("試量產審查會議", "試量產審查會議"),
        ("新品發表會議", "新品發表會議"),
    ]

    iso_file_no = forms.ChoiceField(
        label="文件編號(ISO)",
        choices=FILE_NO_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'iso_file_no'}),
    )

    meeting_place = forms.CharField(
        label="會議場所", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    meeting_moderator = forms.ChoiceField(
        choices=CUSTOMUSER_CHOICES,
        label="會議主持人",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'meeting_moderator'})
    )

    meeting_address = forms.CharField(
        label="會議地址", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    resource_no = forms.ChoiceField(
        choices=MOTHER_FORM_CHOICES,
        label="來源單號(選填)",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'resource_no'})
    )

    newProductName = forms.CharField(
        label="產品(型號)名稱", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    conferenceName = forms.ChoiceField(
        label="會議名稱",
        choices=CONFERENCE_NAME_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'conferenceName'}),
    )

    conference_start_datetime = forms.DateTimeField(
        label="開始日期時間",
        initial=timezone.now(),
        widget=forms.DateTimeInput(format=('%Y-%m-%dT%H:%M'),
                                   attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'conference_start_datetime'}),
    )

    conference_end_datetime = forms.DateTimeField(
        label="結束日期時間",
        initial=timezone.now(),
        widget=forms.DateTimeInput(format=('%Y-%m-%dT%H:%M'),
                                   attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'conference_end_datetime'}),
    )

    attendees = forms.MultipleChoiceField(
        label="與會人員",
        choices=CUSTOMUSER_CHOICES,
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select select2-multiple', 'id': 'attendees'}),
    )
    content = forms.CharField(
        label="內容概要",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'content'})
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

class ExperimentalTestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        TAGS_CHOICES = kwargs.pop('tags_choices', [])
        CORPORATION_CHOICES = kwargs.pop('coprorataion_choices', [])
        super(ExperimentalTestForm, self).__init__(*args, **kwargs)

        self.fields['tags'] = forms.MultipleChoiceField(
            choices=TAGS_CHOICES,
            label="標籤選擇(可複選)",
            widget=Select2MultipleWidget(attrs={'class': 'form-control', 'id': 'Tags_control'})
        )
        self.fields['Compet_corporation'] = forms.ChoiceField(
            choices=CORPORATION_CHOICES,
            required=False,
            label="競品公司名稱",
            widget=Select2Widget(attrs={'class': 'form-control', 'id': 'coporation_control', 'placeholder': "請輸入競品的品牌名稱"})
        )


        ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")    
        PROD_df = ERP_sql.get_pd_data("select PROD_NO,PROD_NAME from PROD")
        PRODUCT_CHOICES = [('','--')] + [(prod_no, f'{prod_no}--{prod_name}') for prod_no, prod_name in PROD_df.values]
        
        self.fields['prod_number'] = forms.MultipleChoiceField(
            choices=PRODUCT_CHOICES,
            required=False,
            label="產品型號",
            widget=Select2MultipleWidget(
                attrs={'class': 'form-control', 'id': 'prod_number'})
        )

    TEST_TYPE_CHOICES = [
        ('', '--'),
        ("競品比較", "競品比較"),
        ("競品研究", "競品研究"),
        ("強度測試", "強度測試"),
        ("壽命測試", "壽命測試"),
        ("組裝測試", "組裝測試"),
        ("CAE模擬", "CAE模擬"),
        ("元貝產品系列測試", "元貝產品系列測試"),
        ("功能測試", "功能測試"),


    ]
    PROD_TYPE_CHOICES = PROD_TYPE_CHOICES

    PROVIDER_CHOICES = [
        ('是', '是'),
        ('否', '否')
    ]
    
    test_type = forms.ChoiceField(
        choices=TEST_TYPE_CHOICES,
        label="測試類別",
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'test_type'})
    )
    
    test_reason = forms.CharField(
        label="測試原因",        
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'test_reason'})
    )



    prod_type = forms.ChoiceField(
        choices=PROD_TYPE_CHOICES,
        required=False,
        label="產品類別",
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'prod_type'})
    )
    

    
    
    Compet_prod_number = forms.CharField(        
        required=False,
        label="競品型號",
        widget=forms.TextInput(
            attrs={'class': 'form-control mt-2', 'placeholder': '請輸入競品的型號，如有多個型號請用逗號分隔，EX:(TGY-338、TGY-556)'}
        )
    )


    
    remark = forms.CharField(
        label="備註",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'remark'})
    )
    
    # 使用規格確認書的选择字段
    sample_provider = forms.ChoiceField(
        choices=PROVIDER_CHOICES,
        widget=forms.RadioSelect(),
        label='樣品提供'
    )
    
    sample_num = forms.IntegerField(
        label="樣品數量",
        required=False,
        widget=forms.NumberInput(
           attrs={'min': 1, 'step': 1,'class': 'form-control',})
    )
    
    if_destroy = forms.ChoiceField(
        choices=PROVIDER_CHOICES,
        required=False,
        widget=forms.RadioSelect(),
        label='是否可破壞'
    )

    if_destroy_remark = forms.CharField(
        label="原因",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'if_destroy_remark'})
    )
    if_back = forms.ChoiceField(
        choices=PROVIDER_CHOICES,
        widget=forms.RadioSelect(),
        required=False,
        label='是否歸還提供者'
    )

    if_back_remark = forms.CharField(
        label="原因",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'if_back_remark'})
    )

    estimated_completion_date = forms.DateField(
        label="預計完成日期",
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}),
    )

    Exception_date = forms.DateField(
        label="期望繳交日期",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}),
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
            attrs={'class': 'form-control', 'id': 'attachment6'})
    )
    attachment8 = forms.FileField(
        label="附件8",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment6'})
    )
    attachment9 = forms.FileField(
        label="附件9",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment6'})
    )
    attachment10 = forms.FileField(
        label="附件10",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment6'})
    )

    if_ER_remark = forms.CharField(
        label="實驗室備註",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'if_ER_remark'})
    )

class PartApprovalNotificationForm(forms.Form):
    ERP_sql = SQL_operate.DB_operate(sqltype="YBIT")    
    PROD_df = ERP_sql.get_pd_data("select PROD_NO,PROD_NAME from PROD")
    PRODUCT_CHOICES = [('','--')] + [(prod_no, f'{prod_no}--{prod_name}') for prod_no, prod_name in PROD_df.values]

    FACT_df = ERP_sql.get_pd_data("select FACT_NO,FACT_NA,CONT_NO from FACT")

    FACT_NUMBER_CHOICES = [
        (i, i) for i in FACT_df['FACT_NO'] + ' ' + FACT_df['FACT_NA'].to_list()]

    SOURCE_CHOICES = [
        ("","--"),
        ("新開發","新開發"),
        ("設計變更單","設計變更單"),
        ("更換廠商","更換廠商"),
        ("非設變開修模","非設變開修模"),
    ]

    IF_GOOD_CHOICES = [
        ("","--"),
        ("合格","合格"),
        ("不合格","不合格"),
    ]

    OPEN_CHOICES = [
        ("","--"),
        ("開立","開立"),
        ("不開立","不開立"),
    ]
    prod_number = forms.ChoiceField(
        choices=PRODUCT_CHOICES,
        label="零件料號",
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'prod_number'})
    )

    version = forms.CharField(
        label="版次", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    model = forms.CharField(
        label="型號", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )
    
    send_sample_date = forms.DateField(
        label="送樣日期",
        initial=timezone.now().date,
        widget=forms.DateInput(format=('%Y-%m-%d'),
                               attrs={'type': 'date', 'class': 'form-control'}),
    )

    fact_number = forms.ChoiceField(
        choices=FACT_NUMBER_CHOICES,
        label="廠商名稱",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'fact_number'})
    )
    
    fact_prod_number = forms.CharField(
        label="廠商零件料號",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    source_type = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        label="需求來源",        
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'source_type'})
    )

    resource_no = forms.CharField(
        label="來源單號(選填)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )


    size = forms.ChoiceField(
        choices=IF_GOOD_CHOICES,
        label="尺寸(游標卡尺)",
        required=False,        
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'size'})
    )
    appearance = forms.ChoiceField(
        choices=IF_GOOD_CHOICES,
        label="外觀(投影機)",
        required=False,        
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'appearance'})
    )

    experiment_open = forms.ChoiceField(
        choices=OPEN_CHOICES,
        label="實驗測試申請單(開立)",       
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'experiment_open'})
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



class SampleConfirmationForm(forms.Form):
    sql = SQL_operate.DB_operate(sqltype="YBIT")
    CUST_df = sql.get_pd_data("select CUST_NO,CUST_NA,CONT_NO from CUST")

    CUSTOMER_NUMBER_CHOICES = [
        (i, i) for i in CUST_df['CUST_NO'] + ' ' + CUST_df['CUST_NA'].to_list()]

    SAMPLE_TYPE_CHOICES = [
        ("塑膠模", "塑膠模"),
        ("沖壓模", "沖壓模"),
        ("鍛造", "鍛造"),
        ("壓鑄模", "壓鑄模"),
        ("鋁擠模", "鋁擠模"),
        ("脫蠟模", "脫蠟模"),
        ("鋁重鑄", "鋁重鑄"),
        ("成品", "成品"),
    ]
    QUALIFIED_CHOICES = [
        ('合格', '合格'),
        ('不合格', '不合格')
    ]

    filters_form = Form.objects.filter(form_name='出圖依賴書')

    MOTHER_FORM_CHOICES = [(each_form.form_id,
                            each_form.form_id + '  ' + each_form.data.get('newProductNumber','') + '  ' + each_form.applicant) for each_form in filters_form]

    FILE_NO_CHOICES = [
        ("YB-0016", "YB-0016")
    ]
    iso_file_no = forms.ChoiceField(
        label="文件編號(ISO)",
        choices=FILE_NO_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'iso_file_no'}),
    )

    marchine_model = forms.CharField(
        label="機種", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    sample_order_number = forms.CharField(
        label="樣品訂單號碼(選填)",
         required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    customer_number = forms.ChoiceField(
        choices=CUSTOMER_NUMBER_CHOICES,
        label="客戶名稱(選填)",
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    resource_no = forms.ChoiceField(
        choices=MOTHER_FORM_CHOICES,
        label="來源單號(選填)",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'resource_no'})
    )

    sample_type = forms.ChoiceField(
        choices=SAMPLE_TYPE_CHOICES,
        label="樣品型態",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'sample_type'})
    )

    othersample_type = forms.CharField(
        label="其他樣品型態",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    version = forms.CharField(
        label="樣品圖面及版本", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    # 使用規格確認書的选择字段
    Function_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='功能<使用規格確認書>開發'
    )

    # 設計尺寸比對的选择字段
    design_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='設計尺寸比對-開發'
    )

    smoothness_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='順暢度'
    )
    noise_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='異音'
    )
    gap_check_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='間隙檢查'
    )

    strength_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='強度'
    )
    assembly_method_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='組裝方式'
    )

    adjustment_method_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='調整方式'
    )

    processing_manufacturability_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='加工可製造性'
    )
    
    plastic_material_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='塑膠材質'
    )
    exterior_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='外觀'
    )
    carry_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='搬運'
    )
    durability_test_discussion_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='耐久測試討論'
    )
    cost_review_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='成本再檢討'
    )
    easy_replacement_items_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='易更換物品之便利性'
    )
    oil_glue_is_qualified = forms.ChoiceField(
        required=False,
        choices=QUALIFIED_CHOICES,
        widget=forms.RadioSelect(),
        label='上油上膠'
    )
    content = forms.CharField(
        label="測試內容與結果",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'content'})
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