from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import platform
import smtplib



class Email_Sever():
    def __init__(self, windows_path: str, linux_path: str) -> None:
        """
            所有寄信的功能
        """
        self.system = platform.system()  # 'Windows'
        self.Recipient_list = []
        self.windows_path = windows_path
        self.linux_path = linux_path
        self.pick_path()

    def update_Recipient_list(self, User_data: list):
        self.Recipient_list = User_data

    def pick_path(self):
        """
            根據系統來選擇需要的郵件地址
        """
        if self.system == 'Windows':
            self.email_path = self.windows_path
        else:
            self.email_path = self.linux_path

    def change_context(self, form_id: str):
        # 建立email的內容 # linux
        with open(self.email_path, "r", encoding='utf-8') as file:
            # 本地測試
            email_content = file.read()
            email_content = email_content.replace(
                '<span class="text-primary">#</span>', f'<span class="text-primary">表單號碼:{form_id}</span>')
            self.email_content = email_content

    def Send(self, Subject:str):
        for each_recipient in self.Recipient_list:
            self._email_send(Subject, recipient_email=each_recipient.email)

    def _email_send(self, Subject, recipient_email: str):
        """
            將重郵件寄出
            form_id(str):表單號碼提醒使用者哪一個表單已經被核准
        """
        # 設定寄件人和收件人
        sender_email = 'admin@mail.ybico.com.tw'

        # 建立一個多部分的email
        msg = MIMEMultipart()
        # 設定email的標題和寄件人、收件人
        msg['Subject'] = Subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(self.email_content, 'html'))

        # 連接SMTP服務器並發送email
        with smtplib.SMTP('192.168.2.180', 587) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(sender_email, 'YB22067856!')
            smtp_server.sendmail(
                sender_email, recipient_email, msg.as_string())

        print(f"Email_Sever-傳送成功,表單:{Subject}")





