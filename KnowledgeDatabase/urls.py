from django.urls import path
from . import views
from .views import EditArticleView, DeleteArticleView, ShowArticleView, AddArticleView

urlpatterns = [
    path('article-list', views.ArticleListView.as_view(),
         name='article-list'),  
    path('article-add', views.AddArticleView.as_view(),
         name='article-add'),  
    # 用來編輯文章
    path('article-edit/<int:pk>/', EditArticleView.as_view(), name='article-edit'),
    path('article-delete/<int:pk>/', DeleteArticleView.as_view(), name='article-delete'),
     path('show-article/<int:pk>/', ShowArticleView.as_view(), name='show-article')



    #     path("AddInformation/<int:pk>/",
    #          ArticleDetailView.as_view(), name="article-detail"),
]
