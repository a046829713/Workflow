# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from workFlow.Appsettings import SAVE_ATTACHMENT_PATH
from ckeditor_uploader.fields import RichTextUploadingField


def get_upload_to(instance, filename):
    """ 
    form_name :unit_configuration
    取得附件要保存的路徑
    """
    form_name = instance.form_name
    for key, value in SAVE_ATTACHMENT_PATH.items():
        if form_name == key:
            return value + '/' + filename


class CustomUser(AbstractUser):
    """

        自訂自己的 UserModel
    Args:
        AbstractUser (_type_): 它將繼承 AbstractUser 中的所有字段和方法,包括用戶名username、密碼password、電子郵件email等。
    """
    FullName = models.CharField(max_length=100, null=False)


class Attachment(models.Model):
    name = models.CharField(max_length=255)  # 文件的名字，如 "單位人員配置圖"
    form_name = models.CharField(max_length=255, default='')  # 相關表單的名稱
    form_id = models.CharField(max_length=255, default='')  # 相關表單的ID
    file = models.FileField(upload_to=get_upload_to)  # type:ignore

    class Meta:
        db_table = 'Company_attachment'


class Form(models.Model):
    form_id = models.CharField(max_length=100, primary_key=True)  # 表單ID
    form_name = models.CharField(max_length=100)  # 表單名稱
    applicant = models.CharField(max_length=100)  # 申請人
    result = models.CharField(max_length=100)  # 結果
    application_date = models.CharField(max_length=100)  # 申請日期
    closing_date = models.CharField(max_length=100)  # 結案日期
    version_number = models.CharField(max_length=100)  # 版本號
    data = models.JSONField()  # Data

    # Company_forms_attachments # 這個是中介表用來記錄和表單之間的關係
    attachments = models.ManyToManyField(Attachment)  # 附件

    # 這種的繼承是為了知道使用者修改了甚麼表單來做繼承
    # 用來比較同類型單(母子單之間之差異)
    parents_form_id = models.CharField(max_length=100, default='')
    # 來源單號最主要的差異在不同類型之間的表單
    resourcenumber = models.CharField(max_length=100, default='')
    # 關係單號是一種(非強關聯的關係)
    relationshipnumber = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'Company_forms'  # 表名

    def delete(self, *args, **kwargs):
        # 刪除步驟
        # 1.確認刪掉 (django負責)Process
        # 2.確認刪掉 (django負責)Process_real
        # 3.確認刪掉 (手動)Process_history
        # 4.確認刪掉 (手動)Attachment
        # 5.確認刪掉 (django負責)RichText
        for attachment in self.attachments.all():
            attachment.file.delete()  # 刪除文件
            attachment.delete()  # 刪除模型實例
        
        # 需要手動刪除 因為django 透過資料庫刪除時 不會再回來call delete function
        process = Process.objects.filter(form_id=self.form_id).first()
        if process:
            Process_history.objects.filter(process_id=process.process_id).delete()

        # 刪除中介表(django 在後台會自己處理)
        super().delete(*args, **kwargs)
    
class Process(models.Model):
    process_id = models.CharField(max_length=100, primary_key=True)
    # 。on_delete=models.CASCADE 則表示當相關的 Form 被刪除時，與其相關的所有 Process 也將被刪除
    form_id = models.ForeignKey(Form, on_delete=models.CASCADE)
    # on_delete=models.CASCADE 改成 on_delete=models.PROTECT。這樣在你嘗試刪除 Form  時，如果還有相關的 Process 存在，Django 會拋出 ProtectedError 異常。
    level_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'Company_process'


# 這是產生實例的地方,運行中的才會出現
class Process_real(models.Model):
    process_id = models.ForeignKey(
        Process, on_delete=models.CASCADE, primary_key=True)
    site_record = models.CharField(max_length=100)  # 站點記錄
    approver = models.ForeignKey(CustomUser, on_delete=models.PROTECT)  # 簽核者
    approval_opinion = models.CharField(max_length=500)  # 簽核意見
    approval_time = models.CharField(max_length=100)  # 簽核時間
    approval_status = models.CharField(max_length=100)   # 簽核狀態(站點選擇)
    process_status = models.CharField(max_length=50)  # 流程狀態
    endorsement_allow = models.BooleanField(
        default=None, null=True)  # 是否允許進入下一關卡
    endorsement_approvers = models.CharField(max_length=200, null=True)
    endorsement_count = models.IntegerField(default=0)
    endorsement_asign = models.CharField(max_length=200, null=True)
    # Temporary approval 用作臨時簽核,當簽核完畢之後才會用到的放這裡 # 這種方式沒有考慮到會簽,加簽等功能的實現
    # 所以試用場景為搶簽模式,若為其它模式建議使用加簽,而不是採用臨時簽核
    temporaryapproval = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'Company_process_real'


class Process_history(models.Model):
    """ 由於 process_history ，process_id 是多個所以不能使用process_id 當成primary_key """
    process_id = models.CharField(max_length=100)  # 記錄下process id 就好不要關聯
    site_record = models.CharField(max_length=100)  # 站點記錄
    approver = models.ForeignKey(CustomUser, on_delete=models.PROTECT)  # 簽核者
    approval_opinion = models.CharField(max_length=2000)  # 簽核意見
    approval_time = models.CharField(max_length=100)  # 簽核時間
    approval_status = models.CharField(max_length=100)   # 簽核狀態(站點選擇)

    class Meta:
        db_table = 'Company_process_history'


class RichText(models.Model):
    """RichText for form"""
    form = models.ForeignKey(
        Form,
        related_name="rich_text_attachments",
        on_delete=models.CASCADE,
    )
    content = RichTextUploadingField(null=True, verbose_name="內容")

    class Meta:
        db_table = 'Company_RichText'  # 表名


class Level(models.Model):
    level_id = models.CharField(
        max_length=100, primary_key=True)  # 關卡ID  +  (本站序號)
    level_name = models.CharField(max_length=100, null=True)  # 關卡中文名稱
    station_name = models.CharField(max_length=255)  # 本站點名稱
    next_station = models.CharField(max_length=255)  # 下一站
    previous_station = models.CharField(max_length=255)  # 上一站
    station_choice = models.CharField(max_length=255)  # 站點選擇
    station_manager = models.CharField(
        max_length=255, default='', blank=True)  # 站點負責人
    station_group = models.CharField(max_length=255)  # 站點團體
    station_mode = models.CharField(max_length=255)  # 站點模式
    endorsement_manager = models.CharField(
        max_length=255, default='', blank=True)  # 加簽負責人
    endorsement_group = models.CharField(
        max_length=255, default='', blank=True)  # 加簽團體
    endorsement_mode = models.CharField(
        max_length=255, default='', blank=True)  # 加簽模式
    limited_time = models.CharField(
        max_length=255, default='', blank=True)  # 限時
    versionNumber = models.CharField(max_length=255, default='')  # 限時

    class Meta:
        db_table = 'Company_levels'  # 表名


class Employee(models.Model):
    worker_id = models.CharField(max_length=100, primary_key=True)  # 工號
    name = models.CharField(max_length=100)  # 姓名
    unit = models.CharField(max_length=100)  # 單位
    status = models.CharField(max_length=50)  # 狀態
    supervisor_id = models.CharField(max_length=100)  # 直屬主管工號
    supervisor_name = models.CharField(max_length=100)  # 直屬主管姓名
    position_name = models.CharField(max_length=100)  # 職稱名稱
    department_level = models.CharField(max_length=100, null=True)  # 部級

    class Meta:
        db_table = 'Company_employee'  # 表名
