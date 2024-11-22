from django import forms
from Company.models import CustomUser, Form
from django_select2.forms import Select2Widget
from Database import SQL_operate
from django.utils import timezone



class AssetDataForm(forms.Form):
    asset_id = forms.CharField(
        label="財產編號", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    ) # 手動輸入
    
    asset_type = forms.CharField(
        label="資產類型", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=500,
    ) # choice
    
    
    item = forms.CharField(max_length=100, label="Item")  # 項目 # 品名 # 動
    amount = forms.DecimalField(max_digits=12, decimal_places=2, label="Amount")  # 金額 # 手動
    acquisition_date = forms.DateField(label="Acquisition Date")  # 取得日期 # 手動
    disposal_reason = forms.CharField(max_length=100, label="Disposal Reason")  # 報廢原因 # 手動