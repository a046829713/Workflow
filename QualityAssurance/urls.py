from django.urls import path
from . import views

urlpatterns = [
    path("QualityAbnormalityReport/<form_id_Per>/<Reset>",
         views.QualityAbnormalityReport.as_view(), name="QualityAbnormalityReportFormReset"),
    path("QualityAbnormalityReport/<form_id_Per>/",
         views.QualityAbnormalityReport.as_view(), name="QualityAbnormalityReportForm"),
    path("QualityAbnormalityReport/<form_id_Per>/<OnlyChangeData>/",
         views.QualityAbnormalityReport.as_view(), name="QualityAbnormalityReportFormOnlyChangeData"),
    path("QualityAbnormalityReport/<form_id_Per>/<finish>/",
         views.QualityAbnormalityReport.as_view(), name="QualityAbnormalityReportFormFinish"),
    path("QualityAbnormalityReport", views.QualityAbnormalityReport.as_view(),
         name="QualityAbnormalityReportFormWithoutArg"),

     path("QualityAbnormalityReportFormsummary", views.QualityAbnormalityReportFormsummary.as_view(),
         name="QualityAbnormalityReportFormsummary"),
     
     
     
     
     
     path("Heavyworkorder/<form_id_Per>/<Reset>",
         views.Heavyworkorder.as_view(), name="HeavyworkorderFormReset"),
     path("Heavyworkorder/<form_id_Per>/",
          views.Heavyworkorder.as_view(), name="HeavyworkorderForm"),
     path("Heavyworkorder/<form_id_Per>/<OnlyChangeData>/",
          views.Heavyworkorder.as_view(), name="HeavyworkorderFormOnlyChangeData"),
     path("Heavyworkorder/<form_id_Per>/<finish>/",
          views.Heavyworkorder.as_view(), name="HeavyworkorderFormFinish"),
     path("Heavyworkorder", views.Heavyworkorder.as_view(),
          name="HeavyworkorderFormWithoutArg"),

     path("HeavyworkorderFormsummary", views.HeavyworkorderFormsummary.as_view(),
          name="HeavyworkorderFormsummary"),
     
     path("HeayworkorderPrint/<form_id>", views.HeayworkorderPrint.as_view(),
          name="HeayworkorderPrint"),
     
     path("pricemodal", views.pricemodal.as_view(),
          name="pricemodal"),
     
     path("mknumberModal", views.mknumberModal.as_view(),
          name="mknumberModal"),
     
     path("delAbnormalMK", views.delAbnormalMK.as_view(),
          name="delAbnormalMK"),        

     path('get_prod_choices_ajax', views.get_prod_choices_ajax, name='get_prod_choices_ajax'),
     path('get_io_number', views.get_io_number, name='get_io_number'),
     
     # 讓IO 拿取得更快
]
