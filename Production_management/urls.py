from django.urls import path
from . import views

urlpatterns = [
    path('Dailyvalue', views.Dailyvalue.as_view(), name='Dailyvalue'),  # name 是用來渲染模板使用,目前都只使用在url
    path('download_csv_two', views.download_csv_two, name='download_csv_two'),
    path('download_csv/<str:table_name>/', views.download_csv, name='download_csv'),
    path('Slow_moving', views.Slow_moving_View.as_view(), name='Slow_moving'),
    path('line_chart', views.Line_Chart_View.as_view(), name='line_chart'),
    path('value_stream_map', views.ValueStreamMapView.as_view(), name='value_stream_map'),
    path('treeApi', views.TreeAPIView.as_view(), name='treeApi'),
    path('treedata/checktime', views.TreeAPIView.as_view(), name='treeApiCheckTime'),
    path('treedata/getopenmaterials', views.TreeAPIView.as_view(), name='getopenmaterials'),
    

]