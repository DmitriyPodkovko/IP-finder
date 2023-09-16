from django.urls import path
from . import views

urlpatterns = [
    path('', views.FileFieldFormView.as_view(), name='index'),
    path('result/', views.FileResultView.as_view(), name='result'),
    path('delete_file/', views.delete_file, name='delete_file'),
    # path('loaded/', views.FileLoadedView.as_view(), name='loaded'),
]
