from django.db import models
class AbnormalMK(models.Model):
    mk_number = models.CharField(max_length=100, verbose_name="MK單號")
    form_id = models.CharField(max_length=100, verbose_name="重工單號")
    item = models.CharField(max_length=100, verbose_name="令次")
    remarks = models.TextField(verbose_name="備註")

    def __str__(self):
        return f"{self.mk_number} - {self.form_id} - {self.item}"

class AbnormalFactna(models.Model):
    form_id = models.CharField(max_length=100, verbose_name="重工單號")
    item = models.CharField(max_length=100, verbose_name="令次")
    factoryno = models.CharField(max_length=100, verbose_name="加工廠商編號")
    factoryname = models.CharField(max_length=100, verbose_name="加工廠商名稱")
    makeno = models.CharField(max_length=100, verbose_name="加工製程編號")
    makename = models.CharField(max_length=100, verbose_name="加工製程")
    unit_price = models.FloatField(null=True,verbose_name="單價")
    total_price = models.FloatField(null=True,verbose_name="總價")
    
    class Meta:
        unique_together = (('form_id', 'item'),)  

    def __str__(self):
        return f"{self.form_id}_{self.item},id = {self.id}" # type:ignore

    def number(self):
        return str(int(self.item) -1 )