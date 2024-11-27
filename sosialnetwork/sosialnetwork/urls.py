
from django.contrib import admin
from django.urls import path, include

# from django.conf import settings
from sosialnetwork import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('social/', include('social.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)