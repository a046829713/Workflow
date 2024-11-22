from django.db import models
from django.conf import settings

# Create your models here.
class Sticker(models.Model):
    # 產品編號，作為主鍵
    PROD_NO = models.CharField(primary_key=True, max_length=100)

    # 購買類型
    BUY_TYPE_CHOICES = (
        ('自印', '自印'),
        ('外購', '外購'),
    )
    BuyType = models.CharField(max_length=100,  null=True, choices=BUY_TYPE_CHOICES)

    # 描述類型
    DSC_TYPE_CHOICES = (
        ('標準', '標準'),
        ('依訂單不同', '依訂單不同'),
    )
    DSCType = models.CharField(max_length=100, null=True , choices=DSC_TYPE_CHOICES)

    # 高度大小，以毫米為單位
    heightsize = models.IntegerField(help_text="Height in millimeters", null=True)

    # 寬度大小，以毫米為單位
    widthsize = models.IntegerField(help_text="Width in millimeters", null=True)

    # 材質 牛皮 白紙
    MATERIAL_CHOICES = (
        ('牛皮紙', '牛皮紙'),
        ('白紙', '白紙'),
        ('透明材質', '透明材質'),
    )
    material = models.CharField(max_length=100, null=True, choices=MATERIAL_CHOICES)

    # 顏色
    COLOR_CHOICES = (
        ('彩色', '彩色'),
        ('黑白', '黑白'),
        ('透明', '透明'),
    )
    color = models.CharField(max_length=100, null=True, choices=COLOR_CHOICES)

    # 圖片
    image = models.ImageField(upload_to='stickers/', default='', blank=True)

    # 備註
    remark = models.TextField(blank=True, null=True)

    # AUTH_USER_MODEL = 'Company.CustomUser' 透過workFloe裡面的預設驗證模型
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_stickers'
    )