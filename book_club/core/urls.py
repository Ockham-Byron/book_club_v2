"""
URL configuration for book_club project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('books/', include('books.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('groups/', include('groups.urls')),
    path('pages/', include('pages.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#handling 404 errors
handler404 = 'pages.views.page_not_found_view'
