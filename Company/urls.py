from django.urls import path
from . import views, views_action,views_upload_file
from django.contrib.auth import views as authentication_views
from .Richtextviews import EditFormRichtextView, ShowRichTextView

urlpatterns = [
    path('login', views.post_login, name='login'),  # name 是用來渲染模板使用,目前都只使用在url
    path('index', views.index, name='index'),
    path('logout', authentication_views.LogoutView.as_view(
        template_name='Company/logout.html'), name='logout'),
    path("form_application", views.form_application, name='form_application'),
    path("add_model", views.AddModelView.as_view(), name='add_model'),
    path("allform", views.Allform.as_view(), name='allform'),
    path("approved", views.ShowFormListView.as_view(), name='approved'),
    path("form_information/<str:form_id>",
         views.form_information, name='form_information'),
    path("form_information_finish/<str:form_id>",
         views.form_information_finish, name='form_information_finish'),
    path('action/<str:form_id>', views_action.action, name='action'),
    path('forbidden', views.forbidden, name='forbidden'),
    path('FormDraft', views.FormDraft.as_view(), name='FormDraft'),
    path('remove_form/<str:form_id>', views.remove_form, name='remove_form'),
    path('already_down', views.Already_down.as_view(), name='already_down'),
    path('changeURLSaveORSubmit', views.ChangeURLSaveORSubmit.as_view(),
         name='changeURLSaveORSubmit'),
    path('SaveFrom/<form_id_Per>/', views.SaveFrom.as_view(), name='SaveFrom'),
    path('SaveFrom', views.SaveFrom.as_view(), name='SaveFromWithoutArg'),
    path('OutSideFrom', views.OutSideForm.as_view(), name='OutSideFrom'),
    path('InSideFrom', views.InSideForm.as_view(), name='InSideFrom'),
    path('reviewedForm', views.reviewedForm.as_view(), name='reviewedForm'),
    path('SummaryForm', views.SummaryForm.as_view(), name='SummaryForm'),
    path('IllustrateForm', views.Illustrate.as_view(), name='IllustrateForm'),
    path('change_passward', views.change_passward.as_view(), name='change_passward'),
    path("Richtext/<str:form_id>", EditFormRichtextView.as_view(), name="Richtext"),
    path("ShowRichText/<str:form_id>",ShowRichTextView.as_view(), name="ShowRichText"),
    path("upload/",views_upload_file.upload_view, name="upload")
]
