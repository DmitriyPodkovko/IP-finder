from django.urls import path
from . import views

urlpatterns = [
    path('', views.FileFieldFormView.as_view(), name='index'),
    path('result/', views.FileResultView.as_view(), name='result'),
    path('cancel-task/', views.CancelTaskView.as_view(), name='cancel_task'),
    path('delete_file/', views.delete_file, name='delete_file'),
    path('edit_settings/', views.edit_settings, name='edit_settings'),
    path('check_processing_status/', views.check_processing_status, name='check_processing_status'),
    # path('loaded/', views.FileLoadedView.as_view(), name='loaded'),
]
