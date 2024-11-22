from django import forms
from Company.models import CustomUser, Form
from workFlow.Appsettings import FORM_INFOMATION
from django.utils import timezone
from django_select2.forms import Select2Widget, Select2MultipleWidget


def get_MOTHER_FORM_CHOICES(if_id=True):
    check_map = {}

    filters_form = Form.objects.filter(form_name='職務說明書', result='結案')

    # 判斷先後順序
    for each_form in filters_form:
        job_title = each_form.data['job_title_select']
        if job_title in check_map:
            if each_form.form_id[3:11] > check_map[job_title]:
                check_map[job_title] = each_form.form_id[3:11]
        else:
            check_map[job_title] = each_form.form_id[3:11]

    # 需要判斷使用者的部門,然後根據使用者的部門去把轄下部門給抓出來

    if if_id:
        return [('', '--')] + [(each_form.form_id, each_form.form_id + '/' + each_form.data['job_title_select']) for each_form in filters_form]
    else:
        return [('', '--')] + [(each_form.data['job_title_select'], each_form.data['job_title_select']) for each_form in filters_form]


class LanguageAbilityForm(forms.Form):
    ABILITY = [
        ('', '程度'),
        ('不需', '不需'),
        ('略懂', '略懂'),
        ('中等', '中等'),
        ('精通', '精通')
    ]

    language = forms.ChoiceField(
        label="語文條件",
        choices=[('', '請選擇'), ('英文', '英文'), ('中文', '中文'),
                 ('日文', '日文'), ('西班牙文', '西班牙文'), ('德文', '德文')],
        widget=forms.Select(attrs={'class': 'form-select mb-2'}),
        required=False)

    listen = forms.ChoiceField(
        choices=ABILITY,
        widget=forms.Select(attrs={'class': 'form-select me-3'}),
        required=False)

    speak = forms.ChoiceField(
        choices=ABILITY,
        widget=forms.Select(attrs={'class': 'form-select me-3'}),
        required=False)

    read = forms.ChoiceField(
        choices=ABILITY,
        widget=forms.Select(attrs={'class': 'form-select me-3'}),
        required=False)

    write = forms.ChoiceField(
        choices=ABILITY,
        widget=forms.Select(attrs={'class': 'form-select me-3'}),
        required=False)


class JobResponsibilityForm(forms.Form):
    TIME_FREQUENCY_CHOICES = FORM_INFOMATION['TIME_FREQUENCY_CHOICES']
    job_function_and_responsibilities_time_estimation = forms.CharField(
        label="列出職務重要的功能及責任,並估計所占用的時間比例",
        widget=forms.Textarea(attrs={'class': 'form-control job_responsibilities_time', 'rows': '3'}))

    work_hours_percentage = forms.IntegerField(
        label="工作時數占比%:",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control work_hours_input'}))

    time_frequency = forms.ChoiceField(
        label="頻率(日/月/年):",
        choices=TIME_FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select time_frequency'}))


class ToolForm(forms.Form):
    first_level = forms.ChoiceField(choices=[], required=False, widget=Select2Widget(
        attrs={'class': 'form-control first_level'}))  # 請自行填充選項
    second_level = forms.ChoiceField(choices=[], required=False, widget=Select2Widget(
        attrs={'class': 'form-control second_level'}))
    third_level = forms.ChoiceField(choices=[], required=False, widget=Select2Widget(
        attrs={'class': 'form-control third_level'}))


class WorkSkillForm(forms.Form):
    skill_first_level = forms.ChoiceField(choices=[], required=False, widget=Select2Widget(
        attrs={'class': 'form-control skill_first_level'}))  # 請自行填充選項
    skill_second_level = forms.ChoiceField(choices=[], required=False, widget=Select2Widget(
        attrs={'class': 'form-control skill_second_level'}))
    skill_third_level = forms.ChoiceField(choices=[], required=False, widget=Select2Widget(
        attrs={'class': 'form-control skill_third_level'}))


class PersonnelAdditionApplicationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PersonnelAdditionApplicationForm, self).__init__(*args, **kwargs)
        # job_description 原本的命名,但是為了記錄母表要改成統一名稱resource_no
        MOTHER_FORM_CHOICES = get_MOTHER_FORM_CHOICES()
        self.fields['resource_no'] = forms.ChoiceField(
            choices=MOTHER_FORM_CHOICES,
            label="職務說明書",
            widget=Select2Widget(attrs={'class': 'form-control'})
        )

        self.fields['add_job_title'] = forms.ChoiceField(
            choices=get_MOTHER_FORM_CHOICES(if_id=False),
            label="增補職稱",
            widget=Select2Widget(attrs={'class': 'form-control'})
        )

    CORPORATE_SECTOR_CHOICES = FORM_INFOMATION['CORPORATE_SECTOR_CHOICES']
    UNIT_CHOICES = FORM_INFOMATION['UNIT_CHOICES']
    DEPARTMENT_CHOICES = FORM_INFOMATION['DEPARTMENT_CHOICES']
    GROUP_CHOICES = FORM_INFOMATION['GROUP_CHOICES']
    LICENSE_CHOICES = FORM_INFOMATION['LICENSE_CHOICES']
    EDUCATION_LEVEL_CHOICES = FORM_INFOMATION['EDUCATION_LEVEL_CHOICES']
    DEPARTMENT_SCHOOL_CHOICES = FORM_INFOMATION['DEPARTMENT_SCHOOL_CHOICES']
    WORK_EXPERIENCE_CHOICES = FORM_INFOMATION['WORK_EXPERIENCE_CHOICES']
    EDUCATION_LEVEL_LIMIT_CHOICES = FORM_INFOMATION['EDUCATION_LEVEL_LIMIT_CHOICES']

    GENDER_CHOICES = [
        ('', "--"),
        ('男', '男'),
        ('女', '女'),
        ('不拘', '不拘'),
    ]

    AGE_CHOICES = [
        ('', "--"),
        ('不拘', '不拘'),
        ('年齡限制', '年齡限制'),
    ]

    RESPONSIBILITY_CHOICES = [
        ('', '--'),
        ("不須負擔管理責任", "不須負擔管理責任"),
        ("4人以下", "4人以下"),
        ("5-8人", "5-8人"),
        ("9-12人", "9-12人"),
        ("13人以上", "13人以上"),
        ("人數未定", "人數未定"),
    ]

    WORK_YEAR_CHOICES = [
        ('', '--'),
        ('1年以上', '1年以上'),
        ('2年以上', '2年以上'),
        ('3年以上', '3年以上'),
        ('4年以上', '4年以上'),
        ('5年以上', '5年以上'),
        ('6年以上', '6年以上'),
        ('7年以上', '7年以上'),
        ('8年以上', '8年以上'),
        ('9年以上', '9年以上'),
        ('10年以上', '10年以上'),
    ]
    corporate_sector = forms.ChoiceField(
        label="申請單位",
        choices=CORPORATE_SECTOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))

    gender = forms.ChoiceField(
        label="性別",
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))

    age = forms.ChoiceField(
        label="年齡",
        choices=AGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'age_Department'}))

    age_input = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'mt-2 me-3 form-control', 'id': 'age_Department_area', 'placeholder': '請輸入年齡:限幾歲以下'}))

    licenses = forms.MultipleChoiceField(
        label="持有駕照",
        choices=LICENSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False)

    custom_education_level = forms.MultipleChoiceField(
        label="學歷",
        choices=EDUCATION_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    department_school = forms.ChoiceField(
        label="科系要求",
        choices=DEPARTMENT_SCHOOL_CHOICES,
        widget=forms.RadioSelect())

    custom_department = forms.CharField(
        label="其他科系",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': '請輸入科系全名'}))

    work_experience = forms.ChoiceField(
        label="經歷職務年資",
        choices=WORK_EXPERIENCE_CHOICES,
        widget=forms.RadioSelect())

    job_title = forms.CharField(
        label="職務名稱",
        required=False,
        widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'form-control mt-2', 'id': 'job_title', 'placeholder': '請輸入職務名稱'}))

    work_years = forms.ChoiceField(
        label="職務年資",
        choices=WORK_YEAR_CHOICES,
        widget=forms.Select(
            attrs={'style': 'display: none;', 'class': 'form-select mt-2', 'id': 'work_years'}),
        required=False)

    school_knowledge = forms.CharField(
        label="學校知識",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'school_knowledge', 'rows': '3'}))

    work_knowledge = forms.CharField(
        label="業界知識/經驗",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'work_knowledge', 'rows': '3'}))

    work_skill = forms.CharField(
        label="工作專業技能",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'work_skill', 'rows': '3'}))

    certificates = forms.CharField(
        label="執照/證照",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'certificates', 'rows': '3'}))

    additional_notes = forms.CharField(
        label="其他備註",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'additional_notes', 'rows': '3'}))

    outside_add_job_title = forms.CharField(
        label="對外增補職稱",
        max_length=10,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'outside_add_job_title'})
    )

    add_people = forms.IntegerField(
        label="增補人數",
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'id': 'add_people'})
    )

    ADD_PEOPLE_REASON_CHOICES = [
        ('', "--"),
        ('擴大編制', '擴大編制'),
        ('儲備人力', '儲備人力'),
        ('短期需求', '短期需求'),
        ('離職遞補', '離職遞補'),
        ('其他', '其他'),
    ]

    add_people_reason_choice = forms.ChoiceField(
        label="增補原因",
        choices=ADD_PEOPLE_REASON_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-control me-3', 'id': 'add_people_reason_choice'})
    )

    add_people_reason = forms.CharField(
        widget=forms.TextInput(attrs={
                               'class': 'form-control me-3', 'id': 'add_people_reason', 'placeholder': '說明原因:'})
    )

    short_term_duration = forms.CharField(
        label="短期時長",
        required=False,
        widget=forms.TextInput(attrs={
                               'class': 'form-control me-3', 'id': 'short_term_duration', 'placeholder': '請輸入所需時間:'})
    )

    unit_configuration = forms.FileField(
        label="單位人員配置圖",
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'unit_configuration'})
    )

    interview_questions = forms.FileField(
        label="面談問題表與甄選試題測驗卷",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'interview_questions'})
    )
    other_documents = forms.FileField(
        label="其他文件",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'other_documents'})
    )

    work_content = forms.CharField(
        label="對外刊登之工作內容與職務說明",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'workContent', 'rows': '8'}),

    )

    minimum_salary = forms.CharField(
        label="最低薪資",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'minSalary'}),

    )

    maximum_salary = forms.CharField(
        label="最高薪資",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'maxSalary'}),

    )

    management_responsibility = forms.ChoiceField(
        label="管理責任",
        choices=RESPONSIBILITY_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'managementResponsibility'}),
    )

    work_outside = forms.ChoiceField(
        label="是否需要出差",
        choices=[
            ('', '--'),
            ("不需要出差", "不需要出差"),
            ("需出差", "需出差"),
        ],
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'workOutside'}),
    )

    work_ability = forms.IntegerField(
        label="靈活工作",
        widget=forms.NumberInput(
            attrs={'type': 'range', 'min': 1, 'max': 3, 'step': 1})
    )
    industry_experience = forms.IntegerField(
        label="業界經驗",
        widget=forms.NumberInput(
            attrs={'type': 'range', 'min': 1, 'max': 3, 'step': 1})
    )

    industry_connections = forms.IntegerField(
        label="業界人脈",
        widget=forms.NumberInput(
            attrs={'type': 'range', 'min': 1, 'max': 3, 'step': 1})
    )
    industry_knowledge = forms.IntegerField(
        label="業界知識",
        widget=forms.NumberInput(
            attrs={'type': 'range', 'min': 1, 'max': 3, 'step': 1})
    )
    school_knowledge_select = forms.IntegerField(
        label="學校相關知識",
        widget=forms.NumberInput(
            attrs={'type': 'range', 'min': 1, 'max': 3, 'step': 1})
    )
    business_knowledge = forms.IntegerField(
        label="企業知識",
        widget=forms.NumberInput(
            attrs={'type': 'range', 'min': 1, 'max': 3, 'step': 1})
    )


class RecruitmentInterviewEvaluationForm(forms.Form):
    CORPORATE_SECTOR_CHOICES = FORM_INFOMATION['CORPORATE_SECTOR_CHOICES']

    ALLUSER = CustomUser.objects.all()

    # 人資面試官
    HRUSER = [('', '--')] + [(eachuser.username, eachuser.username + ' ' + eachuser.FullName)
                             for eachuser in ALLUSER if eachuser.username != 'Administrator' and eachuser.groups.filter(name='人資課').exists()]
    HRUSER = sorted(HRUSER, key=lambda x: x[0])

    # 單位面試官
    NOHRUSER = [(eachuser.username, eachuser.username + ' ' + eachuser.FullName)
                for eachuser in ALLUSER if eachuser.is_active and eachuser.username != 'Administrator']

    NOHRUSER = sorted(NOHRUSER, key=lambda x: x[0])

    INTERVIEW_RESULT = [
        ("錄取", '錄取'),
        ("安排複試", '安排複試'),
        ("未錄取", '未錄取'),
    ]

    NORMAL_CHOICES = [
        ('合適', '合適'),
        ('不合適', '不合適'),
    ]
    NORMAL_CHOICES_TWO = [
        ('合適', '合適'),
        ('不合適', '不合適'),
        ('對本職務無妨', '對本職務無妨'),
    ]
    NORMAL_CHOICES_THREE = [
        ('可滿足職務獨立作業', '可滿足職務獨立作業'),
        ('不足,但內部有資源可以做教育訓練', '不足,但內部有資源可以做教育訓練'),
        ('不足,且無法訓練', '不足,且無法訓練'),
    ]
    NORMAL_CHOICES_FOUR = [
        ('偏低', '偏低'),
        ('中等', '中等'),
        ('偏高', '偏高'),
    ]
    NORMAL_CHOICES_FIVE = [
        ('基本,對知識追求較低,僅對興趣相關知識稍有了解', '基本,對知識追求較低,僅對興趣相關知識稍有了解'),
        ('進階,對知識有較高興趣,主動學習各領域知識', '進階,對知識有較高興趣,主動學習各領域知識'),
        ('專業,在特定領域內具有深入專業知識和技能', '專業,在特定領域內具有深入專業知識和技能'),
        ('創新,在現有知識基礎上進行創新和探索,發現新知識和觀念', '創新,在現有知識基礎上進行創新和探索,發現新知識和觀念'),
    ]

    NORMAL_CHOICES_SIX = [
        ('具備目前公司所需有效人脈可運用', '具備目前公司所需有效人脈可運用'),
        ('具備人脈,但目前無妨', '具備人脈,但目前無妨'),
        ('無人脈,但對本職無妨', '無人脈,但對本職無妨'),
        ('無人脈,在工作發展上可能會有所受限', '無人脈,在工作發展上可能會有所受限'),
    ]

    UNIT_CHOICES = FORM_INFOMATION['UNIT_CHOICES']
    DEPARTMENT_CHOICES = FORM_INFOMATION['DEPARTMENT_CHOICES']
    GROUP_CHOICES = FORM_INFOMATION['GROUP_CHOICES']

    user_name = forms.CharField(
        label="應徵者姓名", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=100,
    )

    interviewjobvacancies = forms.CharField(label="面試職缺", widget=forms.TextInput(
        attrs={'class': 'form-control'}), max_length=100)

    corporate_sector = forms.ChoiceField(
        label="需求單位",
        choices=CORPORATE_SECTOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))

    interview_date = forms.DateField(
        label="面試日期",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}),

    )
    character_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )
    character_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    character_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES,
        widget=forms.RadioSelect,
    )

    intent_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    intent_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    intent_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES,
        widget=forms.RadioSelect,
    )

    educational_backgroud_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    educational_backgroud_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    educational_backgroud_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES_TWO,
        widget=forms.RadioSelect,
    )

    Industry_knowledge_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    Industry_knowledge_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    Industry_knowledge_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES_THREE,
        widget=forms.RadioSelect,
    )

    person_self_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    person_self_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    person_self_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES_FOUR,
        widget=forms.RadioSelect,
    )

    learning_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    learning_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    learning_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES_FIVE,
        widget=forms.RadioSelect,
    )

    contacts_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    contacts_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    contacts_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES_SIX,
        widget=forms.RadioSelect,
    )

    behavior_behavior = forms.CharField(
        label='行為事例:(面試者所述之紀錄)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    behavior_control = forms.CharField(
        label='評語(面試官討論評估結論)',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )

    )

    behavior_option = forms.ChoiceField(
        label="小結",
        choices=NORMAL_CHOICES,
        widget=forms.RadioSelect,
    )

    interview_result = forms.ChoiceField(
        choices=INTERVIEW_RESULT,
        label='面試結果',
        widget=forms.RadioSelect(
            attrs={'class': 'form-check-input'}
        ), error_messages={
            'required': '請選擇一個選項。',
        }
    )

    hr_interviewer = forms.ChoiceField(
        label="人資面試官",
        widget=forms.Select(attrs={'class': 'form-select'}),
        choices=HRUSER,
        required=False
    )

    unit_interviewer = forms.MultipleChoiceField(
        label="單位面試官",
        choices=NOHRUSER,
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select select2-multiple'})
    )


class jobDescriptionForm(forms.Form):
    CORPORATE_SECTOR_CHOICES = FORM_INFOMATION['CORPORATE_SECTOR_CHOICES']

    LICENSE_CHOICES = FORM_INFOMATION['LICENSE_CHOICES']
    EDUCATION_LEVEL_CHOICES = FORM_INFOMATION['EDUCATION_LEVEL_CHOICES']
    EDUCATION_LEVEL_LIMIT_CHOICES = FORM_INFOMATION['EDUCATION_LEVEL_LIMIT_CHOICES']
    JOB_DEPARTMENT_SCHOOL_CHOICES = FORM_INFOMATION['JOB_DEPARTMENT_SCHOOL_CHOICES']
    CERTIFICATES_CHOICES = FORM_INFOMATION['CERTIFICATES_CHOICES']
    JOB_WORK_EXPERIENCE_CHOICES = FORM_INFOMATION['JOB_WORK_EXPERIENCE_CHOICES']
    OCCUPATION_CATEGORY_CHOICES = FORM_INFOMATION['OCCUPATION_CATEGORY_CHOICES']
    CAREER_LEVEL_CHOICES = FORM_INFOMATION['CAREER_LEVEL_CHOICES']
    JOB_TITLE_CHOICES = FORM_INFOMATION['JOB_TITLE_CHOICES']

    WORK_YEAR_CHOICES = [
        ('', '--'),
        ('1年以上', '1年以上'),
        ('2年以上', '2年以上'),
        ('3年以上', '3年以上'),
        ('4年以上', '4年以上'),
        ('5年以上', '5年以上'),
        ('6年以上', '6年以上'),
        ('7年以上', '7年以上'),
        ('8年以上', '8年以上'),
        ('9年以上', '9年以上'),
        ('10年以上', '10年以上'),
    ]

    corporate_sector = forms.MultipleChoiceField(
        label="所屬單位",
        choices=CORPORATE_SECTOR_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple'}))

    job_title_select = forms.CharField(
        label="職務名稱",
        max_length=10,  # 添加這一行設定最大字符長度為10
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請填寫'}))

    Occupation_category = forms.ChoiceField(
        label="職系",
        choices=OCCUPATION_CATEGORY_CHOICES,
        widget=forms.RadioSelect())

    main_duty = forms.CharField(
        label="主要職責",
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'main_duty', 'rows': '3', 'placeholder': '請用一至兩句話闡明本職務的職責'}))

    career_level = forms.ChoiceField(
        label="職等",
        choices=CAREER_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))

    licenses = forms.MultipleChoiceField(
        label="持有駕照",
        choices=LICENSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False)

    education_level = forms.ChoiceField(
        label="教育程度",
        choices=EDUCATION_LEVEL_LIMIT_CHOICES,
        widget=forms.RadioSelect,
    )

    custom_education_level = forms.MultipleChoiceField(
        label="自訂義教育程度",
        choices=EDUCATION_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    department_school = forms.ChoiceField(
        label="科系要求",
        choices=JOB_DEPARTMENT_SCHOOL_CHOICES,
        widget=forms.RadioSelect())

    custom_department = forms.CharField(
        label="其他科系",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': '請輸入科系全名'}))

    certificates = forms.ChoiceField(
        label="專業證照/執照",
        choices=CERTIFICATES_CHOICES,
        widget=forms.RadioSelect())

    custom_certificates = forms.CharField(
        label="其他證照",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': '請輸入'}))

    work_experience = forms.ChoiceField(
        label="相關工作經驗",
        choices=JOB_WORK_EXPERIENCE_CHOICES,
        widget=forms.RadioSelect())

    job_title = forms.CharField(
        label="職務名稱",
        required=False,
        widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'form-control mt-2', 'id': 'job_title', 'placeholder': '請輸入職務名稱'}))

    work_years = forms.ChoiceField(
        label="職務年資",
        choices=WORK_YEAR_CHOICES,
        widget=forms.Select(
            attrs={'style': 'display: none;', 'class': 'form-select mt-2', 'id': 'work_years'}),
        required=False)

    has_management = forms.ChoiceField(
        label="是否具備管理職",
        required=False,
        choices=[('是', '是'), ('否', '否')],
        widget=forms.RadioSelect(
            attrs={'class': 'form-control', 'id': 'has_management'}),
    )

    management_responsibility = forms.IntegerField(
        label="管理責任",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'management_responsibility', 'placeholder': '轄下管理人數'}))

    communication_internal_external_up = forms.CharField(
        label="對上",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'communication_internal_external_up', 'placeholder': '角色或單位'})
    )
    communication_internal_external_down = forms.CharField(
        label="對下",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'communication_internal_external_down', 'placeholder': '角色或單位'})
    )
    communication_internal_external_inner = forms.CharField(
        label="對內",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'communication_internal_external_inner', 'placeholder': '角色或單位'})
    )
    communication_internal_external_outer = forms.CharField(
        label="對外",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'communication_internal_external_outer', 'placeholder': '角色或單位'})
    )


LanguageAbilityFormset = forms.formset_factory(LanguageAbilityForm, extra=1)
JobResponsibilityFormSet = forms.formset_factory(
    JobResponsibilityForm, extra=1)
ToolFormSet = forms.formset_factory(ToolForm, extra=1)
SkillFormSet = forms.formset_factory(WorkSkillForm, extra=1)


class AccessControlPermissionForm(forms.Form):
    APPLICATIONCATEGORY_CHOICES = [
        ('', '--'),
        ('初次申請門禁密碼', '初次申請門禁密碼'),
        ('初次申請門禁卡片', '初次申請門禁卡片'),
        ('門禁卡片遺失補發', '門禁卡片遺失補發'),
        ('已有門禁密碼或卡片，新增權限', '已有門禁密碼或卡片，新增權限'),
    ]
    REQUESTFORACCESS_CHOICES = [
        ('', '--'),
        ('大廳辦公室', '大廳辦公室'),
        ('電腦機房', '電腦機房'),
        ('董事長辦公室', '董事長辦公室'),
        ('總經理辦公室', '總經理辦公室'),
        ('資料室', '資料室'),
        ('刀具室', '刀具室'),
        ('逆向設備室大門', '逆向設備室大門'),
        ('一樓乙梯', '一樓乙梯'),
        ('二樓乙梯', '二樓乙梯'),
        ('三樓乙梯', '三樓乙梯'),
        ('地下一樓甲梯', '地下一樓甲梯'),
        ('地下一樓乙梯', '地下一樓乙梯'),
        ('二樓電梯門口', '二樓電梯門口'),
        ('三樓電梯門口', '三樓電梯門口'),
        ('四樓電梯門口', '四樓電梯門口'),

    ]
    ApplicationCategory = forms.MultipleChoiceField(
        choices=APPLICATIONCATEGORY_CHOICES,
        label="申請類別(可複選)",
        widget=Select2MultipleWidget(
            attrs={'class': 'form-control', 'id': 'ApplicationCategory'})
    )

    requestforaccess = forms.MultipleChoiceField(
        choices=REQUESTFORACCESS_CHOICES,
        label="申請權限(可複選)",
        required=False,
        widget=Select2MultipleWidget(
            attrs={'class': 'form-control', 'id': 'requestforaccess'})
    )

    application_reason = forms.CharField(
        label="申請原因",
        widget=forms.Textarea(attrs={'class': 'form-control application_reason'}))


class BusinessCardRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # 可以從kwargs中提取預設值，或者在這裡直接設置
        internal_title_default = kwargs.pop(
            'internal_title_default', '預設對內職稱')  # 這裡設置預設值
        external_title_default = kwargs.pop(
            'external_title_default', '預設對外職稱')  # 這裡設置預設值
        super().__init__(*args, **kwargs)

        # 設置字段的初始值
        self.fields['Externalprofessionaltitle'].initial = external_title_default
        self.fields['Internalprofessionaltitle_display'].initial = internal_title_default
        self.fields['Internalprofessionaltitle'].initial = internal_title_default

    FAX_CHOICES = [
        ("", "--"),
        ("886-4-25335616", '886-4-25335616'),
        ("886-4-25150243", '886-4-25150243'),
        ("886-4-25159834", '886-4-25159834'),
    ]
    BOXES_CHOICES = [
        ("2", '2'),
        ("3", '3'),
        ("5", '5'),
        ("10", '10'),
        ("20", '20'),
        ("30", '30')
    ]

    english_name = forms.CharField(
        label="英文名字",
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))

    # 显示给用户看，但被禁用
    Internalprofessionaltitle_display = forms.CharField(
        label="公司職稱",
        required=False,  # 因为只是显示，所以不需要验证
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'disabled': True})
    )

    # 实际提交的值，隐藏字段
    Internalprofessionaltitle = forms.CharField(widget=forms.HiddenInput())

    Externalprofessionaltitle = forms.CharField(
        label="對外職稱",
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))

    Englishprofessionaltitle = forms.CharField(
        label="英文職稱",
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))

    ExtensionNumber = forms.IntegerField(
        label="分機號碼",
        min_value=0,
        widget=forms.NumberInput(  # 使用 NumberInput 小部件
            attrs={'class': 'form-control'}
        )
    )

    Fax = forms.ChoiceField(
        choices=FAX_CHOICES,
        label="傳真號碼",
        widget=Select2Widget(
            attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="電子郵件地址",
        initial='example@mail.ybico.com.tw',
        widget=forms.EmailInput(  # 使用 EmailInput 小部件
            attrs={'class': 'form-control'}
        ),
        help_text="請輸入您的電子郵件地址。"  # 可选的帮助文本
    )
    IF_REMAINING_CHOICES = [
        ('有', '有'),
        ('無', '無'),
    ]

    ifremainingamount = forms.ChoiceField(
        label="名片是否有剩餘數量",
        choices=IF_REMAINING_CHOICES,
        widget=forms.RadioSelect,

    )

    boxes = forms.ChoiceField(
        choices=BOXES_CHOICES,
        label="申請名片盒數(100張/盒)",
        widget=Select2Widget(
            attrs={'class': 'form-control'})
    )

    Releasedate = forms.DateField(
        label="發放日期",
        required=False,
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'})
    )

    ifRecycle = forms.CharField(
        label="是否回收舊卡片",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    Reasonforapplication = forms.CharField(
        label="申請原因",
        widget=forms.Textarea(  # 使用 NumberInput 小部件
            attrs={'class': 'form-control'}
        )
    )

    Skype_number = forms.CharField(
        label="Skype",
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

