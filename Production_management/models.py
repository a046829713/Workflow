from django.db import models

# Create your models here.
class HistoryDailyConsume(models.Model):
    date = models.DateField(primary_key=True)
    data = models.TextField()