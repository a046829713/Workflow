from django.urls import path
from . import views
from .BusinessCardRequest_views import BusinessCardRequestView
urlpatterns = [
     path("HR_index", views.ApprovalFrom, name="HR_index"),
     path("RecruitmentInterviewEvaluation/<form_id_Per>/<Reset>", views.RecruitmentInterviewEvaluation.as_view(), name="RecruitmentInterviewEvaluationFormReset"),
     path("RecruitmentInterviewEvaluation/<form_id_Per>/", views.RecruitmentInterviewEvaluation.as_view(), name="RecruitmentInterviewEvaluationForm"),
     path("RecruitmentInterviewEvaluation/<form_id_Per>/<finish>/", views.RecruitmentInterviewEvaluation.as_view(), name="RecruitmentInterviewEvaluationFormFinish"),
     path("RecruitmentInterviewEvaluation", views.RecruitmentInterviewEvaluation.as_view(), name="RecruitmentInterviewEvaluationFormWithoutArg"),

     path("jobDescription/<form_id_Per>/<Reset>", views.jobDescription.as_view(), name="jobDescriptionReset"),
     path("jobDescription/<form_id_Per>/", views.jobDescription.as_view(), name="jobDescriptionForm"),
     path("jobDescription/<form_id_Per>/<OnlyChangeData>/",
          views.jobDescription.as_view(), name="jobDescriptionFormOnlyChangeData"),
     path("jobDescription/<form_id_Per>/<finish>/", views.jobDescription.as_view(), name="jobDescriptionFormFinish"),
     path("jobDescription", views.jobDescription.as_view(), name="jobDescriptionFormWithoutArg"),


     path("PersonnelAdditionApplication/<form_id_Per>/<Reset>", views.PersonnelAdditionApplication.as_view(), name="PersonnelAdditionApplicationFormReset"),
     path("PersonnelAdditionApplication/<form_id_Per>/", views.PersonnelAdditionApplication.as_view(), name="PersonnelAdditionApplicationForm"),
     path("PersonnelAdditionApplication/<form_id_Per>/<OnlyChangeData>/",
          views.PersonnelAdditionApplication.as_view(), name="PersonnelAdditionApplicationFormOnlyChangeData"),
     path("PersonnelAdditionApplication/<form_id_Per>/<finish>/", views.PersonnelAdditionApplication.as_view(), name="PersonnelAdditionApplicationFormFinish"),
     path("PersonnelAdditionApplication/", views.PersonnelAdditionApplication.as_view(), name="PersonnelAdditionApplicationFormWithoutArg"),

     path("AccessControlPermission/<form_id_Per>/<Reset>", views.AccessControlPermission.as_view(), name="AccessControlPermissionFormReset"),
     path("AccessControlPermission/<form_id_Per>/", views.AccessControlPermission.as_view(), name="AccessControlPermissionForm"),
     path("AccessControlPermission/<form_id_Per>/<finish>/", views.AccessControlPermission.as_view(), name="AccessControlPermissionFormFinish"),
     path("AccessControlPermission/", views.AccessControlPermission.as_view(), name="AccessControlPermissionFormWithoutArg"),

     path("BusinessCardRequest/<form_id_Per>/<Reset>", BusinessCardRequestView.as_view(), name="BusinessCardRequestFormReset"),
     path("BusinessCardRequest/<form_id_Per>/", BusinessCardRequestView.as_view(), name="BusinessCardRequestForm"),
     path("BusinessCardRequest/<form_id_Per>/<finish>/", BusinessCardRequestView.as_view(), name="BusinessCardRequestFormFinish"),
     path("BusinessCardRequest/", BusinessCardRequestView.as_view(), name="BusinessCardRequestFormWithoutArg"),

     path('get_level_ajax', views.get_level_ajax, name='get_level_ajax'),
     path('get_skill_level_ajax', views.get_skill_level_ajax, name='get_skill_level_ajax'),    
     path('download_pdf/<str:pdf_filename>/', views.download_pdf, name='download_pdf'),

     path("jobDescriptionFormsummary", views.jobDescriptionFormsummary.as_view(),
          name="jobDescriptionFormsummary"),

     path("PersonnelAdditionApplicationFormsummary", views.PersonnelAdditionApplicationFormsummary.as_view(),
          name="PersonnelAdditionApplicationFormsummary")
]
