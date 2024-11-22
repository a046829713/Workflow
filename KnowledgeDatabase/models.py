from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

    

# Create your models here.
class KnowledgeDatabase_model(models.Model):
    # 文章類型 為主要表頭
    project_name = models.CharField(max_length=255, verbose_name="專案名稱")
    tags = models.TextField(verbose_name="標籤")  # 保存標籤為逗號分隔的字符串或者使用JSON格式
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立日期")
    applicant = models.CharField(max_length=100, verbose_name="申請人")  
    content = RichTextUploadingField(null=True, verbose_name="文章")
    unit = models.CharField(null=True, max_length=100, verbose_name="部門")
    last_edit_time = models.DateTimeField(auto_now=True, verbose_name="最後修改日期")
    privacy = models.CharField(max_length=50, verbose_name="隱私", null=True)
    def __str__(self):
        return self.project_name