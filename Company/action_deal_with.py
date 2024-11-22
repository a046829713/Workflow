from Company.models import Form
from .Email_Send import Heavyworkorder_email_send
from .New_Email_Send import Email_Sever
from .models import Form, CustomUser
from django.contrib.auth.models import Group

def Send_Email_CustomerComplaintRecord(Form_objects:Form):
    # 由於有滿多地方都會用到客訴表單變動 所以集中起來
    mailserver = Email_Sever(windows_path=r'C:\Users\user\Desktop\程式專區\Workflow\workflow\Company\templates\Email\CustomerComplaintRecord_Email.html',
                                linux_path=r'/home/user/桌面/program/Workflow/workflow/Company/templates/Email/CustomerComplaintRecord_Email.html')

    mailserver.update_Recipient_list(User_data=list(CustomUser.objects.filter(groups__in=[Group.objects.get(name='業務部')],is_active=True)))
    mailserver.change_context(form_id=Form_objects.form_id)
    mailserver.Send('客訴表單變動')
    
def Send_change_form_Email(Form_objects:Form):
    """
        只要表單有變動都可以使用這個函數
    """
    mailserver = Email_Sever(windows_path=r'C:\Users\user\Desktop\程式專區\Workflow\workflow\Company\templates\Email\commond_Email.html',
                                linux_path=r'/home/user/桌面/program/Workflow/workflow/Company/templates/Email/commond_Email.html')
    mailserver.update_Recipient_list(User_data=[CustomUser.objects.get(username=Form_objects.applicant)])
    mailserver.change_context(form_id=Form_objects.form_id)
    mailserver.Send(Subject='表單變動通知')

    
    
class form_action_deal_with():
    def __init__(self, choice: str) -> None:
        self.choice = choice

    def run(self, Form_objects: Form, post_data: dict) -> None:
        if self.choice in ['核准', '確認']:
            # 當業務填寫了對於外部處理的東西之後保存起來
            if Form_objects.form_name == '客訴紀錄單' and post_data.get('externalprocessing'):
                Form_objects.data['externalprocessing'] = post_data.get(
                    'externalprocessing')
                Form_objects.save()
                return

            # 預計完成日期,由生產管理員回覆
            if Form_objects.form_name == '重工單' and self.choice == '確認':
                Form_objects.data['estimated_completion_date'] = post_data['estimated_completion_date']
                Form_objects.save()
                return

            # 經理核准之後，統一寄信給每個需要知道的人
            if Form_objects.form_name == '重工單' and self.choice == '核准':
                Heavyworkorder_email_send(Form_objects.form_id)
                return

            if Form_objects.form_name =='實驗測試申請單':
                if self.choice == '確認':
                    Form_objects.data['estimated_completion_date'] = post_data.get('estimated_completion_date')
                    Form_objects.save()
                
        elif self.choice in ['結案']:
            if Form_objects.form_name == '客訴紀錄單':
                Send_Email_CustomerComplaintRecord(Form_objects)

        elif self.choice in ['駁回']:
            pass
                
        # 不論何種狀況一律都要通知申請人
        Send_change_form_Email(Form_objects)