from Database import SQL_operate
from workFlow.Appsettings import DEPARTMENT_AUTHORITY
import re
from .models import Employee
def getDepartment(x):
    if '室' in x:
        return x
    
    data  = re.search(r'[\u4e00-\u9fa5]+部',x)
    if data:
        ouput = data.group(0) + '經理'
    return ouput

def Write_Employee():
    """
        Crontab task 寫入每日排程
        寫入company employee
    """
    hr_employee = SQL_operate.DB_operate(
        sqltype="MISMIS").get_pd_data("select 工號, 姓名, CONVERT(nvarchar(max), 單位)單位, CONVERT(nvarchar(max), 狀態)狀態, 直屬主管工號, 直屬主管姓名, 職稱名稱 from hr_employee")

    hr_employee = hr_employee[hr_employee['狀態'] == '在職']
    hr_employee = hr_employee[hr_employee['直屬主管工號'].apply(lambda x: False if "None" in x else True)]

    # 要判斷某個單位上級,若部沒有在裡面要重新組合
    hr_employee['部級'] = hr_employee['單位'].apply(getDepartment)


    # 讀取你的pandas DataFrame
    df = hr_employee
    
    # 先保存後刪除
    for index, row in df.iterrows():
        # 創建Employee對象
        employee = Employee(
            worker_id=row['工號'],
            name=row['姓名'],
            unit=row['單位'],
            status=row['狀態'],
            supervisor_id=row['直屬主管工號'],
            supervisor_name=row['直屬主管姓名'],
            position_name=row['職稱名稱'],
            department_level=row['部級'],
        )
        # 存儲到數據庫
        employee.save()

    all_workids = df['工號'].to_list()
    # 將Employee裡面的資料全部清除 # 否則已經離職的人員會繼續存在
    Employee.objects.exclude(worker_id__in=all_workids).delete()
    
    print("回補完成")

def check_user_if_alive():
    # 當每天
    from .Database import SQL_operate
    from .models import Employee, CustomUser

    employees = Employee.objects.all()
    effective_work_ids = [i.worker_id for i in employees]
    users = CustomUser.objects.all()

    for user in users:
        if user.username == 'Administrator':
            user.is_active = True
            user.save()
            continue
        
        if user.username not in effective_work_ids and user.is_active:
            user.is_active = True  # 將用戶設置為非活動
            user.save()  # 保存更改
            

            


Write_Employee()