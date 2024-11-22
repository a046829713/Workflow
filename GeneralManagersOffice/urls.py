from django.urls import path
from . import views

urlpatterns = [
    path("CorrectiveeActionReport/<form_id_Per>/<Reset>",
         views.CorrectiveeActionReport.as_view(), name="CorrectiveeActionReportFormReset"),
    
    path("CorrectiveeActionReport/<form_id_Per>/",
         views.CorrectiveeActionReport.as_view(), name="CorrectiveeActionReportForm"),
    
    path("CorrectiveeActionReport/<form_id_Per>/<OnlyChangeData>/",
         views.CorrectiveeActionReport.as_view(), name="CorrectiveeActionReportFormOnlyChangeData"),
    
    path("CorrectiveeActionReport/<form_id_Per>/<finish>/",
         views.CorrectiveeActionReport.as_view(), name="CorrectiveeActionReportFormFinish"),
    
    path("CorrectiveeActionReport", views.CorrectiveeActionReport.as_view(),
         name="CorrectiveeActionReportFormWithoutArg"),

]
