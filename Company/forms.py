from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import RichText, Level, CustomUser
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2Widget
from django.contrib.auth.models import Group


class ChangepasswordForm(forms.Form):
    currentPassword = forms.CharField(
        label="請輸入當前用戶密碼",
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': '請輸入舊密碼'}))
    newPassword = forms.CharField(
        label="新密碼",
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': '請輸入新密碼'}))
    confirmNewPassword = forms.CharField(
        label="確認你的新密碼",
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': '確認新密碼'}))

class RichText_modelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):     
        super(RichText_modelForm, self).__init__(*args, **kwargs)        
            
    class Meta:
        model = RichText
        fields = ['content']
        
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='awesome_ckeditor'))


class LevelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    STATION_CHOICE = [
        ('核准', '核准'),
        ('確認', '確認'),
        ('駁回', '駁回'),
        ('送出', '送出'),
        ('加簽', '加簽'),
        ('退簽', '退簽'),
        ('結案', '結案'),
    ]

    STATION_MODE_CHOICES = [
        ('','--'),
        ('grab', '搶簽'),
        ('counter_sign', '會簽'),
    ]

    STATION_MANAGER_CHOICES = [
        ('applicant', '申請人'),
        ('direct_supervisor', '直屬主管'),
        ('department_head', '部級主管'),
        ('previous_level_per', '上一關負責人'),
    ]

    level_name = forms.CharField(
        label=_("請輸入流程的中文名稱:"),        
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    versionNumber = forms.CharField(
        label=_("請輸入版本號碼:(A-Z預設為版本A):"),        
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    station_name = forms.CharField(
        label=_("請輸入本站的名稱(動作的名稱):"),        
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    next_station = forms.CharField(
        label=_("請輸入下一站的名稱(動作的名稱):"),        
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    station_choice = forms.MultipleChoiceField(
        choices=STATION_CHOICE,
        label="站點選擇",
        widget=forms.CheckboxSelectMultiple
    )

    # 站點模式
    station_mode = forms.ChoiceField(
        choices=STATION_MODE_CHOICES,
        label="請選擇簽核模式",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # 關係模式
    station_manager = forms.ChoiceField(
        choices=STATION_MANAGER_CHOICES,
        label="簽核負責人(單人模式)(只允許單一個人)",
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    # 站點團體
    station_group = forms.MultipleChoiceField(
        choices= [(group.name, group.name)for group in Group.objects.all()],
        label="簽核團體(多人模式)(角色)",
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select select2-multiple'})
        
    )
    endorsement_mode = forms.ChoiceField(
        choices=STATION_MODE_CHOICES,
        label="請選擇加簽的簽核模式",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    endorsement_manager = forms.MultipleChoiceField(
        choices= [(user.username, user.FullName)for user in CustomUser.objects.all()],
        label="加簽人員",
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select select2-multiple'})
        
    )

    endorsement_group = forms.MultipleChoiceField(
        choices= [(group.id, group.name)for group in Group.objects.all()],
        label="加簽團體",
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select select2-multiple'})
    )
     
    class Meta:
        model = Level
        fields = ['level_name','versionNumber','station_name','next_station', 'station_choice', 'station_mode','station_manager','station_group'
                  ,'endorsement_mode','endorsement_manager','endorsement_group']
        exclude = ("level_id", "previous_station",'limited_time')