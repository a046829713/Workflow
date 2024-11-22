from django import forms
from Company.models import CustomUser, Form
from workFlow.Appsettings import FORM_INFOMATION
from django.utils import timezone
from django_select2.forms import Select2Widget


class AssembleWmodelForm(forms.Form):
    TRIIMPELLERSILENCER_CHOICES = [
        ('三葉輪', '三葉輪'),
        ('管塞', '管塞'),
    ]

    THREEIMPELLER_SELECT_CHOICES = [('','--'),
                                    ('附加', '附加'),
                                    ('不附加', '不附加')]

    PAPERTUBELINING_CHOICES = [
        ('','--'),
        ('37mm凸點', '37mm凸點'),

    ]

    FILMLENGTH_CHOICES = [
        ('','--'),
        ('450mm', '450mm'),
    ]

    COVERCOLOR_CHOICES = [
        ('紅', '紅'),
        ('綠', '綠'),
        ('藍', '藍'),
        ('橘', '橘'),
    ]
    COVERTAG_CHOICES = [
        ('無', '無'),
        ('XT', 'XT'),
        ('TCPA', 'TCPA'),
        ('Manuli', 'Manuli'),
        ('VMAXX', 'VMAXX'),
        ('FirstWRAP貼紙', 'FirstWRAP貼紙'),
        ('Qartner貼紙', 'Qartner貼紙'),
        ('ENO貼紙', 'ENO貼紙'),
        ('ULINE貼紙', 'ULINE貼紙'),
    ]

    NORMAL_CHOICES = [
        ('有', '有'),
        ('無', '無')
    ]

    PRODUCTNOTYPES_CHOICES = [
        ('標準款', '標準款'),
        ('輕量款', '輕量款'),
        ('組合款', '組合款'),
        ('超輕量款', '超輕量款'),
    ]

    PRODUCTNOTENSIONS_CHOICES = [
        ('', '--'),
        ('調節', '調節'),
        ('固定', '固定'),
        ('ABC', 'ABC'),

    ]



    ROLLERTYPES_CHOICES = [
        ('正反溝灰輪', '正反溝灰輪'),
        ('正反溝黑輪', '正反溝黑輪'),
        ('直溝灰輪', '直溝灰輪'),
        ('直溝黑輪', '直溝黑輪'),
    ]



    FLEXIBLETUBESTANDARDLENGTH_CHOICES = [
        ('','--'),
        ('140mm', '140mm'),
        ('155mm', '155mm'),
        ('253mm', '253mm'),
        ('420mm', '420mm'),
        ('425mm', '425mm'),
    ]
    
    HANDLECOLOR_CHOICES = [
        ('','--'),
        ('黑', '黑'),
        ('灰', '灰'),
    ]
    
    TUBECOLOR_CHOICES = [
        ('','--'),
        ('黑', '黑'),
        ('灰', '灰'),
    ]
    BENDPIPECOLOR_CHOICES= [
        ('','--'),
        ('紅黑', '紅黑'),
        ('綠黑', '綠黑'),
        ('藍黑', '藍黑'),
        ('紅灰', '紅灰'),
        ('綠灰', '綠灰'),
    ]
    
    PERCENT_CHOICES =[
        ('20%', '20%'),
        ('30%', '30%'),
        ('40%', '40%'),
        ('50%', '50%'),
        ('60%', '60%'),
    ]
    
    STRONG_CHOICES = [
        ('強', '強'),
        ('中', '中'),
        ('弱', '弱'),
       
    ]
    HANDLETYPE_CHOICES= [
        ('標準', '標準'),
        ('伸縮', '伸縮'),       
    ]
    # 紙管(膠膜) =====================================================================
    triImpellerSilencer = forms.ChoiceField(
        label="樣式",
        choices=TRIIMPELLERSILENCER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    threeimpeller_select = forms.ChoiceField(
        label="三葉輪附加紙管",
        choices=THREEIMPELLER_SELECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    papertubelining = forms.ChoiceField(
        label="紙管內俓",
        choices=PAPERTUBELINING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    filminnerdiameter= forms.ChoiceField(
        label="膠膜內徑",
        choices=[('','--')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    filmlength = forms.ChoiceField(
        label="紙管長度",
        choices=FILMLENGTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    Threeimpellerlengths = forms.ChoiceField(
        label="三葉輪長度",
        choices=[('','--')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    
    # 上下蓋 =====================================================================
    up_buttom_cover_color = forms.ChoiceField(
        label="上底蓋",
        choices=COVERCOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    down_buttom_cover_color = forms.ChoiceField(
        label="下底蓋",
        choices=COVERCOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    up_top_cover_color = forms.ChoiceField(
        label="上頂蓋",
        choices=COVERCOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    down_top_cover_color = forms.ChoiceField(
        label="下頂蓋",
        choices=COVERCOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    up_top_cover_tag = forms.ChoiceField(
        label="上頂蓋LOGO",
        choices=COVERTAG_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    down_top_cover_tag = forms.ChoiceField(
        label="下頂蓋LOGO",
        choices=COVERTAG_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    magnet = forms.ChoiceField(
        label="磁鐵",
        choices=NORMAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    productnotypes = forms.ChoiceField(
        label="鐵條款式",
        choices=PRODUCTNOTYPES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    tensions = forms.ChoiceField(
        label="鐵條張力",
        choices=PRODUCTNOTENSIONS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


    rollertypes = forms.ChoiceField(
        label="滾輪款式",
        choices=ROLLERTYPES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


    flexibletubehandlelength = forms.ChoiceField(
        label="伸縮握把露出長度",
        choices=FLEXIBLETUBESTANDARDLENGTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    
    foam_is_have = forms.ChoiceField(
        label="有無泡棉",
        choices=NORMAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    
    # 手炳握把
    handletype = forms.ChoiceField(
        label="握把樣式",
        choices=HANDLETYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    handlecolor= forms.ChoiceField(
        label="手柄握把顏色",
        choices=HANDLECOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    bendpipecolor= forms.ChoiceField(
        label="彎管顏色",
        choices=BENDPIPECOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tubecolor= forms.ChoiceField(
        label="套管顏色",
        choices=TUBECOLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    
    
    pulltheblackballis_have= forms.ChoiceField(
        label="有無拉把黑球",
        choices=NORMAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    
    percent= forms.ChoiceField(
        label="齒輪百分比",
        choices=PERCENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    strong= forms.ChoiceField(
        label="強度",
        choices=STRONG_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )