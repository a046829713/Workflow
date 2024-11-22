from django import forms
from Company.models import CustomUser
from django_select2.forms import Select2Widget
from Database import SQL_operate
from workFlow.FormAppsettings import PROD_TYPE_CHOICES


class DrawingDependencyBookForm(forms.Form):
    ALLUSER = CustomUser.objects.all()
    ALLUSER = [(eachuser.username, eachuser.username + eachuser.FullName)
               for eachuser in ALLUSER if eachuser.username != 'Administrator' and eachuser.groups.filter(name='研發部').exists()]
    ALLUSER = [('', '--')] + ALLUSER

    DESIGN_PROCEDURE_CHOICES = [
        ("依開發程序", "依開發程序"),
        ("依設變程序", "依設變程序"),
    ]

    QuotationScheduledDate = forms.DateField(
        label="報價預定日",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}),

    )

    newProductNumber = forms.CharField(
        label="新產品編號", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    newProductName = forms.CharField(
        label="產品名稱", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    EstimatedAmount = forms.IntegerField(
        label="預估量",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'EstimatedAmount'}))

    client = forms.CharField(
        label="客戶", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    )

    drawing = forms.BooleanField(
        label="客戶是否提供圖面",
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', 'id': 'drawing'})
    )

    sample = forms.BooleanField(
        label="客戶是否提供樣品",
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', 'id': 'sample'})
    )

    design_procedure = forms.ChoiceField(
        label="設計程序",
        choices=DESIGN_PROCEDURE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'designProcedure'}),
    )

    usage = forms.CharField(
        label="用途",
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'usage'})
    )

    description = forms.CharField(
        label="說明",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'description'})
    )

    specification = forms.CharField(
        label="規格",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'specification'})
    )

    # 動態創建附件字段
    attachment_fields = ['attachment{}'.format(i) for i in range(1, 9)]
    for attachment in attachment_fields:
        locals()[attachment] = forms.FileField(
            label=f"附件{attachment[-1]}",
            required=False,
            widget=forms.ClearableFileInput(
                attrs={'class': 'form-control', 'id': attachment})
        )


class CustomerComplaintRecordForm(forms.Form):
    sql = SQL_operate.DB_operate(sqltype="YBIT")
    CUST_df = sql.get_pd_data("select CUST_NO,CUST_NA,CONT_NO from CUST")
    PROD_df = sql.get_pd_data("select PROD_NO from PROD")

    CUSTOMER_NUMBER_CHOICES = [
        (i, i)for i in CUST_df['CUST_NO'] + ' ' + CUST_df['CUST_NA'].to_list()]

    COUNTRY_CHOICES = [(i, i)for i in list(set(CUST_df['CONT_NO'].to_list()))]
    PROD_NO_CHOICES = [(i, i)for i in list(set(PROD_df['PROD_NO'].to_list()))]

    COMPLAINT_TYPE_CHOICES = [
        ("功能性", "功能性"),
        ("非功能性", "非功能性")
    ]

    customer_number = forms.ChoiceField(
        choices=CUSTOMER_NUMBER_CHOICES,
        label="客戶編號",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    Complaint_type = forms.ChoiceField(
        choices=COMPLAINT_TYPE_CHOICES,
        label="客訴類別",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        initial="US",
        label="國家",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )
    prod_no = forms.ChoiceField(
        choices=PROD_NO_CHOICES,
        label="料號",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    Complaintcontent = forms.CharField(
        label="客訴內容",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'Complaintcontent'})
    )

    internalprocessing = forms.CharField(
        label="內部處理",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'id': 'internalprocessing',
                   'placeholder': '將內部處理做一個紀錄'
                   })
    )
    externalprocessing = forms.CharField(
        label="外部處理",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'id': 'externalprocessing',
                   'placeholder': '回覆給客戶的資訊'
                   })
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
    followupafterthreemonths = forms.CharField(
        label="三個月後追蹤",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'followupafterthreemonths'})
    )

    prod_type = forms.ChoiceField(
        choices=PROD_TYPE_CHOICES,
        label="產品類別",
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': 'prod_type'})
    )
