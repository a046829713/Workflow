from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings as django_settings
from Company.models import CustomUser
import json

class Visitor(models.Model):
    """
        廠商訪客預約登記行事曆
    """
    company_id = models.CharField(max_length=255, verbose_name=_("Company ID"), blank=True, null=True)
    company_name = models.CharField(max_length=255, verbose_name=_("Company Name"), blank=True, null=True)
    visitor_name = models.CharField(max_length=255, verbose_name=_("Visitor Name"))
    # 事由
    purpose = models.CharField(max_length=500, verbose_name=_("Purpose of Visit"))
    number_of_visitors = models.IntegerField(verbose_name=_("Number of Visitors"))
    interviewee_name  = models.CharField(max_length=255, verbose_name=_("Interviewee Name "))


    # 電話號碼
    tellphone_number = models.CharField(max_length=50, verbose_name=_("contact number in the company"), blank=True, null=True)

    creator = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("creator"),
        related_name="created_visitors",
    )

    slug = models.CharField(max_length=50, verbose_name=_("Data Base Slug"))
    
    class Meta:
        verbose_name = _("Visitor")
        verbose_name_plural = _("Visitor")

    def __str__(self) -> str:
        print("除錯測試:",self.interviewee_name)
        all_FullName = self.interviewee_name

        return f'公司行號:{self.company_name}' + '，' +   f'拜訪者:{self.visitor_name}' + \
        '，' +f"受訪者:{all_FullName}" + '，' +f'事由:{self.purpose}'+ '，' +f'到訪人數:{self.number_of_visitors}'+ '，' + \
            f"分機號碼:{self.tellphone_number}"
    
    def get_absolute_url(self):
        return reverse("calendar_create_event", args=['VendorVisitScheduler'])