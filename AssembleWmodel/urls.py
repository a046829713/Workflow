from django.urls import path
from . import views

urlpatterns = [
    path('AssembleWmodel', views.AssembleWmodel.as_view(), name='AssembleWmodel'),  # name 是用來渲染模板使用,目前都只使用在url
]