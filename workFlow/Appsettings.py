from . import DateInput
FormCodes = {
    # 在命名代碼的時候要保持3位數
    "人員增補申請表": ["人員增補申請表", "PAA", "A"],
    "招募面試評核表": ["招募面試評核表", "RIE", "A"],
    "職務說明書": ["職務說明書", "JDS", "A"],
    # "出圖依賴書": ["出圖依賴書", "DDB", "A"],
    "出圖依賴書": ["出圖依賴書", "DDB", "B"],

    # "客訴紀錄單": ["客訴紀錄單", "CCR", "A"],
    "客訴紀錄單": ["客訴紀錄單", "CCR", "B"],
    "會議記錄": ["會議記錄", "MMF", "A"],
    "品質異常單": ["品質異常單", "QAR", "A"],
    "矯正預防措施處理單": ["矯正預防措施處理單", "CAR", "A"],
    "樣品確認單": ["樣品確認單", "SLC", "A"],
    "資產報廢申請單": ["資產報廢申請單", "SAF", "A"],

    # "重工單": ["重工單", "RWF", "A"],
    "重工單": ["重工單", "RWF", "B"],

    "實驗測試申請單": ["實驗測試申請單", "ETF", "A"],
    "門禁權限申請單": ["門禁權限申請單", "ACP", "A"],
    "名片申請單": ["名片申請單", "BCR", "A"],
    "部品承認通知單": ["部品承認通知單", "PAN", "A"],
}


FORMURLS = {
    "人員增補申請表": "PersonnelAdditionApplicationForm",
    "招募面試評核表": "RecruitmentInterviewEvaluationForm",
    "職務說明書": "jobDescriptionForm",
    "出圖依賴書": "DrawingDependencyBookForm",
    "客訴紀錄單": 'CustomerComplaintRecordForm',
    "會議記錄": 'MeetingMinutesForm',
    "品質異常單": 'QualityAbnormalityReportForm',
    "矯正預防措施處理單": 'CorrectiveeActionReportForm',
    "樣品確認單": 'SampleConfirmationForm',
    "資產報廢申請單": 'AssetDataForm',
    "重工單": 'HeavyworkorderForm',
    "實驗測試申請單": 'ExperimentalTestForm',
    "門禁權限申請單": 'AccessControlPermissionForm',
    "名片申請單": 'BusinessCardRequestForm',
    "部品承認通知單": "PartApprovalNotificationForm",
    # 
}

FORMURLS_ONLYCHANGEDATA = {
    "矯正預防措施處理單": 'CorrectiveeActionReportFormOnlyChangeData',
    "品質異常單": 'QualityAbnormalityReportFormOnlyChangeData',
    "出圖依賴書": 'DrawingDependencyBookFormOnlyChangeData',
    "重工單": 'HeavyworkorderFormOnlyChangeData',
    "實驗測試申請單": 'ExperimentalTestFormOnlyChangeData',
    "客訴紀錄單": 'CustomerComplaintRecordFormOnlyChangeData',
    "職務說明書": 'jobDescriptionFormOnlyChangeData',
    "人員增補申請表": 'PersonnelAdditionApplicationFormOnlyChangeData',
}

FORMURLS_RESET = {
    "人員增補申請表": "PersonnelAdditionApplicationFormReset",
    "招募面試評核表": "RecruitmentInterviewEvaluationFormReset",
    "職務說明書": "jobDescriptionReset",
    "出圖依賴書": "DrawingDependencyBookFormReset",
    "客訴紀錄單": 'CustomerComplaintRecordFormReset',
    "會議記錄": 'MeetingMinutesFormReset',
    "品質異常單": 'QualityAbnormalityReportFormReset',
    "矯正預防措施處理單": 'CorrectiveeActionReportFormReset',
    "樣品確認單": 'SampleConfirmationFormReset',
    "資產報廢申請單": 'AssetDataFormReset',
    "重工單": 'HeavyworkorderFormReset',
    "實驗測試申請單": 'ExperimentalTestFormReset',
    "門禁權限申請單": 'AccessControlPermissionFormReset',
    "名片申請單": 'BusinessCardRequestFormReset',
    "部品承認通知單":"PartApprovalNotificationFormReset",
}


SAVE_ATTACHMENT_PATH = {
    "人員增補申請表": "PersonnelAdditionApplication",
    "招募面試評核表": "RecruitmentInterviewEvaluation",
    "職務說明書": "jobDescription",
    "出圖依賴書": "DrawingDependencyBook",
    "客訴紀錄單": 'CustomerComplaintRecord',
    "會議記錄": 'MeetingMinutes',
    "品質異常單": 'QualityAbnormalityReport',
    "矯正預防措施處理單": 'CorrectiveeActionReport',
    "樣品確認單": 'SampleConfirmation',
    "資產報廢申請單": 'AssetData',
    "重工單": 'Heavyworkorder',
    "實驗測試申請單": 'ExperimentalTest',
    "門禁權限申請單": 'AccessControlPermission',
    "名片申請單": 'BusinessCardRequest',
    "部品承認通知單":"PartApprovalNotification"
}


# 用來決定哪一些附件是要判斷的
ATTACHMENT = {
    "人員增補申請表": {
        "A": ['unit_configuration', 'interview_questions', 'other_documents']
    },
    "招募面試評核表": {
        "A": []
    },
    "職務說明書": {
        "A": []
    },
    "出圖依賴書":  {
        "A": [f'attachment{i}' for i in range(1, 9)],
        "B": [f'attachment{i}' for i in range(1, 9)]
    },
    '客訴紀錄單': {
        "A": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5', 'attachment6'],
        "B": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5', 'attachment6'],

    },
    "會議記錄": {
        "A": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5', 'attachment6']
    },
    "品質異常單": {
        "A": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5',
              'attachment6', 'attachment7', 'attachment8', 'attachment9', 'attachment10', 'attachment11', 'attachment12']
    },
    "矯正預防措施處理單": {
        "A": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5', 'attachment6']
    },
    "樣品確認單": {
        "A": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5', 'attachment6']
    },
    "資產報廢申請單": {
        "A": ['attachment1', 'attachment2', 'attachment3', 'attachment4', 'attachment5', 'attachment6']
    },
    '重工單': {
        "A": [],
        "B": []
    },
    "實驗測試申請單": {
        "A": [f'attachment{i}' for i in range(1, 11)]
    },
    '門禁權限申請單': {
        "A": []
    },
    '名片申請單': {
        "A": []
    },
    "部品承認通知單":{
        "A": [f'attachment{i}' for i in range(1, 13)]
    }
}

# 副件的翻譯名稱
ATTACHMENT_TRANSLATE = {
    "人員增補申請表": {
        "A": {
            "unit_configuration": "單位人員配置圖",
            "interview_questions": "面談問題表與甄選試題測驗卷",
            "other_documents": "其他文件",
        }
    },
    "招募面試評核表": {
        "A": {

        }
    },
    "職務說明書": {
        "A": {

        }
    },
    "出圖依賴書":  {
        "A": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6",
              'attachment7': "附件7",
              'attachment8': "附件8",
              },
        "B": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6",
              'attachment7': "附件7",
              'attachment8': "附件8",
              }
    },
    '客訴紀錄單': {
        "A": {f'attachment{i}': f'附件{i}' for i in range(1, 7)},
        "B": {f'attachment{i}': f'附件{i}' for i in range(1, 7)},

    },
    "會議記錄": {
        "A": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6"}
    },
    "品質異常單": {
        "A": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6",
              'attachment7': "附件7",
              'attachment8': "附件8",
              'attachment9': "附件9",
              'attachment10': "附件10",
              'attachment11': "附件11",
              'attachment12': "附件12"
              }
    },
    "矯正預防措施處理單": {
        "A": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6"}
    },
    "樣品確認單": {
        "A": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6"}
    },
    "資產報廢申請單": {
        "A": {'attachment1': "附件1",
              'attachment2': "附件2",
              'attachment3': "附件3",
              'attachment4': "附件4",
              'attachment5': "附件5",
              'attachment6': "附件6"}
    },
    '重工單': {
        "A": {

        },
        "B": {

        }
    },
    "實驗測試申請單": {
        "A": {f'attachment{i}': f'附件{i}' for i in range(1, 11)}
    },
    '門禁權限申請單': {
        "A": {

        }
    },
    '名片申請單': {
        "A": {

        }
    },
    "部品承認通知單": {
        "A": {f'attachment{i}': f'附件{i}' for i in range(1, 13)}
    },
}

# 表單配置文件
FORM_INFOMATION = {
    "CORPORATE_SECTOR_CHOICES": [
        ('董事長室', '董事長室'),
        ('總經理室', '總經理室'),
        ('資材部', '資材部'),
        ('資材部採購組', '資材部採購組'),
        ('資材部物料組', '資材部物料組'),
        ('管理部', '管理部'),
        ('管理部人資課', '管理部人資課'),
        ('管理部資訊課', '管理部資訊課'),
        ('管理部財務總務課', '管理部財務總務課'),
        ('生產部', '生產部'),
        ('生產部製造課', '生產部製造課'),
        ('生產部生管課', '生產部生管課'),
        ('生產部生技課', '生產部生技課'),
        ('生產部製造課裝配一組', '生產部製造課裝配一組'),
        ('生產部製造課裝配二組', '生產部製造課裝配二組'),
        ('生產部製造課包裝組', '生產部製造課包裝組'),
        ('品技部', '品技部'),
        ('品技部品保課', '品技部品保課'),
        ('品技部加技課', '品技部加技課'),
        ('品技部品保課品檢組', '品技部品保課品檢組'),
        ('品技部加技課加工組', '品技部加技課加工組'),
        ('業務部', '業務部'),
        ('研發部', '研發部'),
        ('研發部產研課', '研發部產研課'),
        ('研發部產設課', '研發部產設課'),
    ],

    "UNIT_CHOICES": [
        ('', '--'),
        ('管理部', '管理部'),
        ('研發部', '研發部'),
        ('品技部', '品技部'),
        ('生產部', '生產部'),
        ('資材部', '資材部'),
        ('業務部', '業務部'),
    ],
    "DEPARTMENT_CHOICES": [
        ('', '--'),
        ('人資課', '人資課'),
        ('財務總務課', '財務總務課'),
        ('資訊課', '資訊課'),
        ('產研課', '產研課'),
        ('產設課', '產設課'),
        ('品保課', '品保課'),
        ('加技課', '加技課'),
        ('組裝課', '組裝課'),
        ('生管課', '生管課'),
    ],
    "GROUP_CHOICES": [
        ('', '--'),
        ('生技組', '生技組'),
        ('品檢組', '品檢組'),
        ('加工組', '加工組'),
        ('裝配一組', '裝配一組'),
        ('裝配二組', '裝配二組'),
        ('物料組', '物料組'),
        ('採購組', '採購組'),
    ],
    "LICENSE_CHOICES": [
        ('輕型機車', '輕型機車'),
        ('普通重型機車', '普通重型機車'),
        ('大型重型機車', '大型重型機車'),
        ('普通小型車', '普通小型車'),
        ('普通大貨車', '普通大貨車'),
    ],

    "EDUCATION_LEVEL_CHOICES": [
        ('高中職以下', '高中職以下'),
        ('高中職', '高中職'),
        ('專科', '專科'),
        ('大學', '大學'),
        ('碩士', '碩士'),
        ('博士', '博士'),
    ],

    'EDUCATION_LEVEL_LIMIT_CHOICES': [
        ('無限制', '無限制'),
        ('學歷限制', '學歷限制'),
    ],

    'DEPARTMENT_SCHOOL_CHOICES': [
        ('不拘', '不拘'),
        ('科系限制', '科系限制'),
    ],

    'JOB_DEPARTMENT_SCHOOL_CHOICES': [
        ('無限制', '無限制'),
        ('科系限制', '科系限制'),
    ],

    'CERTIFICATES_CHOICES': [
        ('無限制', '無限制'),
        ('需具備證照/執照', '需具備證照/執照'),
    ],
    "WORK_EXPERIENCE_CHOICES": [
        ('不拘', '不拘'),
        ('希望具備', '希望具備'),
    ],
    "JOB_WORK_EXPERIENCE_CHOICES": [
        ('無限制', '無限制'),
        ('希望具備', '希望具備'),
    ],

    # 職業類別
    'OCCUPATION_CATEGORY_CHOICES': [
        ('行政', '行政'),
        ('技術', '技術'),
        ('管理', '管理'),
    ],

    # 職業等級
    'CAREER_LEVEL_CHOICES': [
        ('', '請選擇'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    ],

    "TIME_FREQUENCY_CHOICES": [
        ('', '--'),
        ('日', '日'),
        ('月', '月'),
        ('年', '年'),
    ],

    # 這邊這些資料也有用來寫入django裡面的Group
    "JOB_TITLE_CHOICES": [
        ('董事長', '董事長'),
        ('總經理', '總經理'),
        ('執行副總', '執行副總'),
        ('總經理特助', '總經理特助'),
        ('人資課長', '人資課長'),
        ('人資高級專員', '人資高級專員'),
        ('資訊課長', '資訊課長'),
        ('資訊專員', '資訊專員'),
        ('資管專員', '資管專員'),
        ('財務總務課長', '財務總務課長'),
        ('會計專員', '會計專員'),
        ('清潔助理', '清潔助理'),
        ('管理助理', '管理助理'),
        ('管理專員', '管理專員'),
        ('管理部經理', '管理部經理'),
        ('產研課長', '產研課長'),
        ('產設課長', '產設課長'),
        ('生技副組長', '生技副組長'),
        ('研發總工程師', '研發總工程師'),
        ('研發機構高級工程師', '研發機構高級工程師'),
        ('研發機構工程師', '研發機構工程師'),
        ('實驗室測試工程師', '實驗室測試工程師'),
        ('研發助理工程師', '研發助理工程師'),
        ('研發高級專員', '研發高級專員'),
        ('研發製圖員', '研發製圖員'),
        ('品技部經理', '品技部經理'),
        ('加技工程師', '加技工程師'),
        ('品技助理工程師', '品技助理工程師'),
        ('CNC高級工程師', 'CNC高級工程師'),
        ('CNC工程師', 'CNC工程師'),
        ('CNC助理工程師', 'CNC助理工程師'),
        ('加工組組長', '加工組組長'),
        ('品技廠務專員', '品技廠務專員'),
        ('加工技師', '加工技師'),
        ('加工作業員', '加工作業員'),
        ('品檢專員', '品檢專員'),
        ('品檢組組長', '品檢組組長'),
        ('生產部經理', '生產部經理'),
        ('生產部副理', '生產部副理'),
        ('裝配一組長', '裝配一組長'),
        ('裝配二副組長', '裝配二副組長'),
        ('裝配一副組長', '裝配一副組長'),
        ('裝配三組長', '裝配三組長'),
        ('組裝課長', '組裝課長'),
        ('組裝技師', '組裝技師'),
        ('組裝助理技師', '組裝助理技師'),
        ('組裝技術員', '組裝技術員'),
        ('組裝作業員', '組裝作業員'),
        ('裝配技師', '裝配技師'),
        ('裝配助理技師', '裝配助理技師'),
        ('裝配技術員', '裝配技術員'),
        ('廠務專員', '廠務專員'),
        ('廠務助理', '廠務助理'),
        ('工讀生', '工讀生'),
        ('資材部經理', '資材部經理'),
        ('生管課長', '生管課長'),
        ('生管專員', '生管專員'),
        ('生管助理', '生管助理'),
        ('物管組長', '物管組長'),
        ('物料副組長', '物料副組長'),
        ('物料高級專員', '物料高級專員'),
        ('物料專員', '物料專員'),
        ('物料助理', '物料助理'),
        ('採購組長', '採購組長'),
        ('採購高級專員', '採購高級專員'),
        ('採購專員', '採購專員'),
        ('採購技師', '採購技師'),
        ('業務部經理', '業務部經理'),
        ('業務高級專員', '業務高級專員'),
        ('業務助理', '業務助理'),
        ('國貿高級專員', '國貿高級專員'),
        ('國貿管理師', '國貿管理師'),
        ('行銷專員', '行銷專員'),
        ('裝配二組長', '裝配二組長'),
        ('加技助理工程師', '加技助理工程師'),
        ('品保高級專員', '品保高級專員'),
        ('製造工程師', '製造工程師'),
        ('加工助理工程師', '加工助理工程師'),
        ('資訊高級專員', '資訊高級專員'),
        ('裝配作業員', '裝配作業員'),
        ('物流技師', '物流技師'),
        ('物流助理技師', '物流助理技師'),
        ('裝櫃技術員', '裝櫃技術員'),
        ('採購助理', '採購助理'),
    ]

}


# 部門權限文件
DEPARTMENT_AUTHORITY = {
    "總經理室": {
        "管理部": {
            "資訊課": {},
            "人資課": {},
            "財務總務課": {}
        },
        "研發部": {
            "產設課": {},
            "產研課": {}
        },
        "品技部": {
            "加技課": {
                "加工組": {}
            },
            "品保課": {
                "品檢組": {}
            }
        },
        "生產部": {
            "生管課": {},
            "生技課": {},
            "製造課": {
                "裝配一組": {},
                "裝配二組": {},
                "包裝組": {}
            }
        },
        "資材部": {
            "採購組": {},
            "物料組": {}
        },
        "業務部": {
        }
    }
}


FROM_AUTHORITY = {
    "人員增補申請表": {
        "A": ['人資課', '管理部經理', '執行副總']
    },
    "招募面試評核表": {
        "A": ['人資課', '管理部經理', '執行副總']
    },
    "職務說明書": {
        "A": ['人資課', '管理部經理', '執行副總']
    },
    "出圖依賴書": {
        "A": ['業務部', '業務部經理',  '執行副總'],
        'B': ['業務部', '業務部經理',  '執行副總']
    },
    "客訴紀錄單": {
        "A": ['業務部', '業務部經理',  '執行副總'],
        "B": ['業務部', '業務部經理',  '執行副總'],
    },
    "會議記錄": {
        "A": ['研發部', '總經理特助', '業務部', '業務部經理', '執行副總']
    },
    "品質異常單": {
        "A": ['研發部', '總經理特助', '業務部', '業務部經理', '執行副總', '品技部']
    },
    "矯正預防措施處理單": {
        "A": ['研發部', '業務部', '品技部', '資材部', '管理部', '生產部', '總經理特助', '執行副總']
    },
    "樣品確認單": {
        "A": ['研發部', '總經理特助', '業務部', '業務部經理', '執行副總']
    },
    "資產報廢申請單": {
        "A": ['資訊課', "管理部經理", '執行副總']
    },
    "重工單": {
        "A": ['品技部', "品技部經理", '執行副總'],
        "B": ['品技部', "品技部經理", '執行副總'],
    },
    "實驗測試申請單": {
        "A": ['品技部', "業務部", '研發部','生技課']
    },
    "門禁權限申請單": {
        "A": ['人資課', '管理部經理', '執行副總']
    },
    "名片申請單": {
        "A": ['人資課', '管理部經理', '執行副總']
    }
}


# 人資職務說明書表單
GOOD_AT_TOOL = DateInput.GOOD_AT_TOOL
WORK_SKLL = DateInput.WORK_SKLL


# 表單審核畫面要切割的
RECRUITMENTINTERVIEWEVALUATION_TO_CHECK = [
    '應徵者姓名', '面試職缺', '所屬單位', '面試結果', '單位面試官', '人資面試官', '面試日期']
RECRUITMENTINTERVIEWEVALUATION_TO_PARSER = [
    '性格/人格偏好與價值觀', 'Intent意圖(獲取報酬、被滿足的方向)', '學歷背景與天賦(教育學習歷程)', '業界知識、經驗與技能', '自我概念(一個人對自己的看法)', '對知識的追求與學習能力', '業界人脈', '行為觀察備註(如眼神,行為,服裝,姿態)']


JOBDESCRIPTION_TO_CHECK = [
    '所屬單位', '職務名稱', '職系', '職等',
    '主要職責', '教育程度', '自訂義教育程度', '科系要求',
    '自訂系所', '專業證照/執照', '其他證照', '工作經驗', '職稱', '工作年數',
    '持有駕照', '是否有管理責任', '管理責任']

JOBDESCRIPTION_OTHER_TO_CHECK = ['對上',  '對下', '對內', '對外']
PERSONNELADDITIONAPPLICATION_TO_CHECK = ['申請單位',
                                         '增補職稱', '對外增補職稱','增補人數', '增加人員原因', '增補原因', '短期時長', '對外刊登之工作內容與職務說明', '最低薪資',
                                         '最高薪資', '管理責任', '是否需要出差']

PERSONNELADDITIONAPPLICATION_TO_CHECK2 = ['性別', '年齡', '年齡輸入', '持有駕照', '學歷', '科系', '自訂系所', '經歷職務年資', '職位名稱',
                                          '工作年資', '學校知識', '業界知識/經驗', '執照/證照', '其他/備註'
                                          ]


HEAVYWORKORDER_TO_CHECK = ['數量',
                           '責任單位',
                           '付費單位',
                           '重工訊息來源',
                           '來源備註',
                           '預計完工日',
                           '備註',
                           '產品編號(重工前)',
                           '品名規格(重工前)',
                           '產品編號(重工後)',
                           '品名規格(重工後)',
                           '重工原因',
                           '重工後處置',
                           'IO單號',
                           '重工項目',
                           '來源類別'
                           ]

# 實驗室預估完成日期
EXPERIMENTALTEST_MAP = {
    "競品比較": "60",
    "競品研究": "60",
    "強度測試": "7",
    "壽命測試": "60",
    "組裝測試": "3",
    "CAE模擬": "5",
    "元貝產品系列測試": "60",
    "功能測試": "3",
}
