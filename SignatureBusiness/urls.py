from django.urls import path
from . import views

urlpatterns = [
    path("DrawingDependencyBook/<form_id_Per>/<Reset>",
         views.DrawingDependencyBook.as_view(), name="DrawingDependencyBookFormReset"),
    path("DrawingDependencyBook/<form_id_Per>/",
         views.DrawingDependencyBook.as_view(), name="DrawingDependencyBookForm"),
    path("DrawingDependencyBook/<form_id_Per>/<OnlyChangeData>/",
         views.DrawingDependencyBook.as_view(), name="DrawingDependencyBookFormOnlyChangeData"),
    path("DrawingDependencyBook/<form_id_Per>/<finish>/",
         views.DrawingDependencyBook.as_view(), name="DrawingDependencyBookFormFinish"),
    path("DrawingDependencyBook", views.DrawingDependencyBook.as_view(),
         name="DrawingDependencyBookFormWithoutArg"),



    path("CustomerComplaintRecord/<form_id_Per>/<Reset>",
         views.CustomerComplaintRecord.as_view(), name="CustomerComplaintRecordFormReset"),
    path("CustomerComplaintRecord/<form_id_Per>/",
         views.CustomerComplaintRecord.as_view(), name="CustomerComplaintRecordForm"),
     path("CustomerComplaintRecord/<form_id_Per>/<OnlyChangeData>/",
         views.CustomerComplaintRecord.as_view(), name="CustomerComplaintRecordFormOnlyChangeData"),
    path("CustomerComplaintRecord/<form_id_Per>/<finish>/",
         views.CustomerComplaintRecord.as_view(), name="CustomerComplaintRecordFormFinish"),
    path("CustomerComplaintRecord", views.CustomerComplaintRecord.as_view(),
         name="CustomerComplaintRecordFormWithoutArg"),

     path("DrawingDependencyBooksummary", views.DrawingDependencyBooksummary.as_view(),
          name="DrawingDependencyBooksummary"),
          
     path("CustomerComplaintRecordsummary", views.CustomerComplaintRecordsummary.as_view(),
          name="CustomerComplaintRecordsummary")
]
