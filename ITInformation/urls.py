from django.urls import path
from . import views

urlpatterns = [
    path("AssetData/<form_id_Per>/<Reset>",
         views.AssetData.as_view(), name="AssetDataFormReset"),
    
    path("AssetData/<form_id_Per>/",
         views.AssetData.as_view(), name="AssetDataForm"),
    
    path("AssetData/<form_id_Per>/<finish>/",
         views.AssetData.as_view(), name="AssetDataFormFinish"),
    
    path("AssetData", views.AssetData.as_view(),
         name="AssetDataFormWithoutArg"),
]
