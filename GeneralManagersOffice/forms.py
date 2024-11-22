from django import forms
from Company.models import CustomUser, Form, Employee
from django_select2.forms import Select2Widget
from Database import SQL_operate
from django.utils import timezone


class CorrectiveeActionReportForm(forms.Form):
    filter_form = Form.objects.filter(form_name='客訴紀錄單')
    FORMS_CHOICES = [(i.form_id, i.form_id + ' ' + i.form_name)
                     for i in filter_form]

    filter_staff = Employee.objects.all()
    STAFF_CHOICES = [(i.worker_id, i.worker_id + ' ' + i.name)
                     for i in filter_staff]

    resource_no = forms.ChoiceField(
        choices=FORMS_CHOICES,
        label="客訴來源單號",
        widget=Select2Widget(attrs={'class': 'form-control'})
    )

    related_personnel = forms.MultipleChoiceField(
        label="相關人員",
        choices=STAFF_CHOICES,
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select select2-multiple', 'id': 'related_personnel'}),
    )
    complaint_reason = forms.CharField(
        label="不良原因",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'complaint_reason'})
    )

    temporary_plan = forms.CharField(
        label="臨時對策",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'temporary_plan'})
    )
    permanent_countermeasures = forms.CharField(
        label="永久對策",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'permanent_countermeasures'})
    )

    happen_again = forms.CharField(
        label="防止再發生(後續追蹤)",
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'happen_again'})
    )
    attachment1 = forms.FileField(
        label="附件1",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment1'})
    )

    attachment2 = forms.FileField(
        label="附件2",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment2'})
    )

    attachment3 = forms.FileField(
        label="附件3",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment3'})
    )

    attachment4 = forms.FileField(
        label="附件4",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment4'})
    )

    attachment5 = forms.FileField(
        label="附件5",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment5'})
    )

    attachment6 = forms.FileField(
        label="附件6",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'id': 'attachment6'})
    )