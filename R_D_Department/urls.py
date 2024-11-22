from django.urls import path
from . import views

urlpatterns = [
    path("MeetingMinutes/<form_id_Per>/<Reset>",
         views.MeetingMinutes.as_view(), name="MeetingMinutesFormReset"),
    path("MeetingMinutes/<form_id_Per>/",
         views.MeetingMinutes.as_view(), name="MeetingMinutesForm"),
    path("MeetingMinutes/<form_id_Per>/<finish>/",
         views.MeetingMinutes.as_view(), name="MeetingMinutesFormFinish"),
    path("MeetingMinutes", views.MeetingMinutes.as_view(),
         name="MeetingMinutesFormWithoutArg"),
    
     path("MeetingMinutesFormsummary", views.MeetingMinutesFormsummary.as_view(),
         name="MeetingMinutesFormsummary"),
     
     
     path("SampleConfirmation/<form_id_Per>/<Reset>",
         views.SampleConfirmation.as_view(), name="SampleConfirmationFormReset"),
    path("SampleConfirmation/<form_id_Per>/",
         views.SampleConfirmation.as_view(), name="SampleConfirmationForm"),
    path("SampleConfirmation/<form_id_Per>/<finish>/",
         views.SampleConfirmation.as_view(), name="SampleConfirmationFormFinish"),
     path("SampleConfirmation", views.SampleConfirmation.as_view(),
         name="SampleConfirmationFormWithoutArg"),
     
     path("SampleConfirmationFormsummary", views.SampleConfirmationFormsummary.as_view(),
         name="SampleConfirmationFormsummary"),


     path("PartApprovalNotification/<form_id_Per>/<Reset>",
         views.PartApprovalNotification.as_view(), name="PartApprovalNotificationFormReset"),
    path("PartApprovalNotification/<form_id_Per>/",
         views.PartApprovalNotification.as_view(), name="PartApprovalNotificationForm"),
    path("PartApprovalNotification/<form_id_Per>/<finish>/",
         views.PartApprovalNotification.as_view(), name="PartApprovalNotificationFormFinish"),
     path("PartApprovalNotification", views.PartApprovalNotification.as_view(),
         name="PartApprovalNotificationFormWithoutArg"),
     

     
     path("ExperimentalTest/<form_id_Per>/<Reset>",
         views.ExperimentalTest.as_view(), name="ExperimentalTestFormReset"),
     path("ExperimentalTest/<form_id_Per>/",
         views.ExperimentalTest.as_view(), name="ExperimentalTestForm"),
     path("ExperimentalTest/<form_id_Per>/<OnlyChangeData>/",
          views.ExperimentalTest.as_view(), name="ExperimentalTestFormOnlyChangeData"),
     path("ExperimentalTest/<form_id_Per>/<finish>/",
         views.ExperimentalTest.as_view(), name="ExperimentalTestFormFinish"),
     path("ExperimentalTest", views.ExperimentalTest.as_view(),
         name="ExperimentalTestFormWithoutArg"),
     
    path("ExperimentalTestsummary", views.ExperimentalTestsummary.as_view(),
         name="ExperimentalTestsummary"),

]
