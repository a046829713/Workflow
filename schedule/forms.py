from django import forms
from django.utils.translation import gettext_lazy as _
from pypinyin import pinyin, lazy_pinyin
from schedule.models import Event, Occurrence, Visitor
from schedule.widgets import ColorInput
from django_select2.forms import Select2Widget
from Company.models import Form, CustomUser
from django_select2.forms import Select2TagWidget


# 可以自訂義widget,用於時間顯示
class DateTimeInputWithIcon(forms.DateTimeInput):
    template_name = 'widgets/datetime_input_with_icon.html'


class SpanForm(forms.ModelForm):
    start = forms.DateTimeField(
        label=_("起始時間"),
        widget=DateTimeInputWithIcon(
            attrs={'class': 'flatpickr', 'id': "start_time"},
        ),
        help_text=_("選擇開始日期和時間")
    )
    end = forms.DateTimeField(
        label=_("結束時間"),
        widget=DateTimeInputWithIcon(
            attrs={'class': 'flatpickr', 'id': "end_time"},
        ),
        help_text=_("結束時間必須要比開始時間晚")
    )

    def clean(self):
        if "end" in self.cleaned_data and "start" in self.cleaned_data:
            if self.cleaned_data["end"] <= self.cleaned_data["start"]:
                raise forms.ValidationError(
                    _("注意，結束時間必須要比開始時間晚!!")
                )
        return self.cleaned_data


class EventForm(SpanForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 从 kwargs 中提取 user
        super().__init__(*args, **kwargs)

    FROM_CHIOCES = [(_form.form_id, _form.form_id)
                    for _form in Form.objects.filter(form_name='實驗測試申請單')]

    title = forms.CharField(
        label=_("事件標題"),
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'form-control'}),
    )

    color_event = forms.ChoiceField(
        choices=[
            ('#EAEAEA', '莫蘭迪白'),  # 柔和的灰白色
            ('#4A4A4A', '莫蘭迪黑'),  # 柔和的灰黑色
            ('#A28F82', '莫蘭迪紅'),  # 柔和的灰紅色
            ('#8DA19B', '莫蘭迪綠'),  # 柔和的灰綠色
            ('#8994AC', '莫蘭迪藍'),  # 柔和的灰藍色
            ('#D4CE98', '莫蘭迪黃'),  # 柔和的灰黃色
            ('#CC9966', '莫蘭迪橙'),  # 柔和的灰橙色
            ('#A294A6', '莫蘭迪紫'),  # 柔和的灰紫色
            ('#A0C0BF', '莫蘭迪青'),  # 柔和的灰青色
            ('#E8C7D1', '莫蘭迪粉紅'),  # 柔和的灰粉紅色
        ],
        label="顯示顏色",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label=_("事件描述及備註"),
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    form_id = forms.ChoiceField(
        choices=FROM_CHIOCES,
        label="表單號碼",
        required=False,
        widget=Select2Widget(
            attrs={'class': 'form-control', 'id': "user_chose_id"})
    )

    class Meta:
        model = Event
        exclude = ("creator", "created_on", "calendar", "rule",
                   "end_recurring_period", "form_without_view")


class EventVisitForm(EventForm):
    form_without_view = forms.ChoiceField(
        choices=[],
        label="拜訪者資料(必填)",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )


class VisitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 从 kwargs 中提取 user
        super(VisitForm, self).__init__(*args, **kwargs)
        if user:
            # 根据需要选择显示用户的哪部分信息
            self.fields['interviewee_name'].initial = user.FullName

    company_id = forms.CharField(
        label=_("廠商或公司名稱"),
        required=True,
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'form-control'}),
    )

    visitor_name = forms.CharField(
        label=_("拜訪者名稱"),
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'form-control'}),
    )

    purpose = forms.ChoiceField(
        label=_("事由"),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        choices=[
            ("送貨", "送貨"),
            ("洽公", "洽公"),
            ("拜訪", "拜訪"),
            ("維修", "維修"),
            ("上課", "上課"),
            ("施工", "施工"),
            ("稽核/驗廠", "稽核/驗廠"),
        ]
    )

    number_of_visitors = forms.IntegerField(
        label="人數",
        min_value=1,  # 设置最小值为1，禁止0及以下
        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    interviewee_name = forms.CharField(
        label=_("受訪者名稱"),
        widget=forms.TextInput(
            attrs={'type': 'text',
                   'class': 'form-control',
                   'readonly': 'readonly', }),
    )

    tellphone_number = forms.IntegerField(
        label=_("分機號碼"),
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Visitor
        fields = '__all__'  # 使用 '__all__' 自動包含所有模型字段
        exclude = ("creator", "company_name", 'slug')


class OccurrenceForm(SpanForm):
    class Meta:
        model = Occurrence
        exclude = ("original_start", "original_end", "event", "cancelled")


class EventAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Event
        widgets = {"color_event": ColorInput}
