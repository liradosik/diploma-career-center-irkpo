from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include(('apps.accounts.public_urls', 'public'), namespace='public')),
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('portfolio/', include(('apps.portfolio.urls', 'portfolio'), namespace='portfolio')),
    path('vacancies/', include(('apps.vacancies.urls', 'vacancies'), namespace='vacancies')),
    path('courses/', include(('apps.courses.urls', 'courses'), namespace='courses')),
    path('resumes/', include(('apps.resumes.urls', 'resumes'), namespace='resumes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
