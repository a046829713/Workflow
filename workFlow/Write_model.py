def write_group_names():
    from django.contrib.auth.models import Group
    from workFlow.Appsettings import FORM_INFOMATION
    # 這邊是用來寫入職稱(部門中的角色)
    job_titles = FORM_INFOMATION['JOB_TITLE_CHOICES']
    job_titles = [name for name, _ in job_titles]
    for job_title in job_titles:
        print("開始寫入")
        Group.objects.get_or_create(name=job_title)

    departments = ['總經理室', '管理部', '資訊課', '人資課', '財務總務課', '研發部', '產設課', '產研課', '生技組', '品技部', '加技課', '加工組',
                   '品保課', '品檢組', '生產部', '組裝課', '裝配一組', '裝配二組', '裝配三組', '資材部', '生管課', '採購組', '物料組', '業務部', '國內業務', '國外業務']

    for department in departments:
        print("開始寫入")
        Group.objects.get_or_create(name=department)


write_group_names()