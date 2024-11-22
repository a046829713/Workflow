"""
    用來製作每日通知,提醒有待辦事項的人趕快處理
    並且在setting中設定Crontab
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import Employee, Process_real, CustomUser, Level
import json
from workFlow.DataTransformer import get_combin_list
from workFlow.DataTransformer import GetWorkid, Get_listType, Get_otherworkid
from .DataTransformer import change_department_head, _filter_combin
from datetime import datetime
import platform
from typing import Optional


import logging
logger = logging.getLogger('my_logger')

def approved_transfor(all_user, all_process, all_employee):
    """ 
        其實和代辦審核的邏輯相似 但有些地方略有不同
        將符合這個user的表單傳送出去
    """
    all_target_workid = {}
    for _each_process in all_process:
        approval_status = json.loads(
            _each_process.approval_status.replace("'", '"'))
        endorsement_allow = _each_process.endorsement_allow

        # 雖然之前都在加簽,但是一但endorsement_allow被允許之後或拒絕之後就不需要再走加簽的判斷了
        if ('加簽' not in approval_status and "同意加簽" not in approval_status and "不同意加簽" not in approval_status) or endorsement_allow is not None:
            combin_list = get_combin_list(_each_process, endorsement_allow)
            _filter_combin(_each_process, combin_list)
            # 申請人變數
            applicant = _each_process.process_id.form_id.applicant

            # 原本部級主管定義是一個人 這邊已經轉換為Group了(在workflow的系統當中,簽核者的身份都是以活字格的角色,或是團體下去思考)
            new_combin = change_department_head(combin_list, applicant)

            target_workid = GetWorkid(new_combin, all_user)
            Get_otherworkid(target_workid, new_combin, applicant,
                            _each_process.process_id.process_id)

            # 添加直屬主管的workid
            if 'direct_supervisor' in combin_list:
                for each_data in all_employee:
                    if each_data.worker_id == applicant:
                        target_workid.append(each_data.supervisor_id)
                        
            # 不論如何這關都要簽(臨時會放入的這種),如果是加簽,還沒有考慮這種臨時指派的            
            if _each_process.temporaryapproval:
                target_workid.extend(json.loads(_each_process.temporaryapproval))
        else:
            # 取得所有流程裡面的事件,並且判斷目前執行到的最後一關的下一關是否有自己
            combin_list = []
            # 透過事件ID取得關卡狀態,並且判斷該站點是否需要自己否則跳過
            levels = Level.objects.filter(
                level_id__startswith=_each_process.process_id.level_id)
            station_manager = ''

            for _level in levels:
                if _level.station_name == _each_process.site_record:
                    # 取得當下關卡的負責人員
                    station_manager = _level.endorsement_manager
                    station_group = _level.endorsement_group
                    station_group = station_group.replace("'", '"')
                    station_group = json.loads(station_group)

                    if isinstance(station_group, list):
                        combin_list = combin_list + station_group
                    else:
                        if station_group:
                            combin_list.append(station_group)

            target_workid = GetWorkid(combin_list, all_user)

            if station_manager:
                target_workid.append(station_manager)
                
            # 臨時需要加簽的人員
            if _each_process.endorsement_asign:                
                target_workid.extend(json.loads(_each_process.endorsement_asign.replace("'", '"')))
                
            # 判斷允許加簽的人是否已經都簽核完畢
            if _each_process.endorsement_approvers:
                for i in [workid for workid, chioce in Get_listType(_each_process.endorsement_approvers)]:
                    target_workid.remove(i)

        all_target_workid.update({_each_process: target_workid})

    return all_target_workid


def send_email(recipient_email: str, Assign_email_str: str):
    """
        將郵件寄出
    """
    # 設定寄件人和收件人
    sender_email = 'admin@mail.ybico.com.tw'

    # 建立一個多部分的email
    msg = MIMEMultipart()

    # 設定email的標題和寄件人、收件人
    msg['Subject'] = '工作流系統每日通知'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    if platform.system() == 'Windows':
        if Assign_email_str == 'everyday':
            email_path = r"Company\templates\Company\email.html"
    else:
        if Assign_email_str == 'everyday':
            email_path = r"/home/user/桌面/program/Workflow/workflow/Company/templates/Company/email.html"
        
    # 建立email的內容 # linux
    with open(email_path, "r", encoding='utf-8') as file:
        email_content = file.read()
        msg.attach(MIMEText(email_content, 'html'))

    # 連接SMTP服務器並發送email
    with smtplib.SMTP('192.168.2.180', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender_email, 'YB22067856!')
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())

    
    logger.debug(f"傳送成功-send_email,時間:{datetime.now()},收件人信箱:{recipient_email}")

def short_term_QAR_send_email(form_id:str, recipient_email: str):
    """
        將郵件寄出(品質異常單)品質異常單手動開立通知
    """
    # 設定寄件人和收件人
    sender_email = 'admin@mail.ybico.com.tw'

    # 建立一個多部分的email
    msg = MIMEMultipart()

    # 設定email的標題和寄件人、收件人
    msg['Subject'] = '品質異常單手動開立通知'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    if platform.system() == 'Windows':
        email_path = r"Company\templates\Company\short_term_QAR.html"
    else:
        email_path = r"/home/user/桌面/program/Workflow/workflow/Company/templates/Company/short_term_QAR.html"
    
    # 建立email的內容 # linux
    with open(email_path, "r", encoding='utf-8') as file:
        email_content = file.read()
        email_content = email_content.replace('<span class="form_number">#</span>',f'<span class="form_number">表單號碼:{form_id}</span>')
        msg.attach(MIMEText(email_content, 'html'))

    # 連接SMTP服務器並發送email
    with smtplib.SMTP('192.168.2.180', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender_email, 'YB22067856!')
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())

    print("傳送成功-short_term_QAR_send_email")

def sendDailyEmail():
    all_user = CustomUser.objects.all()
    # 將每一個流程取出來 #並且取得
    all_process = Process_real.objects.all()
    all_employee = Employee.objects.all()

    if datetime.today().weekday() in [5, 6]:
        return

    toSendData = approved_transfor(all_user, all_process, all_employee)
    data = list(toSendData.values())
    flattenedData = list(set([item for sublist in data for item in sublist]))

    for user in all_user:
        if user.username == 'Administrator':
            continue

        if user.username in flattenedData:
            try:
                # send_email(user.email,Assign_email_str='everyday')
                print("成功寄出EMIAL")
            except Exception as e:
                logger.error('Company-Email_Send-sendDailyEmail Function Error: %s', e, exc_info=True)

def _Heavyworkorder_email_send(form_id:str,recipient_email: str):
    """
        將重郵件寄出
        form_id(str):表單號碼提醒使用者哪一個表單已經被核准
    """
    # 設定寄件人和收件人
    sender_email = 'admin@mail.ybico.com.tw'

    # 建立一個多部分的email
    msg = MIMEMultipart()

    # 設定email的標題和寄件人、收件人
    msg['Subject'] = '重工單核准通知'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    if platform.system() == 'Windows':
        email_path = r'C:\Users\user\Desktop\程式專區\Workflow\workflow\Company\templates\Company\Heavyworkorder_email.html'
    else:
        email_path = r"/home/user/桌面/program/Workflow/workflow/Company/templates/Company/Heavyworkorder_email.html"
    
    # 建立email的內容 # linux
    with open(email_path, "r", encoding='utf-8') as file:
        # 本地測試
        email_content = file.read()
        email_content = email_content.replace('<span class="text-primary">#</span>',f'<span class="text-primary">表單號碼:{form_id}</span>')
        msg.attach(MIMEText(email_content, 'html'))

    # 連接SMTP服務器並發送email
    with smtplib.SMTP('192.168.2.180', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender_email, 'YB22067856!')
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())

    print("傳送成功-_Heavyworkorder_email_send")
    
def Heavyworkorder_email_send(form_id):
    """
        通知所有重工單人員
    """
    # 這些是重工單人員需要通知的名單
    Heavyworkorder_emails =[
        "張家毓",
        '魏瑜慧',
        '黃惠萍',
        '劉安邦',
        '張美芳',        
        '李宜珍',
        '林詩涵',
        '柳宥蓁',
        '劉立威',
        '鄭振佑',
    ]

    all_employee = Employee.objects.all()
    all_user = CustomUser.objects.all()
    
    worker_id =''
    email = ''
    for user in Heavyworkorder_emails:
        for employee_info in all_employee:
            if employee_info.name == user:
                # 取得工號之後 就可以寄信了
                worker_id = employee_info.worker_id
                break
             
        for _user in all_user:
            if worker_id == _user.username:
                email = _user.email
                break
            
        if email:
            _Heavyworkorder_email_send(form_id,email)