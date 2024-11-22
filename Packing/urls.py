from django.urls import path
from . import views


urlpatterns = [
    path("packing_index",views.PackingIndex.as_view(), name="packing_index"),
    path("sticker_index",views.StickerListView.as_view(), name="sticker_index"),
    path("update_sticker_view",views.update_sticker_view.as_view(), name="update_sticker_view"),
]
