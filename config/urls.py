from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("ipfinder.urls")),
    path('admin/', admin.site.urls),
    # if download files only from the shared directory
    # path('result/<path:path>/', serve, {'document_root': RESULT_DIRECTORY}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
