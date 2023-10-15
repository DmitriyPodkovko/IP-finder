from django.urls import path, include
from . import views
from ipfinder.api.file_ import async_api


urlpatterns = [
    path('', views.FileFieldFormView.as_view(), name='index'),
    path('result/', views.FileResultView.as_view(), name='result'),
    path('cancel-task/', views.CancelTaskView.as_view(), name='cancel_task'),
    path('delete_file/', views.delete_file, name='delete_file'),
    path("api/", async_api.urls),
    # path('loaded/', views.FileLoadedView.as_view(), name='loaded'),
]
