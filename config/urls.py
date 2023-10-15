from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


urlpatterns = [
    path("", include("ipfinder.urls")),
    path('result/<path:path>/', serve, {'document_root': settings.RESULT_DIRECTORY}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
